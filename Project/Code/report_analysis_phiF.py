#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Compare OCO-2 vs GOME-2 φF for a single month and plot hexbin scatter.
- 强制读取变量: phiF_emitted (unitless)
- 经度统一到 0–360 并排序
- 网格不一致时: 用最近邻把 GOME-2 对齐到 OCO-2
- 物理合理值域: 0–0.05
- 输出: hexbin 图 + 诊断打印
"""

from pathlib import Path
import numpy as np
import xarray as xr
import matplotlib.pyplot as plt

# =================== 配置 ===================
YEAR  = 2018
MONTH = 7

# OCO-2 φF 月度文件
OCO2_PATHS = [
    "../Results/fesc_OCO2/fesc_phiF_{YYYY}_{MM:02d}_vza5.nc",
]

# GOME-2 φF 月度文件（优先 lon0360；若没有就回退普通网格）
GOME2_PATHS = [
    "../Results/fesc_GOME2/fesc_phiF_{YYYY}_{MM:02d}_vzaAll.nc",
]

# 输出目录
OUT_DIR = Path("../Results/Plot/analysis")
OUT_DIR.mkdir(parents=True, exist_ok=True)

# 画图参数
GRIDSIZE = 60           # hexbin 网格数
X_LIM = (0.0, 0.04)     # φF 合理范围
Y_LIM = (0.0, 0.04)
CMAP = "viridis"
# ============================================


# ------------- 工具函数 -------------
def find_existing(patterns, YYYY, MM) -> Path:
    for p in patterns:
        fp = Path(p.format(YYYY=YYYY, MM=MM))
        if fp.exists():
            return fp
    raise FileNotFoundError("未找到文件：\n" + "\n".join([p.format(YYYY=YYYY, MM=MM) for p in patterns]))

def std_latlon(da: xr.DataArray) -> xr.DataArray:
    lat = next((n for n in ("lat","latitude","y") if n in da.dims or n in da.coords), None)
    lon = next((n for n in ("lon","longitude","x") if n in da.dims or n in da.coords), None)
    if lat is None or lon is None:
        raise ValueError(f"无法识别经纬度: dims={da.dims}, coords={list(da.coords)}")
    if lat != "lat": da = da.rename({lat:"lat"})
    if lon != "lon": da = da.rename({lon:"lon"})
    return da

def to_lon0360(da: xr.DataArray) -> xr.DataArray:
    lon_new = (da.lon % 360 + 360) % 360
    return da.assign_coords(lon=lon_new).sortby("lon")

def load_phiF_emitted(path: Path) -> xr.DataArray:
    ds = xr.open_dataset(path)
    if "phiF_emitted" not in ds:
        raise KeyError(f"{path.name} 未包含变量 'phiF_emitted'（请确认文件内容与命名）")
    da = ds["phiF_emitted"].astype("float32")
    da = std_latlon(da)
    da = to_lon0360(da)
    return da

def align_to_ref(ref: xr.DataArray, tgt: xr.DataArray) -> xr.DataArray:
    # 坐标完全一致则直接返回；否则最近邻插值对齐
    try:
        if np.allclose(ref.lat, tgt.lat) and np.allclose(ref.lon, tgt.lon):
            return tgt
    except Exception:
        pass
    return tgt.interp_like(ref, method="nearest")

def vectorize_pair(a: xr.DataArray, b: xr.DataArray):
    x = a.values.ravel()
    y = b.values.ravel()
    m = np.isfinite(x) & np.isfinite(y)
    return x[m], y[m]

def basic_stats(x: np.ndarray, y: np.ndarray):
    if x.size == 0:
        return dict(N=0, r2=np.nan, bias=np.nan, mae=np.nan, rmse=np.nan, slope=np.nan, intercept=np.nan)
    dx = y - x
    bias = float(np.mean(dx))
    mae  = float(np.mean(np.abs(dx)))
    rmse = float(np.sqrt(np.mean(dx**2)))
    # R^2
    r = np.corrcoef(x, y)[0,1] if x.size > 1 else np.nan
    r2 = float(r**2) if np.isfinite(r) else np.nan
    # 线性拟合（诊断用）
    A = np.vstack([x, np.ones_like(x)]).T
    slope, intercept = np.linalg.lstsq(A, y, rcond=None)[0]
    return dict(N=int(x.size), r2=r2, bias=float(bias), mae=float(mae), rmse=float(rmse),
                slope=float(slope), intercept=float(intercept))
# ------------------------------------


def main():
    y, m = YEAR, MONTH

    # —— 定位文件
    oco2_fp  = find_existing(OCO2_PATHS, y, m)
    gome2_fp = find_existing(GOME2_PATHS, y, m)

    print(f"[路径] OCO-2 : {oco2_fp}")
    print(f"[路径] GOME-2: {gome2_fp}")

    # —— 读取 φF（强制 phiF_emitted）
    oco2 = load_phiF_emitted(oco2_fp)
    gome2 = load_phiF_emitted(gome2_fp)

    # —— 网格对齐（把 GOME-2 对齐到 OCO-2）
    gome2_al = align_to_ref(oco2, gome2)

    # —— 值域筛选（0–0.05）并做联合掩膜
    oco2 = oco2.where((oco2>=X_LIM[0]) & (oco2<=X_LIM[1]))
    gome2_al = gome2_al.where((gome2_al>=Y_LIM[0]) & (gome2_al<=Y_LIM[1]))

    # —— 诊断打印
    print(f"[变量] OCO-2: {oco2.name} range≈[{float(np.nanmin(oco2)):.5f}, {float(np.nanmax(oco2)):.5f}]")
    print(f"[变量] GOME-2: {gome2_al.name} range≈[{float(np.nanmin(gome2_al)):.5f}, {float(np.nanmax(gome2_al)):.5f}]")
    print("[检查] arrays identical? ", oco2.identical(gome2_al))

    # —— 拉直为一维向量
    x, yv = vectorize_pair(oco2, gome2_al)

    # —— 统计
    S = basic_stats(x, yv)
    print(f"[统计] N={S['N']}, bias={S['bias']:.5f}, MAE={S['mae']:.5f}, RMSE={S['rmse']:.5f}, "
          f"R²={S['r2']:.3f}, slope={S['slope']:.3f}, intercept={S['intercept']:.5f}")

    # —— 画 hexbin
    fig, ax = plt.subplots(figsize=(6, 6))
    hb = ax.hexbin(x, yv, gridsize=GRIDSIZE, cmap=CMAP, mincnt=1, extent=[*X_LIM, *Y_LIM])
    cb = fig.colorbar(hb, ax=ax, label="Counts")

    # 1:1 参考线
    diag_min = max(X_LIM[0], Y_LIM[0])
    diag_max = min(X_LIM[1], Y_LIM[1])
    ax.plot([diag_min, diag_max], [diag_min, diag_max], "r--", lw=1)

    ax.set_xlim(*X_LIM); ax.set_ylim(*Y_LIM)
    ax.set_xlabel("OCO-2 ϕF")        # 也可写 r"$\varphi F$"
    ax.set_ylabel("GOME-2 ϕF")
    ax.set_title(f"Hexbin Analysis (R²={S['r2']:.3f})")
    out_png = OUT_DIR / f"phiF_hexbin_{y}_{m:02d}.png"
    fig.tight_layout(); fig.savefig(out_png, dpi=300); plt.close(fig)
    print(f"[OK] 图已保存：{out_png.resolve()}")

if __name__ == "__main__":
    main()
