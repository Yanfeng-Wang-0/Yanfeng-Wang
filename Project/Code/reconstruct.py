import os
import xarray as xr
import numpy as np
import pandas as pd

# === 正确设置路径 ===
data_dir = "../Results/PhiF/"
output_path = "../Results/PhiF_monthly_cube_1deg.nc"
years = range(2014, 2021)

time_list = []
phiF_array_list = []

for year in years:
    year_path = os.path.join(data_dir, str(year))
    for month in range(1, 13):
        fname_a = f"PhiF_{year}_{month:02d}_a.nc"
        fname_b = f"PhiF_{year}_{month:02d}_b.nc"
        path_a = os.path.join(year_path, fname_a)
        path_b = os.path.join(year_path, fname_b)
        if not os.path.exists(path_a) or not os.path.exists(path_b):
            print(f"[跳过] 缺失文件: {fname_a} 或 {fname_b}")
            continue

        # === 打开数据并自动获取变量名 ===
        dsa = xr.open_dataset(path_a)
        dsb = xr.open_dataset(path_b)
        var_a = list(dsa.data_vars)[0]
        var_b = list(dsb.data_vars)[0]

        phiF_a = dsa[var_a]
        phiF_b = dsb[var_b]

        # === 平均栅格，添加时间戳 ===
        phiF_mean = (phiF_a + phiF_b) / 2
        timestamp = pd.Timestamp(f"{year}-{month:02d}-15")
        time_list.append(timestamp)
        phiF_array_list.append(phiF_mean)

        dsa.close()
        dsb.close()

# === 构建 DataArray 并保存 ===
phiF_cube = xr.concat(phiF_array_list, dim="time")
phiF_cube = phiF_cube.assign_coords(time=("time", time_list))
phiF_cube.name = "phiF"

phiF_cube.to_netcdf(output_path)
print(f"\n✅ 保存成功: {output_path}")
print(f"📐 数据形状: {phiF_cube.sizes}")
