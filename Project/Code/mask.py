import xarray as xr
import numpy as np

# === 设置输入输出路径 ===
input_path = "../Data/IMERG_land_sea_mask.nc"     # 替换为你的水面百分比文件路径
output_path = "../Data/IMERG_land_mask_1deg.nc"   # 输出的陆地掩膜文件

# === 读取水面覆盖百分比 ===
ds = xr.open_dataset(input_path)
water_pct = ds["landseamask"]  # 取值范围 0-100，表示水体覆盖率百分比

# === 判定陆地区域 ===
# 小于 60% 的地方认为是陆地（保留干旱区）；海洋赋为 NaN
land_mask = xr.where(water_pct < 60, 1, np.nan)

# === 添加坐标名与变量名（便于后续插值）===
land_mask.name = "land_mask"
land_mask.attrs["description"] = "1=Land, NaN=Ocean based on water coverage <60%"

# === 保存为 NetCDF ===
land_mask.to_netcdf(output_path)
print(f"✅ 已保存陆地掩膜至: {output_path}")
