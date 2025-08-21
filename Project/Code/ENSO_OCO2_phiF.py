import pandas as pd
import xarray as xr
import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt
import glob
import os

# ==== 路径 ====
oni_path = Path("../Data/ONI.csv")  # 官方 ONI 数据
phiF_base_dir = Path("../Results/PhiF")  # phiF 数据目录

# ==== 读取 ONI 并展开到月份 ====
oni_df = pd.read_csv(oni_path)
oni_df = oni_df.melt(id_vars=['Year'], var_name='Season', value_name='ONI')

# 季节 → 月份映射
season_to_months = {
    'DJF': [12, 1, 2], 'JFM': [1, 2, 3], 'FMA': [2, 3, 4], 'MAM': [3, 4, 5],
    'AMJ': [4, 5, 6], 'MJJ': [5, 6, 7], 'JJA': [6, 7, 8], 'JAS': [7, 8, 9],
    'ASO': [8, 9, 10], 'SON': [9, 10, 11], 'OND': [10, 11, 12], 'NDJ': [11, 12, 1]
}

oni_monthly = []
for _, row in oni_df.iterrows():
    year = int(row['Year'])
    oni_val = row['ONI']
    for m in season_to_months[row['Season']]:
        y = year
        if row['Season'] in ['DJF', 'NDJ'] and m == 12:
            y = year - 1
        oni_monthly.append({'Year': y, 'Month': m, 'ONI': oni_val})

oni_monthly_df = pd.DataFrame(oni_monthly).drop_duplicates(subset=['Year', 'Month']).sort_values(['Year', 'Month'])

# ==== 匹配 phiF（a+b 合并） ====
results = []
for year_folder in sorted(phiF_base_dir.glob("*")):
    if not year_folder.is_dir():
        continue
    year = int(year_folder.name)
    if year < 2014 or year > 2020:
        continue
    for month in range(1, 13):
        file_a = year_folder / f"PhiF_{year}_{month:02d}_a.nc"
        file_b = year_folder / f"PhiF_{year}_{month:02d}_b.nc"
        if file_a.exists() and file_b.exists():
            da_a = xr.open_dataset(file_a)
            da_b = xr.open_dataset(file_b)
            var_name_a = list(da_a.data_vars)[0]
            var_name_b = list(da_b.data_vars)[0]
            phiF_combined = (da_a[var_name_a] + da_b[var_name_b]) / 2
            phiF_mean = phiF_combined.mean().item() * 100
            oni_val = oni_monthly_df[(oni_monthly_df['Year'] == year) & (oni_monthly_df['Month'] == month)]
            oni_val = oni_val['ONI'].values[0] if not oni_val.empty else np.nan
            results.append({'Year': year, 'Month': month, 'phiF_mean': phiF_mean, 'ONI': oni_val})

results_df = pd.DataFrame(results)
results_df.to_csv("../Data/ENSO/ONI/OCO2_phiF.csv", index=False)
print("匹配结果已保存到 OCO2_phiF.csv")

# ==== 绘图 ====
plt.figure(figsize=(12, 6))
plt.plot(pd.to_datetime(results_df[['Year','Month']].assign(DAY=1)), results_df['phiF_mean'], label='phiF mean * 100', color='green')
plt.plot(pd.to_datetime(results_df[['Year','Month']].assign(DAY=1)), results_df['ONI'], label='ONI', color='red')
plt.axhline(0.5, color='gray', linestyle='--', label='El Niño threshold')
plt.axhline(-0.5, color='gray', linestyle='--', label='La Niña threshold')
plt.legend()
plt.xlabel("Time")
plt.ylabel("Value")
plt.title("OCO-2 phiF vs ONI (2014-2020)")
plt.tight_layout()
plt.savefig("../Data/ENSO/ONI/OCO2_phiF_timeseries.png", dpi=300)
plt.show()
