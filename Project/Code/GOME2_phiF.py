import os
import xarray as xr
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# ========= 常量 ==========
PI = np.pi
h = 6.626e-34
c = 2.998e8
Na = 6.022e23
f_esc = 0.47
f_PSII = 0.66
YEAR = 2020
APAR_THRESHOLD = 3e-5

# ========= 路径 ==========
base_dir = '../Data'
sif_dir = os.path.join(base_dir, f'GOME2/final/{YEAR}')
fpar_dir = os.path.join(base_dir, 'FPAR_Processed')
par_sec_dir = os.path.join(base_dir, f'PAR_new/PAR_per_sec_{YEAR}')
fc_file = os.path.join(base_dir, 'yield_lambda.xlsx')
mask_file = os.path.join(base_dir, 'IMERG_land_mask_1deg.nc')
output_dir = f'../Results/GOME2/phiF/{YEAR}'
os.makedirs(output_dir, exist_ok=True)

# ========= 荧光谱转换因子 ==========
fc_df = pd.read_excel(fc_file, header=None, names=["lambda", "fc"])
fc_df = fc_df[(fc_df['lambda'] >= 640) & (fc_df['lambda'] <= 850)]
lambda_array = fc_df['lambda'].values * 1e-9
fc_weights = fc_df['fc'].values
delta_lambda = np.mean(np.diff(fc_df['lambda']))
P_sum = np.sum(fc_weights * lambda_array / (h * c * Na)) * delta_lambda * 3e-1

# ========= 陆地掩膜 ==========
land_mask = xr.open_dataset(mask_file)['land_mask']

# ========= 月份处理 ==========
months = ['{:02d}'.format(i) for i in range(1, 13)]
phi_list = []

for month in months:
    print(f"\n📦 正在处理月份：{month}")
    fpar_file = os.path.join(fpar_dir, f'{YEAR}/FPAR_{YEAR}_{month}_1x1.nc')
    par_file = os.path.join(par_sec_dir, f'PAR_per_sec_{YEAR}_{month}.nc')
    sif_file = os.path.join(sif_dir, f'GOME2B_SIF_{YEAR}_{month}_land.nc')

    if not all(map(os.path.exists, [fpar_file, par_file, sif_file])):
        print(f"❌ 缺失输入文件，跳过 {month}")
        continue

    # === 加载数据 ===
    fpar = xr.open_dataset(fpar_file)['FPAR'].mean(dim="time", skipna=True)
    par_sec = xr.open_dataset(par_file)['PAR_per_sec']
    apar = par_sec * fpar / 2
    apar_interp = apar

    # 掩膜插值
    land_mask_interp = land_mask.interp_like(apar_interp, method='nearest')

    sif = xr.open_dataset(sif_file)['SIF']  # 单位转为 W m⁻² nm⁻¹ sr⁻¹
    sif = sif.assign_coords(lon=((sif.lon + 360) % 360)).sortby('lon')
    sif_interp = sif

    # APAR 阈值屏蔽
    valid_apar = apar_interp.where(apar_interp > APAR_THRESHOLD)

    # φF 计算
    phi_f = (sif_interp * PI * f_PSII * P_sum) / (f_esc * valid_apar) 
    phi_f = phi_f.where(valid_apar.notnull(), np.nan)
    phi_f = phi_f.where(phi_f >= 0, np.nan)

    # 填零再恢复海洋为 NaN
    phi_f_filled = phi_f.fillna(0)
    phi_f_final = phi_f_filled.where(land_mask_interp == 1, np.nan)
    phi_f_final.name = "phiF"

    # 保存 .nc
    phi_f_final.to_netcdf(os.path.join(output_dir, f"PhiF_{YEAR}_{month}_a.nc"))

    # 缓存用于统一色标
    phi_list.append(phi_f_final)

# ===== 统一绘图色阶 =====
print("\n📊 计算全年色标范围...")
all_phi = xr.concat(phi_list, dim="month")
vmin = np.nanpercentile(all_phi, 5)
vmax = np.nanpercentile(all_phi, 95)

# ===== 绘图 =====
for month, phi_f_final in zip(months, phi_list):
    plt.figure(figsize=(10, 6))
    ax = phi_f_final.plot.imshow(
        cmap='viridis',
        vmin=vmin,
        vmax=0.04,
        cbar_kwargs={'label': 'φF'}
    )
    ax.axes.set_aspect('equal')
    plt.title(f"φF from GOME2B {YEAR}-{month}")
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, f"PhiF_{YEAR}_{month}_a.png"), dpi=300)
    plt.close()
    print(f"🖼️ 图像已保存: PhiF_{YEAR}_{month}_a.png")

print("\n✅ GOME2 φF 计算完成！")
