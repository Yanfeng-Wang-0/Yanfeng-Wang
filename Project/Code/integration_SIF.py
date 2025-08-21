#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
合并每个月的 SIF a/b 文件，取平均，掩膜海洋，仅输出一个 NetCDF 与一张 PNG。
读取:
    ../Data/SIF_Processed/<YEAR>/sif_ann_YYYYMMa.nc
    ../Data/SIF_Processed/<YEAR>/sif_ann_YYYYMMb.nc
陆地掩膜:
    ../Data/IMERG_land_mask_1deg.nc  (变量名: "land_mask", 1=陆地, 0=海洋)
输出:
    NetCDF -> ../Data/SIF_final/<YEAR>/sif_ann_YYYYMM_ab_land.nc  (变量: "sif_ann")
    图像   -> ../Results/SIF/<YEAR>/SIF_YYYY_MM_ab.png
"""
import os
import xarray as xr
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import numpy as np

# ------------------------- 路径设置（可按需修改） -------------------------
input_base_dir = "../Data/SIF_final"
output_data_dir = "../Results/SIF_monthly"
output_fig_dir = "../Results/SIF_monthly"
land_mask_path = "../Data/IMERG_land_mask_1deg.nc"  # 变量名优先为 "land_mask"

# 确保输出目录存在
os.makedirs(output_data_dir, exist_ok=True)
os.makedirs(output_fig_dir, exist_ok=True)

# ------------------------- 起止时间 -------------------------
start_year, start_month = 2014, 9
end_year, end_month     = 2020, 7

# ------------------------- 读取陆地掩膜 -------------------------
if not os.path.exists(land_mask_path):
    raise FileNotFoundError(f"未找到陆地掩膜: {land_mask_path}")
land_mask_ds = xr.open_dataset(land_mask_path)

# 兼容一些常见变量名
for cand in ["land_mask", "mask", "landmask", "land"]:
    if cand in land_mask_ds:
        land_mask = land_mask_ds[cand]
        break
else:
    raise KeyError("陆地掩膜文件中未找到变量。已尝试: 'land_mask', 'mask', 'landmask', 'land'。")

def month_iter():
    """按月遍历给定时间范围"""
    y, m = start_year, start_month
    while (y < end_year) or (y == end_year and m <= end_month):
        yield y, m
        m += 1
        if m > 12:
            y += 1
            m = 1

def merge_ab_for_month(year: int, month: int):
    """对某年某月合并 a/b，掩膜海洋并输出"""
    month_str = f"{month:02d}"
    year_str  = f"{year}"
    year_dir  = os.path.join(input_base_dir, year_str)

    fa = os.path.join(year_dir, f"sif_ann_{year_str}{month_str}a_land.nc")
    fb = os.path.join(year_dir, f"sif_ann_{year_str}{month_str}b_land.nc")

    if not (os.path.exists(fa) and os.path.exists(fb)):
        print(f"❌ 缺少 a/b: {year}-{month_str}: {fa} 或 {fb}")
        return

    # 读取并做单位缩放（与原脚本保持一致 *10）
    ds_a = xr.open_dataset(fa)
    ds_b = xr.open_dataset(fb)

    if "sif_ann" not in ds_a or "sif_ann" not in ds_b:
        print(f"❌ 未找到变量 'sif_ann' 于 {fa} 或 {fb}")
        return

    sif_a = ds_a["sif_ann"]
    sif_b = ds_b["sif_ann"] 

    # 合并 (A+B)/2
    sif_ab = (sif_a + sif_b) / 2.0

    # 将掩膜插值到 SIF 网格（最近邻）
    land_mask_interp = land_mask.interp_like(sif_ab, method="nearest")

    # 仅保留陆地 (==1)
    sif_land = sif_ab.where(land_mask_interp == 1)

    # ------------------------- 保存 NetCDF -------------------------
    out_year_dir = os.path.join(output_data_dir, year_str)
    os.makedirs(out_year_dir, exist_ok=True)
    out_nc = os.path.join(out_year_dir, f"sif_ann_{year_str}{month_str}_ab_land.nc")

    sif_land_ds = sif_land.to_dataset(name="sif_ann")
    # 元数据
    sif_land_ds["sif_ann"].attrs.update({
        "long_name": "SIF (a/b 合并后, 仅陆地)",
        "note": "sif_ann_ab = (sif_ann_a + sif_ann_b) / 2; 相对原文件单位放大10倍",
    })
    sif_land_ds.attrs.update({
        "source_a": os.path.basename(fa),
        "source_b": os.path.basename(fb),
        "land_mask": os.path.basename(land_mask_path),
    })

    sif_land_ds.to_netcdf(out_nc)
    print(f"✅ 保存 NetCDF: {out_nc}")

    # ------------------------- 绘图并保存 PNG -------------------------
    out_fig_dir = os.path.join(output_fig_dir, year_str)
    os.makedirs(out_fig_dir, exist_ok=True)
    out_png = os.path.join(out_fig_dir, f"SIF_{year_str}_{month_str}_ab.png")

    fig = plt.figure(figsize=(10, 5))
    ax = plt.axes(projection=ccrs.PlateCarree())
    sif_land.plot(
        ax=ax, transform=ccrs.PlateCarree(), cmap="YlOrRd",
        cbar_kwargs={"label": "SIF 740 nm"}, vmin=0
    )
    ax.coastlines()
    ax.set_title(f"SIF (Land Only, A+B avg) - {year}-{month_str}")
    plt.tight_layout()
    plt.savefig(out_png, dpi=150)
    plt.close(fig)
    print(f"✅ 保存 图像: {out_png}")

def main():
    for y, m in month_iter():
        merge_ab_for_month(y, m)

if __name__ == "__main__":
    main()
