import xarray as xr
import numpy as np
from scipy.ndimage import zoom
import matplotlib.pyplot as plt
import os

year = 2014

# === 输入文件路径（修改为你实际的路径）===
input_path = f"../Data/landcover/raw/output_landcover_{year}.nc"  # 高分辨率原始 land cover 文件
output_path = f"../Data/landcover/resampled/landcover_{year}_1deg.nc"   # 重采样输出路径

# === 打开原始 land cover 数据（变量名为 'Band1'）===
ds = xr.open_dataset(input_path)
da = ds["Band1"]  # 如果变量名不是 Band1，print(ds) 查看并修改这里

# === 获取原始尺寸（如 shape: [y=1800, x=3600]）===
ny, nx = da.shape
print(f"原始数据尺寸: {ny} × {nx}")

# === 设置目标网格尺寸（1°：180 × 360），并计算缩放因子 ===
target_lat = 180
target_lon = 360
zoom_factors = (target_lat / ny, target_lon / nx)

# === 使用最近邻法（order=0）重采样，适用于分类变量 ===
resampled_data = zoom(da.values, zoom=zoom_factors, order=0)

# === 生成新的纬度和经度坐标（与 φF 数据对齐）===
lat_new = np.arange(-89.5, 90.5, 1.0)   # 纬度中心点：-89.5 到 89.5，共180格
lon_new = np.arange(0, 360, 1.0)        # 经度中心点：0 到 359，共360格

# === 构建重采样后的 DataArray ===
da_resampled = xr.DataArray(
    resampled_data,
    dims=["lat", "lon"],
    coords={"lat": lat_new, "lon": lon_new},
    name="LC_Type"
)

# === 保存为新的 NetCDF 文件 ===
da_resampled.to_netcdf(output_path)
print(f"✅ 重采样完成，结果保存为：{output_path}")

# === 可选：可视化检查结果 ===
plt.figure(figsize=(12, 5))
da_resampled.plot(cmap="tab20", cbar_kwargs={"label": "Land Cover Type (IGBP Code)"})
plt.title("Land Cover Resampled to 1° × 1°")
plt.tight_layout()
plt.show()
