import os
import xarray as xr
import matplotlib.pyplot as plt
import cartopy.crs as ccrs

# 设置输入和输出基础路径
input_base_dir = "../Data/FPAR"
output_base_dir = "../Results/FPAR"
os.makedirs(output_base_dir, exist_ok=True)

# 遍历2011到2021年
for year in range(2011, 2022):
    input_dir = os.path.join(input_base_dir, str(year))
    output_dir = os.path.join(output_base_dir, str(year))
    os.makedirs(output_dir, exist_ok=True)

    for month in range(1, 13):
        month_str = f"{month:02d}"
        file_name = f"FPAR_{year}_{month_str}_1x1.nc"
        file_path = os.path.join(input_dir, file_name)

        if not os.path.exists(file_path):
            print(f"❌ 文件不存在: {file_path}")
            continue

        # 打开 NetCDF 文件
        ds = xr.open_dataset(file_path)
        
        # 假设变量名是 FPAR
        fpar = ds["FPAR"].mean(dim="time")  # 按时间轴平均
        
        # 绘图
        fig = plt.figure(figsize=(10, 5))
        ax = plt.axes(projection=ccrs.PlateCarree())
        fpar.plot(ax=ax, transform=ccrs.PlateCarree(), cmap="YlGn", 
                  cbar_kwargs={'label': 'FPAR'})
        ax.coastlines()
        ax.set_title(f"FPAR - {year}-{month_str}")
        plt.tight_layout()

        # 保存输出图片
        output_file = os.path.join(output_dir, f"FPAR_{year}_{month_str}.png")
        plt.savefig(output_file, dpi=150)
        plt.close()
        print(f"✅ 已保存: {output_file}")
