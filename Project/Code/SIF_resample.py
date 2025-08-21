import os
import xarray as xr

# 数据路径
sif_dir = "../Data/SIF/2020/"
output_dir = "../Data/SIF_Resampled/2020/"
os.makedirs(output_dir, exist_ok=True)

# 获取所有 SIF 文件
sif_files = sorted([f for f in os.listdir(sif_dir) if f.endswith(".nc")])

# 降采样参数
lat_factor = 20
lon_factor = 20

for sif_file in sif_files:
    input_path = os.path.join(sif_dir, sif_file)
    output_path = os.path.join(output_dir, sif_file)
    
    # 读取 SIF 数据
    ds = xr.open_dataset(input_path)
    
    # 检查数据变量
    if "sif_ann" not in ds:
        print(f"❌ 无法找到 'sif_ann' 变量: {sif_file}")
        continue
    
    # 提取 SIF 数据
    sif_data = ds["sif_ann"]
    
    # 降采样
    sif_resampled = sif_data.coarsen(lat=lat_factor, lon=lon_factor, boundary="trim").mean()
    
    # 更新属性信息
    sif_resampled.attrs = sif_data.attrs
    sif_resampled.name = "sif_ann"
    
    # 保存降采样后的数据
    sif_resampled.to_netcdf(output_path)
    print(f"✅ 已保存: {output_path}") 