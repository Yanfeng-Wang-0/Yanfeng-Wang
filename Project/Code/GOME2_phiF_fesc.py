#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Merge GOME-2 VZA=20/30/40° fesc/phiF 月产品为单一月产品（同网格）。
无需命令行参数，目录与权重都在 CONFIG 段写死即可。

输入文件命名（位于 IN_DIR）：
  fesc_phiF_YYYY_MM_vza20.nc
  fesc_phiF_YYYY_MM_vza30.nc
  fesc_phiF_YYYY_MM_vza40.nc
每个文件需含变量：'fesc' 与 'phiF_emitted'

输出（写到 OUT_DIR）：
  fesc_phiF_YYYY_MM_vzaAll.nc
  变量：
    - fesc_merged   （合并后的 fesc）
    - phiF_emitted  （最终合并 φF，无量纲）
    - phiF_old_est  （诊断：由各角度反推出的旧 φF 中位数）
    - phiF_wmean    （参考：各角度 φF 的加权平均）
"""

import re, glob, numpy as np, xarray as xr
from pathlib import Path

# ============== CONFIG（按需改这里就行） ==============
# 项目根目录
BASE   = Path("/home/yanfeng-wang/Documents/Project")

# 输入目录：放三角度月文件
IN_DIR  = BASE / "Results" / "fesc2"
# 输出目录：不改的话就和输入目录相同
OUT_DIR = BASE / "Results" / "fesc_GOME2"

# 角度与权重
ANGLES  = [20, 30, 40]

# 权重模式：'equal' 等权；'cos' 用 cos(VZA)
WEIGHTS_MODE = "cos"   # 可改为 "equal"

# 旧流程使用的常数 fesc，用于从各角度反推旧 φF
F_ESC0   = 0.47
PHI_CLIP = (0.0, 0.04)
FESC_CLIP= (0.1, 0.9)
# =====================================================

def weights_from_mode():
    if WEIGHTS_MODE.lower() == "cos":
        return [float(np.cos(np.deg2rad(a))) for a in ANGLES]
    return [1.0]*len(ANGLES)

def ensure_2d_latlon(da: xr.DataArray) -> xr.DataArray:
    for d in ("time","Time","T","date","Date","FileDates"):
        if d in da.dims:
            da = da.mean(d, skipna=True) if da.sizes[d] > 1 else da.isel({d:0})
    lat = next(n for n in ("lat","latitude","y") if n in da.dims)
    lon = next(n for n in ("lon","longitude","x") if n in da.dims)
    return da.transpose(lat, lon)

def parse_ym(name: str):
    m = re.search(r'(\d{4})[_-](\d{2})', name)
    return (int(m.group(1)), int(m.group(2))) if m else (None, None)

def wmean(arrs, ws):
    """xarray DataArray 的带权平均，自动跳过 NaN。"""
    wstack = xr.concat([xr.full_like(arrs[0], w) for w in ws], dim="m")
    astack = xr.concat(arrs, dim="m")
    valid  = xr.where(xr.ufuncs.isfinite(astack), 1.0, 0.0)
    num = (astack * wstack * valid).sum("m")
    den = (wstack * valid).sum("m")
    return num / xr.where(den > 0, den, np.nan)

def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    W = weights_from_mode()
    print(f"[CONFIG] IN_DIR={IN_DIR}")
    print(f"[CONFIG] OUT_DIR={OUT_DIR}")
    print(f"[CONFIG] ANGLES={ANGLES}  WEIGHTS={W}  MODE={WEIGHTS_MODE}")

    files = sorted(glob.glob(str(IN_DIR / "fesc_phiF_*_*_vza*.nc*")))
    if not files:
        raise SystemExit(f"No input files found in {IN_DIR}")

    # 按 YYYY_MM 分组
    groups = {}
    for fp in files:
        ym = "_".join(Path(fp).stem.split("_")[2:4])  # fesc_phiF_YYYY_MM_...
        groups.setdefault(ym, []).append(fp)

    for ym, fps in sorted(groups.items()):
        # 收集该月的角度文件（允许缺角度）
        per_angle = {}
        for a in ANGLES:
            hit = glob.glob(str(IN_DIR / f"fesc_phiF_{ym}_vza{a}.nc*"))
            if hit:
                per_angle[a] = hit[0]
        if not per_angle:
            print(f"[skip] {ym}: no angles present")
            continue

        print(f"[{ym}] merging angles:", sorted(per_angle.keys()))

        fesc_list, phif_list, phi_old_est_list, w_used = [], [], [], []
        for a in sorted(per_angle.keys()):
            ds = xr.open_dataset(per_angle[a])
            if "fesc" not in ds or "phiF_emitted" not in ds:
                print(f"  - missing vars in {Path(per_angle[a]).name}; skip")
                ds.close(); continue
            fesc = ensure_2d_latlon(ds["fesc"]).clip(*FESC_CLIP)
            phif = ensure_2d_latlon(ds["phiF_emitted"]).clip(*PHI_CLIP)

            phi_old_i = (phif * fesc / F_ESC0)   # 由该角度反推旧 φF
            fesc_list.append(fesc)
            phif_list.append(phif)
            phi_old_est_list.append(phi_old_i)
            w_used.append(W[ANGLES.index(a)])
            ds.close()

        if not fesc_list:
            print(f"[skip] {ym}: no valid files")
            continue

        # 旧 φF 的稳健估计（多角度中位数）
        phi_old_est = xr.concat(phi_old_est_list, dim="m").median("m", skipna=True).rename("phiF_old_est")

        # 合并 fesc（带权平均）
        fesc_merged = wmean(fesc_list, w_used).clip(*FESC_CLIP).rename("fesc_merged")

        # 合并缩放比（F_ESC0/fesc）的带权平均
        ratio_list = [ (F_ESC0 / f) for f in fesc_list ]
        ratio_merged = wmean(ratio_list, w_used)

        # 最终 φF（与单一 phi_old 自洽）
        phiF_final = (phi_old_est * ratio_merged).clip(*PHI_CLIP).rename("phiF_emitted")

        # 参考：直接对各角度 φF 做带权平均
        phiF_wmean = wmean(phif_list, w_used).clip(*PHI_CLIP).rename("phiF_wmean")

        # 保存
        out = xr.Dataset(dict(
            fesc_merged = fesc_merged,
            phiF_emitted= phiF_final,
            phiF_old_est= phi_old_est,
            phiF_wmean  = phiF_wmean,
        ))
        out.attrs.update(dict(
            note="Merged from multi-VZA products",
            angles=",".join(str(a) for a in sorted(per_angle.keys())),
            weights=",".join(str(w) for w in w_used),
            weights_mode=WEIGHTS_MODE,
            fesc0=F_ESC0
        ))
        out_fp = OUT_DIR / f"fesc_phiF_{ym}_vzaAll.nc"
        out.to_netcdf(out_fp)
        print(f"  -> {out_fp}")

if __name__ == "__main__":
    main()
