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
YEAR = 2014
APAR_THRESHOLD = 3e-5  # <<<<<< 加入屏蔽阈值，避免高纬极端 φF 值

# ========= 路径 ==========
base_dir = '../Data'
sif_dir = os.path.join(base_dir, 'SIF_final')
fpar_dir = os.path.join(base_dir, 'FPAR_Processed')
nirv_dir = os.path.join(base_dir, 'NIRv')
par_sec_dir = os.path.join(base_dir, f'PAR_new/PAR_per_sec_{YEAR}')
fc_file = os.path.join(base_dir, 'yield_lambda.xlsx')
mask_file = os.path.join(base_dir, 'IMERG_land_mask_1deg.nc')
output_dir = f'../Results/PhiF/{YEAR}'
os.makedirs(output_dir, exist_ok=True)

# ========= 荧光谱转换因子 ==========
fc_df = pd.read_excel(fc_file, header=None, names=["lambda", "fc"])
fc_df = fc_df[(fc_df['lambda'] >= 640) & (fc_df['lambda'] <= 850)]
lambda_array = fc_df['lambda'].values * 1e-9
fc_weights = fc_df['fc'].values
delta_lambda = np.mean(np.diff(fc_df['lambda']))
P_sum = np.sum(fc_weights * lambda_array / (h * c * Na)) * delta_lambda * 3e-1

# ========= 加载陆地掩膜 ==========
land_mask = xr.open_dataset(mask_file)['land_mask']

# ========= 月份循环 ==========
months = ['{:02d}'.format(i) for i in range(1, 13)]

for month in months:
    print(f"\n📦 正在处理月份：{month}")

    fpar_file = os.path.join(fpar_dir, f'{YEAR}/FPAR_{YEAR}_{month}_1x1.nc')
    nirv_file = os.path.join(nirv_dir, f'{YEAR}/NIRv_{YEAR}_{month}_1x1.nc')
    par_sec_file = os.path.join(par_sec_dir, f'PAR_per_sec_{YEAR}_{month}.nc')

    if not all(map(os.path.exists, [fpar_file, nirv_file, par_sec_file])):
        print(f"❌ 缺失输入文件，跳过 {month}")
        continue

    fpar = xr.open_dataset(fpar_file)['FPAR'].mean(dim="time", skipna=True)
    nirv = xr.open_dataset(nirv_file)['NIRv'].mean(dim="time", skipna=True)
    par_per_sec = xr.open_dataset(par_sec_file)['PAR_per_sec']
    apar = par_per_sec * fpar
    apar_interp = apar

    # 插值掩膜
    land_mask_interp = land_mask.interp_like(apar_interp, method='nearest')

    phi_dict = {}
    for sif_label in ['a', 'b']:
        sif_file = os.path.join(sif_dir, f'{YEAR}/sif_ann_{YEAR}{month}{sif_label}_land.nc')
        if not os.path.exists(sif_file):
            print(f"⚠️ 缺失 SIF 文件 {sif_label}，跳过")
            continue

        sif_ds = xr.open_dataset(sif_file)
        sif = sif_ds['sif_ann'] 
        sif = sif.assign_coords(lon=((sif.lon + 360) % 360)).sortby('lon')
        sif_interp = sif

        # 屏蔽 APAR < 阈值
        valid_apar = apar_interp.where(apar_interp > APAR_THRESHOLD)

        # φF 计算
        phi_f = (sif_interp * PI * f_PSII * P_sum) / (f_esc * valid_apar) 
        phi_f = phi_f.where(valid_apar.notnull(), np.nan)
        phi_f = phi_f.where((phi_f >= 0), np.nan)

        # 填充空白为 0
        phi_f_filled = phi_f.fillna(0)

        # 海洋部分恢复为 NaN
        phi_f_final = phi_f_filled.where(land_mask_interp == 1, np.nan)

        phi_f.name = f"phiF_{sif_label}_original"
        phi_f_final.name = f"phiF_{sif_label}"

        phi_dict[sif_label] = phi_f_final

        print(f"[{month} {sif_label}] φF max: {float(phi_f_final.max().values):.4f}")
        print(f"[{month} {sif_label}] φF min: {float(phi_f_final.min().values):.4f}")
        print(f"[{month} {sif_label}] 有效像素: {int(np.isfinite(phi_f_final).sum())}")

    # ========= 保存和绘图 ==========
    if phi_dict:
        all_phi = xr.concat(list(phi_dict.values()), dim="label")
        vmin = np.nanpercentile(all_phi, 5)
        vmax = np.nanpercentile(all_phi, 95)

        for sif_label, phi_f_final in phi_dict.items():
            phi_f_final.to_netcdf(os.path.join(output_dir, f"PhiF_{YEAR}_{month}_{sif_label}.nc"))

            plt.figure(figsize=(10, 6))
            ax = phi_f_final.plot.imshow(
                cmap='viridis',
                vmin=vmin,
                vmax=0.040,
                cbar_kwargs={'label': 'φF'}
            )
            ax.axes.set_aspect('equal')
            plt.title(f"φF for {YEAR}-{month} ({sif_label})")
            plt.tight_layout()
            plt.savefig(os.path.join(output_dir, f"PhiF_{YEAR}_{month}_{sif_label}.png"), dpi=300)
            plt.close()
            print(f"🖼️ 图像保存: {sif_label}")

print("\n✅ 全年 φF 计算与掩膜完成")
