#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
LAI+固定VZA 估算 fesc，并在“旧 φF”网格/掩膜上重标定得到新 φF。

- LAI 先最近邻对齐到旧 φF 网格再计算 fesc（不再 broadcast_like）
- 旧 φF 变量名智能识别（优先 phiF_ab/phiF，排除 *const），会打印命中名
- 只在旧 φF 有效区域内计算；对 fesc 的小 NaN 洞做最近邻补全
- φF_new = φF_old * (fesc0 / fesc_filled)，并夹到 [0, 0.04]

输出：每月 1 个 NetCDF，变量 {fesc, phiF_emitted}
"""

import os, re, glob
import numpy as np
import xarray as xr
from pathlib import Path

# ========== 配置（按需修改） ==========
BASE = Path(__file__).resolve().parents[1]      # .../Project
PHIF_DIR = BASE / "Results" / "phiF_monthly"    # 旧 φF 文件夹（目标网格+掩膜）
LAI_DIR  = BASE / "Data"    / "LAI_processed"   # LAI 月度文件夹（1x1_masked）
OUT_DIR  = BASE / "Results" / "fesc"

F_ESC0   = 0.47                                  # 旧流程里的常数 fesc
VZA_LIST = [5.0]                                 # OCO-2≈5°；GOME-2 可用 [20, 30, 40]
CLIP_FESC = (0.1, 0.9)
CLIP_PHIF = (0.0, 0.04)

# 可能的时间维名字（都会被统一降到 2D）
TIME_DIMS = ("time", "Time", "T", "date", "Date", "FileDates")

# ========== 小工具 ==========
def parse_ym_from_name(path: str):
    m = re.search(r'(\d{4})[_-](\d{2})', os.path.basename(path))
    return (int(m.group(1)), int(m.group(2))) if m else None

def get_lat_lon_names(da_or_ds):
    names_lat = ("lat", "latitude", "y")
    names_lon = ("lon", "longitude", "x")
    lat_name = next((n for n in names_lat if n in da_or_ds.coords), None)
    lon_name = next((n for n in names_lon if n in da_or_ds.coords), None)
    if lat_name is None or lon_name is None:
        raise KeyError("经纬度坐标未找到，请检查坐标名。")
    return lat_name, lon_name

def collapse_time(da: xr.DataArray) -> xr.DataArray:
    """把任何时间维降到 2D：多层→均值；单层→去掉该维。"""
    dims_present = [d for d in TIME_DIMS if d in da.dims]
    for d in dims_present:
        if da.sizes[d] > 1:
            da = da.mean(d, skipna=True)
        else:
            da = da.isel({d: 0})
    return da

def ensure_2d_latlon(da: xr.DataArray) -> xr.DataArray:
    """确保只有 (lat, lon) 两维，并把维度顺序统一成 (lat, lon)。"""
    da = collapse_time(da)
    lat_name, lon_name = get_lat_lon_names(da)
    return da.transpose(lat_name, lon_name)

def pick_phi_old(ds: xr.Dataset) -> xr.DataArray:
    """优先选 phiF_ab/phiF，排除带 const 的变量；打印最终命中名。"""
    order = ["phiF_ab", "phif_ab", "phiF", "phif", "phiF_old"]
    for k in order:
        if k in ds.data_vars:
            print(f"[phiF] using variable: {k}")
            return ds[k]
    # 模糊匹配：含 'phi' 且不含 'const'
    for k in ds.data_vars:
        kl = k.lower()
        if ("phi" in kl) and ("const" not in kl):
            print(f"[phiF] using variable (fuzzy): {k}")
            return ds[k]
    raise RuntimeError(f"未找到旧 φF 变量；可用变量：{list(ds.data_vars)}")

def pick_lai(ds: xr.Dataset) -> xr.DataArray:
    for k in ["LAI", "lai"]:
        if k in ds.data_vars:
            return ds[k]
    # 回退：挑一个二维/三维变量
    for k, v in ds.data_vars.items():
        if v.ndim >= 2:
            return v
    raise RuntimeError("未找到 LAI 变量。")

def fesc_from_LAI_on_phi_grid(LAI_src: xr.DataArray, phi_like: xr.DataArray, vza_deg: float, G: float=0.5):
    """LAI 最近邻对齐到 φF 网格后计算 fesc；返回与 φF 同维度/坐标。"""
    lat_phi, lon_phi = get_lat_lon_names(phi_like)
    lat_lai, lon_lai = get_lat_lon_names(LAI_src)
    LAI_src = collapse_time(LAI_src)
    LAI = LAI_src.interp({lat_lai: phi_like[lat_phi], lon_lai: phi_like[lon_phi]}, method="nearest")
    mu = np.cos(np.deg2rad(vza_deg)); mu = max(float(mu), 1e-6)
    k  = G / mu
    x  = k * xr.apply_ufunc(np.clip, LAI, 0.0, 10.0)
    small = x < 1e-6
    fesc = xr.where(small, 1.0 - x/2.0, (1.0 - xr.ufuncs.exp(-x)) / x)
    return fesc

def clamp(da, lo, hi):
    return xr.apply_ufunc(np.clip, da, lo, hi)

# ========== 主流程 ==========
def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    phif_list = sorted(glob.glob(str(PHIF_DIR / "*.nc*")))
    if not phif_list:
        raise SystemExit(f"在 {PHIF_DIR} 未找到 φF nc 文件")

    for f in phif_list:
        ym = parse_ym_from_name(f)
        if ym is None:
            print(f"[跳过] 无法解析年月：{os.path.basename(f)}"); continue
        yy, mm = ym

        # 旧 φF（作为目标网格 + 掩膜）
        ds_phi = xr.open_dataset(f)
        phi_old = ensure_2d_latlon(pick_phi_old(ds_phi)).astype("float32")
        lat_phi, lon_phi = get_lat_lon_names(phi_old)

        # 当月 LAI
        lai_path = LAI_DIR / f"LAI_{yy:04d}_{mm:02d}_1x1_masked.nc"
        if not lai_path.exists():
            cands = sorted(glob.glob(str(LAI_DIR / f"LAI_{yy:04d}_{mm:02d}_1x1_masked*.nc*")))
            if not cands:
                print(f"[缺 LAI] {yy}-{mm:02d} 跳过 {os.path.basename(f)}"); ds_phi.close(); continue
            lai_path = Path(cands[0])
        ds_lai = xr.open_dataset(lai_path)
        LAI_src = pick_lai(ds_lai)

        for vza in VZA_LIST:
            # 1) fesc：在旧 φF 网格上计算
            fesc = fesc_from_LAI_on_phi_grid(LAI_src, phi_old, vza_deg=float(vza), G=0.5)
            fesc = clamp(fesc, *CLIP_FESC).astype("float32")

            # 2) 只在旧 φF 有效区域内计算；fesc 小 NaN 洞最近邻补齐
            mask_phi = np.isfinite(phi_old.values)
            fesc_on_phi = fesc.where(mask_phi)
            # 最近邻补洞（只在 φF 掩膜内；最多扩 1 个像元）
            fesc_on_phi = fesc_on_phi.interpolate_na(dim=lon_phi, method="nearest", limit=1)
            fesc_on_phi = fesc_on_phi.interpolate_na(dim=lat_phi, method="nearest", limit=1)

            # 3) 新 φF（继承旧 φF 掩膜）
            ratio    = (F_ESC0 / (fesc_on_phi + 1e-12))
            phi_new  = (phi_old * ratio).where(mask_phi)
            phi_new  = clamp(phi_new, *CLIP_PHIF).rename("phiF_emitted")

            # 4) 写出
            out = xr.Dataset({
                "fesc": fesc_on_phi.rename("fesc"),
                "phiF_emitted": phi_new,
            })
            out["fesc"].attrs.update(dict(units="1", long_name="escape probability",
                                          VZA_deg=float(vza),
                                          note="(1-exp(-k*LAI))/(k*LAI), k=0.5/cos(VZA)"))
            out["phiF_emitted"].attrs.update(dict(units="1",
                                                  long_name="fluorescence quantum yield (emitted)",
                                                  definition="phiF_new = phiF_old * (fesc0 / fesc)",
                                                  f_esc0=F_ESC0, VZA_deg=float(vza)))
            out_name = f"fesc_phiF_{yy:04d}_{mm:02d}_vza{int(round(vza))}.nc"
            out.to_netcdf(OUT_DIR / out_name)
            print(f"[OK] {yy}-{mm:02d} VZA={vza}° -> {OUT_DIR/out_name}")

        ds_phi.close(); ds_lai.close()

if __name__ == "__main__":
    main()
