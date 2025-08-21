import os
import xarray as xr

# 文件路径
fpar_dir = "../Data/FPAR/2021/"
output_dir = "../Data/FPAR_Processed/2021/"
os.makedirs(output_dir, exist_ok=True)

# 目标经纬度坐标系 (1° × 1°) - 基于 NIRv 数据
target_file = "../Data/NIRv/2015/NIRv_2015_07_1x1.nc"
target_ds = xr.open_dataset(target_file)
target_lat = target_ds.lat
target_lon = target_ds.lon

# 遍历 FPAR 数据文件
for fpar_file in os.listdir(fpar_dir):
    if fpar_file.endswith(".nc"):
        input_path = os.path.join(fpar_dir, fpar_file)
        output_path = os.path.join(output_dir, fpar_file)

        # 读取 FPAR 数据
        ds = xr.open_dataset(input_path)
        if "FPAR" not in ds:
            print(f"❌ 未找到 'FPAR' 变量: {fpar_file}")
            continue

        fpar_data = ds["FPAR"]

        # 经度转换: -180° ~ 180° → 0° ~ 360°
        fpar_data = fpar_data.assign_coords(lon=((fpar_data.lon + 360) % 360)).sortby('lon')

        # 经纬度插值
        fpar_interpolated = fpar_data.interp(lat=target_lat, lon=target_lon, method="linear")

        # 保存结果
        fpar_interpolated.to_netcdf(output_path)
        print(f"✅ 已保存: {output_path}")
