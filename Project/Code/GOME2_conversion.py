import xarray as xr
import numpy as np
import os

# ==== 设置年份 ====
year = 2020

# ==== 输入输出路径 ====
input_dir = f"../Data/GOME2/resampled/{year}"
output_dir = f"../Data/GOME2/processed/{year}"
os.makedirs(output_dir, exist_ok=True)

# ==== 遍历 12 个月份 ====
for month in range(1, 13):
    mm = f"{month:02d}"
    in_file = f"GOME2B_SIF{year}_{mm}_1x1.nc"
    out_file = f"GOME2B_SIF{year}_{mm}_1x1.nc"

    in_path = os.path.join(input_dir, in_file)
    out_path = os.path.join(output_dir, out_file)

    if not os.path.exists(in_path):
        print(f"❌ 缺失文件：{in_path}")
        continue

    # === 读取文件并转换经度 ===
    ds = xr.open_dataset(in_path)

    # 将经度转换为 [0, 360)
    ds = ds.assign_coords(lon=((ds.lon + 360) % 360))
    ds = ds.sortby('lon')

    # 替换经度坐标为整数网格点：0 到 359（每隔 1 度）
    if ds.dims['lon'] == 360:
        ds = ds.assign_coords(lon=np.arange(0, 360, 1))
    else:
        print(f"⚠️ 警告：{in_file} 中经度数量 ≠ 360，未修改为整数")

    # === 保存为新文件 ===
    ds.to_netcdf(out_path)
    print(f"✅ 已保存：{out_path}")
