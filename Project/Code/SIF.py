import os
import xarray as xr
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import numpy as np

# 输入路径
input_base_dir = "../Data/SIF_Processed"
# 输出路径
output_data_dir = "../Data/SIF_final"
output_fig_dir = "../Results/SIF"
os.makedirs(output_data_dir, exist_ok=True)
os.makedirs(output_fig_dir, exist_ok=True)

# 读取陆地掩膜（假设变量名为 'mask'，1 表示陆地，0 表示海洋）
land_mask_ds = xr.open_dataset("../Data/IMERG_land_mask_1deg.nc")
land_mask = land_mask_ds["land_mask"]

# 起止时间
start_year, start_month = 2014, 9
end_year, end_month = 2020, 7

# 时间循环
year, month = start_year, start_month
while (year < end_year) or (year == end_year and month <= end_month):
    month_str = f"{month:02d}"
    year_str = str(year)
    year_dir = os.path.join(input_base_dir, year_str)

    file_a = f"sif_ann_{year_str}{month_str}a.nc"
    file_b = f"sif_ann_{year_str}{month_str}b.nc"
    path_a = os.path.join(year_dir, file_a)
    path_b = os.path.join(year_dir, file_b)

    if not os.path.exists(path_a) or not os.path.exists(path_b):
        print(f"❌ 缺少文件: {path_a} 或 {path_b}")
        month += 1
        if month > 12:
            month = 1
            year += 1
        continue

    for label, path, suffix in zip(["A", "B"], [path_a, path_b], ["a", "b"]):
        ds = xr.open_dataset(path)
        sif = ds["sif_ann"] * 10
        
        # 插值掩膜
        land_mask_interp = land_mask.interp_like(sif, method="nearest")
        sif_land = sif.where(land_mask_interp == 1)

        # 输出 NetCDF 文件
        data_output_dir = os.path.join(output_data_dir, year_str)
        os.makedirs(data_output_dir, exist_ok=True)
        output_nc = os.path.join(data_output_dir, f"sif_ann_{year_str}{month_str}{suffix}_land.nc")
        sif_land.to_netcdf(output_nc)

        # 输出图像
        fig_output_dir = os.path.join(output_fig_dir, year_str)
        os.makedirs(fig_output_dir, exist_ok=True)
        output_png = os.path.join(fig_output_dir, f"SIF_{year_str}_{month_str}_{suffix}.png")

        fig = plt.figure(figsize=(10, 5))
        ax = plt.axes(projection=ccrs.PlateCarree())
        sif_land.plot(ax=ax, transform=ccrs.PlateCarree(), cmap="YlOrRd",
                      cbar_kwargs={'label': 'SIF 740nm'}, vmin=0)
        ax.coastlines()
        ax.set_title(f"SIF (Land Only) - {year}-{month_str} {label}")
        plt.tight_layout()
        plt.savefig(output_png, dpi=150)
        plt.close()

        print(f"✅ 已保存: {output_nc}")
        print(f"✅ 已保存: {output_png}")

    # 更新时间
    month += 1
    if month > 12:
        month = 1
        year += 1
