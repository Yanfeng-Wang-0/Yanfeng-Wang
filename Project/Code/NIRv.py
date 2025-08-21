import os
import xarray as xr
import matplotlib.pyplot as plt
import cartopy.crs as ccrs

input_dir = "../Data/NIRv_processed"
output_dir = "../Results/NIRv"
os.makedirs(output_dir, exist_ok=True)

years = range(2014, 2021)
months = ["{:02d}".format(m) for m in range(1, 13)]

for year in years:
    for month_str in months:
        file_path = os.path.join(input_dir, f"NIRv_{year}_{month_str}_1x1_IMERGmask.nc")
        if not os.path.exists(file_path):
            print(f"❌ 缺少文件: {file_path}")
            continue

        ds = xr.open_dataset(file_path)
        nirv = ds["NIRv"].mean(dim="time")

        # 检查负值
        negative_mask = nirv < 0
        negative_count = negative_mask.sum().item()
        total_count = nirv.size
        ratio = negative_count / total_count * 100

        print(f"⚠️  {year}-{month_str}: 有 {negative_count} 个负值像元，占比 {ratio:.2f}%")

        # 保存正常的 NIRv 图像
        fig = plt.figure(figsize=(10, 5))
        ax = plt.axes(projection=ccrs.PlateCarree())
        nirv.plot(ax=ax, transform=ccrs.PlateCarree(), cmap="YlGn", 
                  cbar_kwargs={'label': 'NIRv'}, vmin=0, vmax=0.5)
        ax.coastlines()
        ax.set_title(f"NIRv - {year}-{month_str}")
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, f"NIRv_{year}_{month_str}.png"), dpi=150)
        plt.close()

        # 保存负值掩膜图
        fig = plt.figure(figsize=(10, 5))
        ax = plt.axes(projection=ccrs.PlateCarree())
        negative_mask.plot(ax=ax, transform=ccrs.PlateCarree(), cmap="Reds", 
                           cbar_kwargs={'label': 'Negative NIRv Mask'})
        ax.coastlines()
        ax.set_title(f"NIRv Negative Values - {year}-{month_str}")
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, f"NIRv_NegativeMask_{year}_{month_str}.png"), dpi=150)
        plt.close()
