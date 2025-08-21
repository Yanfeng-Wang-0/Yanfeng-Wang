import os
import xarray as xr

# 文件路径
sif_dir = "../Data/SIF_Resampled/2020/"
output_dir = "../Data/SIF_Processed/2020/"
os.makedirs(output_dir, exist_ok=True)

# NIRv 或 PAR 数据的目标经纬度坐标系 (1° × 1°)
target_file = "../Data/NIRv/2015/NIRv_2015_07_1x1.nc"
target_ds = xr.open_dataset(target_file)
target_lat = target_ds.lat
target_lon = target_ds.lon

# 遍历 SIF 数据文件
for sif_file in os.listdir(sif_dir):
    if sif_file.endswith(".nc"):
        input_path = os.path.join(sif_dir, sif_file)
        output_path = os.path.join(output_dir, sif_file)

        # 读取 SIF 数据
        ds = xr.open_dataset(input_path)
        if "sif_ann" not in ds:
            print(f"❌ 未找到 'sif_ann' 变量: {sif_file}")
            continue

        sif_data = ds["sif_ann"]

        # 经度转换: -180° ~ 180° → 0° ~ 360°
        sif_data = sif_data.assign_coords(lon=((sif_data.lon + 360) % 360)).sortby('lon')

        # 经纬度插值
        sif_interpolated = sif_data.interp(lat=target_lat, lon=target_lon, method="linear")

        # 保存结果
        sif_interpolated.to_netcdf(output_path)
        print(f"✅ 已保存: {output_path}")