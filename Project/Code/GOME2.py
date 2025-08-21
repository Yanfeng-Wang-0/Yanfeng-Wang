import os
import xarray as xr
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import numpy as np

# ==== 设置年份 ====
year = 2014

# ==== 输入和输出路径 ====
input_dir = f"../Data/GOME2/processed/{year}"
output_data_dir = f"../Data/GOME2/final/{year}"
output_fig_dir = f"../Results/GOME2/SIF/{year}"
os.makedirs(output_data_dir, exist_ok=True)
os.makedirs(output_fig_dir, exist_ok=True)

# ==== 读取陆地掩膜 ====
land_mask_ds = xr.open_dataset("../Data/IMERG_land_mask_1deg.nc")
land_mask = land_mask_ds["land_mask"]

# ==== 遍历每月文件 ====
for month in range(1, 13):
    file_name = f"GOME2B_SIF{year}_{month:02d}_1x1.nc"
    input_path = os.path.join(input_dir, file_name)

    if not os.path.exists(input_path):
        print(f"❌ Missing: {input_path}")
        continue

    # === 打开数据并读取 SIF ===
    ds = xr.open_dataset(input_path)
    sif = ds["SIF"] * 1000
    land_mask_interp = land_mask.interp_like(sif, method="nearest")
    sif_land = sif.where(land_mask_interp == 1)

    # === 保存处理后的 nc 文件 ===
    output_nc = os.path.join(output_data_dir, f"GOME2B_SIF_{year}_{month:02d}_land.nc")
    sif_land.to_netcdf(output_nc)

    # === 生成图像 ===
    fig = plt.figure(figsize=(12, 6))
    ax = plt.axes(projection=ccrs.PlateCarree())
    sif_land.plot(ax=ax, transform=ccrs.PlateCarree(), cmap="YlOrRd",
                  cbar_kwargs={'label': 'SIF'}, vmin=0)
    ax.coastlines()
    ax.set_title(f"GOME2B SIF (Land Only) - {year}-{month:02d}")
    plt.tight_layout()

    # === 保存图像 ===
    output_png = os.path.join(output_fig_dir, f"GOME2B_SIF_{year}_{month:02d}.png")
    plt.savefig(output_png, dpi=150)
    plt.close()

    print(f"✅ Saved: {output_nc}")
    print(f"✅ Saved: {output_png}")
