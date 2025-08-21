import xarray as xr
import os

# === 设置输入输出路径与年份 ===
year = 2020
input_dir = f"../Data/GOME2/raw/GOME2B_SIF{year}"
output_dir = f"../Data/GOME2/resampled/{year}"
os.makedirs(output_dir, exist_ok=True)

# === 遍历 1 月到 12 月 ===
for month in range(1, 13):
    mm = f"{month:02d}"
    file_name = f"GOME2B_SIF{year}_{mm}.nc"
    input_path = os.path.join(input_dir, file_name)
    output_path = os.path.join(output_dir, f"GOME2B_SIF{year}_{mm}_1x1.nc")

    if not os.path.exists(input_path):
        print(f"❌ 跳过缺失文件：{input_path}")
        continue

    print(f"✅ 处理文件：{input_path}")
    
    # === 打开数据 ===
    ds = xr.open_dataset(input_path)

    # === 获取原始分辨率 ===
    lat_res = abs(ds['lat'][1] - ds['lat'][0]).item()
    lon_res = abs(ds['lon'][1] - ds['lon'][0]).item()
    lat_factor = int(1 / lat_res)
    lon_factor = int(1 / lon_res)

    # === 重采样（聚合为1°网格） ===
    ds_1x1 = ds.coarsen(lat=lat_factor, lon=lon_factor, boundary="trim").mean()

    # === 保存重采样文件 ===
    ds_1x1.to_netcdf(output_path)
    print(f"🎉 已保存：{output_path}")
