import os
import xarray as xr
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# 常量
PI = np.pi
PAR_CONVERSION_FACTOR = 1 / 0.3940  # mol m-2 d-1 → W m-2
h = 6.626e-34  # Planck constant [J*s]
c = 2.998e8     # Speed of light [m/s]
Na = 6.022e23   # Avogadro constant [mol^-1]

YEAR = 2020  # 可修改为所需年份

# 文件路径
base_dir = '../Data'
sif_dir = os.path.join(base_dir, 'SIF_Processed')
fpar_dir = os.path.join(base_dir, 'FPAR_Processed')
nirv_dir = os.path.join(base_dir, 'NIRv')
par_dir = os.path.join(base_dir, 'PAR')
lambda_file = os.path.join(base_dir, 'yield_lambda.xlsx')
output_dir = f'../Results/PhiF/{YEAR}'
if not os.path.exists(output_dir): os.makedirs(output_dir)

# 检查 Lambda 文件
if not os.path.exists(lambda_file):
    print(f"❌ 找不到 Lambda 文件：{lambda_file}")
    exit()

# 读取 lambda 数据
lambda_df = pd.read_excel(lambda_file, header=None, names=['band', 'lambda'])
lambda_df.set_index('band', inplace=True)

# 月份列表
months = ['{:02d}'.format(i) for i in range(1, 13)]

for month in months:
    print(f"处理月份：{month}")

    sif_file_a = os.path.join(sif_dir, f'{YEAR}/sif_ann_{YEAR}{month}a.nc')
    sif_file_b = os.path.join(sif_dir, f'{YEAR}/sif_ann_{YEAR}{month}b.nc')
    fpar_file = os.path.join(fpar_dir, f'{YEAR}/FPAR_{YEAR}_{month}_1x1.nc')
    nirv_file = os.path.join(nirv_dir, f'{YEAR}/NIRv_{YEAR}_{month}_1x1.nc')
    par_file = os.path.join(par_dir, f'{YEAR}/PAR_1x1_{YEAR}_{month}.nc')

    if not all(map(os.path.exists, [sif_file_a, sif_file_b, fpar_file, nirv_file, par_file])):
        print(f"❌ 数据文件缺失，跳过 {month}")
        continue

    fpar = xr.open_dataset(fpar_file)['FPAR'].mean(dim="time", skipna=True)
    nirv = xr.open_dataset(nirv_file)['NIRv'].mean(dim="time", skipna=True)
    par = xr.open_dataset(par_file)['PAR'].mean(dim="time", skipna=True) * PAR_CONVERSION_FACTOR

    target_lat, target_lon = nirv.lat, nirv.lon
    fpar_interp = fpar.interp(lat=target_lat, lon=target_lon, method="linear")

    for sif_label, sif_path in zip(['a', 'b'], [sif_file_a, sif_file_b]):
        sif_ds = xr.open_dataset(sif_path)
        sif = sif_ds['sif_ann'] * 1e-3
        sif = sif.assign_coords(lon=((sif.lon + 360) % 360)).sortby('lon')
        sif_interp = sif.interp(lat=target_lat, lon=target_lon, method="linear")

        band_value = 757  # 按照你要求固定为 757nm
        P_lambda = lambda_df['lambda'].get(band_value, 0.5)
        P_lambda_array = xr.DataArray(P_lambda, coords={"lat": target_lat, "lon": target_lon}, dims=["lat", "lon"])

        # 单位转换：W/m^2 → mol/m^2
        lambda_m = band_value * 1e-9
        energy_to_photon = lambda_m / (h * c * Na)
        sif_interp = sif_interp * energy_to_photon

        phi_f = (sif_interp * PI) / (par * P_lambda_array * nirv)
        phi_f = phi_f.where((par > 0) & (nirv > 0) & (fpar_interp > 0), np.nan)

        output_file = os.path.join(output_dir, f"PhiF_{YEAR}_{month}_{sif_label}.nc")
        phi_f.to_netcdf(output_file)

        if phi_f.notnull().sum() > 0:
            vmin, vmax = 0, 0.1
            plt.figure(figsize=(10, 6))
            ax = phi_f.plot.imshow(
                cmap='viridis',
                vmin=vmin,
                vmax=vmax,
                cbar_kwargs={'label': 'PhiF (0 - 0.1)'}
            )
            ax.axes.set_aspect('equal')
            plt.title(f"PhiF Visualization for {month} {YEAR} ({sif_label})")
            plt.tight_layout()
            plt.savefig(os.path.join(output_dir, f"PhiF_{YEAR}_{month}_{sif_label}.png"))
            plt.close()
        else:
            print(f"❌ {month} ({sif_label}) 没有有效数据用于绘图")

print("✅ 全年处理完成（a 和 b 分开输出）！")
