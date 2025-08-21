#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
合并已生成的 PhiF a/b 文件 -> 平均值
输出到 ../Results/phiF_monthly
绘图固定色标范围 0–0.040
"""

import os
import xarray as xr
import numpy as np
import matplotlib.pyplot as plt

# 输入和输出目录
in_root = "../Results/PhiF"          # 存放 a/b 文件的目录
out_root = "../Results/phiF_monthly" # 新的合并结果目录
os.makedirs(out_root, exist_ok=True)

# 时间范围
start_year, start_month = 2014, 9
end_year, end_month     = 2020, 7

def month_iter():
    y, m = start_year, start_month
    while (y < end_year) or (y == end_year and m <= end_month):
        yield y, m
        m += 1
        if m > 12:
            y += 1
            m = 1

def load_phiF(path):
    if not os.path.exists(path):
        return None
    ds = xr.open_dataset(path)
    # 变量名可能不同，这里兼容
    if "phiF" in ds:
        return ds["phiF"]
    else:
        for v in ds.data_vars:
            if v.lower().startswith("phif"):
                return ds[v]
    raise KeyError(f"No phiF variable found in {path}")

def merge_month(y, m):
    month_str = f"{m:02d}"
    year_str  = str(y)
    fa = os.path.join(in_root, year_str, f"PhiF_{y}_{month_str}_a.nc")
    fb = os.path.join(in_root, year_str, f"PhiF_{y}_{month_str}_b.nc")

    a = load_phiF(fa)
    b = load_phiF(fb)

    if a is None and b is None:
        print(f"❌ {y}-{month_str}: a/b 文件都不存在，跳过。")
        return

    if a is not None and b is not None:
        a, b = xr.align(a, b, join="inner")
        ab = (a + b) / 2.0
    else:
        ab = a if a is not None else b
        print(f"⚠️ {y}-{month_str}: 只有一个文件，直接使用。")

    ab = ab.rename("phiF")
    ab.attrs.update({
        "long_name": "Fluorescence quantum yield (a/b merged)",
        "units": "dimensionless",
        "note": "mean(a,b) if both exist, else single available"
    })

    # 保存到新目录
    out_nc = os.path.join(out_root, f"PhiF_{y}_{month_str}_ab.nc")
    ab.to_dataset(name="phiF").to_netcdf(out_nc)
    print(f"✅ 保存 NetCDF: {out_nc}")

    # 绘图固定 0–0.040
    plt.figure(figsize=(10, 6))
    ax = ab.plot(
        cmap="viridis",
        vmin=0.0,
        vmax=0.040,
        cbar_kwargs={"label": "φF"}
    )
    ax.axes.set_aspect("equal")
    plt.title(f"φF (A+B avg) {y}-{month_str}")
    plt.tight_layout()
    out_png = os.path.join(out_root, f"PhiF_{y}_{month_str}_ab.png")
    plt.savefig(out_png, dpi=300)
    plt.close()
    print(f"🖼️ 保存 图像: {out_png}")

if __name__ == "__main__":
    for y, m in month_iter():
        merge_month(y, m)
