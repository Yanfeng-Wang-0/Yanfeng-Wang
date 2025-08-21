#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os, re, glob
import numpy as np
import xarray as xr
import matplotlib.pyplot as plt

# ============ 配置（按需改这里） ============
IN_DIR  = "/home/yanfeng-wang/Documents/Project/Results/fesc_GOME2"  # 合并后的 nc 目录
OUT_DIR = os.path.join(IN_DIR, "quick_maps")                          # 导出图所在目录
os.makedirs(OUT_DIR, exist_ok=True)

# 要绘制的变量列表（按需增减）
VARS_TO_PLOT = [
    "fesc_merged",   # 合并后的 fesc
    "phiF_emitted",  # 最终 φF（无量纲）
    # "phiF_wmean",
    # "phiF_old_est",
]

# 色标范围
VMIN_VMAX = {
    "fesc_merged":  (0.1, 0.9),
    "phiF_emitted": (0.0, 0.04),
    "phiF_wmean":   (0.0, 0.04),
    "phiF_old_est": (0.0, 0.04),
}

# 色标文字
CBAR_LABEL = {
    "fesc_merged":  "fesc",
    # 用 MathText 显示希腊字母 φ：也可换成 "φF"
    "phiF_emitted": r"$\varphi F$",
    "phiF_wmean":   r"$\varphi F$ (w-mean)",
    "phiF_old_est": r"$\varphi F_{\mathrm{old}}$ (est.)",
}
# ==========================================

# 匹配合并后的文件：fesc_phiF_YYYY_MM_vzaAll.nc
pattern = os.path.join(IN_DIR, "fesc_phiF_*_*_vzaAll.nc")
files = sorted(glob.glob(pattern))
if not files:
    raise SystemExit(f"未在 {IN_DIR} 找到 fesc_phiF_YYYY_MM_vzaAll.nc")

# 从文件名提取年月
ym_re = re.compile(r"fesc_phiF_(\d{4})_(\d{2})_vzaAll", re.IGNORECASE)

TIME_DIMS = ("time", "Time", "T", "date", "Date", "FileDates")

def collapse_time_to_2d(da: xr.DataArray) -> xr.DataArray:
    """把任何 time-like 维降成 2D（多层→均值，单层→去掉），并统一成(lat, lon)"""
    for d in TIME_DIMS:
        if d in da.dims:
            da = da.mean(d, skipna=True) if da.sizes[d] > 1 else da.isel({d: 0})
    lat = next(n for n in ("lat", "latitude", "y") if n in da.dims)
    lon = next(n for n in ("lon", "longitude", "x") if n in da.dims)
    return da.transpose(lat, lon)

def plot_one(da: xr.DataArray, title: str, save_path: str, vmin=None, vmax=None, cbar_label=""):
    # xarray -> numpy，确保经纬度单调递增
    lat = np.asarray(da.coords[da.dims[0]].values)  # 第一维是 lat
    lon = np.asarray(da.coords[da.dims[1]].values)  # 第二维是 lon
    data = np.asarray(da.values)

    if lat[0] > lat[-1]:
        lat = lat[::-1]; data = data[::-1, :]
    if lon[0] > lon[-1]:
        lon = lon[::-1]; data = data[:, ::-1]

    extent = [float(lon.min()), float(lon.max()), float(lat.min()), float(lat.max())]
    data = np.ma.masked_invalid(data)

    plt.figure(figsize=(10, 5))
    ax = plt.gca()
    ax.set_facecolor("white")  # NaN 显示为白底
    im = plt.imshow(
        data, origin="lower", extent=extent, aspect="auto",
        vmin=vmin, vmax=vmax
    )
    cb = plt.colorbar(im); cb.set_label(cbar_label)
    plt.title(title); plt.xlabel("Longitude"); plt.ylabel("Latitude")
    plt.tight_layout()
    plt.savefig(save_path, dpi=300)
    plt.close()

for fp in files:
    m = ym_re.search(os.path.basename(fp))
    if not m:
        print(f"[跳过] 文件名不匹配：{os.path.basename(fp)}")
        continue
    yyyy, mm = m.group(1), m.group(2)
    ym = f"{yyyy}-{mm}"

    try:
        ds = xr.open_dataset(fp)
        for var in VARS_TO_PLOT:
            if var not in ds.variables:
                print(f"[{ym}] 缺少变量 {var}，跳过该图。")
                continue

            da = collapse_time_to_2d(ds[var])
            vmin, vmax = VMIN_VMAX.get(var, (None, None))
            label = CBAR_LABEL.get(var, var)

            # —— 标题逻辑：phiF 用“GOME-2 φF (YYYY-MM)”，其他保持默认
            if var == "phiF_emitted":
                title = rf"GOME-2 $\varphi F$ ({ym})"  # 也可换成 "GOME-2 φF"
            else:
                title = f"{var} {ym}"

            png = os.path.join(OUT_DIR, f"map_{var}_{yyyy}_{mm}.png")
            plot_one(da, title, png, vmin=vmin, vmax=vmax, cbar_label=label)
            print(f"[完成] {png}")

        ds.close()
    except Exception as e:
        print(f"[出错] {fp} -> {e}")
