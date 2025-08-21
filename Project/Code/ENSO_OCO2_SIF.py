import pandas as pd
import xarray as xr
import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt

# ==== 路径 ====
oni_path = Path("../Data/ONI.csv")  # 你的 ONI.csv
sif_base_dir = Path("../Data/SIF_final")  # SIF 数据目录（按年份分文件夹）

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

# ==== 匹配 SIF ====
results = []
for year_folder in sorted(sif_base_dir.glob("*")):
    if not year_folder.is_dir():
        continue
    year = int(year_folder.name)
    if year < 2014 or year > 2020:
        continue
    for month in range(1, 13):
        file_a = year_folder / f"sif_ann_{year}{month:02d}a_land.nc"
        file_b = year_folder / f"sif_ann_{year}{month:02d}b_land.nc"
        if file_a.exists() and file_b.exists():
            da_a = xr.open_dataset(file_a)
            da_b = xr.open_dataset(file_b)
            # 假设变量名叫 'SIF'（如果不对改这里）
            var_name = list(da_a.data_vars)[0]
            sif_a = da_a[var_name]
            sif_b = da_b[var_name]
            sif_mean = ((sif_a + sif_b) / 2).mean().item()
            oni_val = oni_monthly_df[(oni_monthly_df['Year'] == year) & (oni_monthly_df['Month'] == month)]
            oni_val = oni_val['ONI'].values[0] if not oni_val.empty else np.nan
            results.append({'Year': year, 'Month': month, 'SIF_mean': sif_mean, 'ONI': oni_val})

results_df = pd.DataFrame(results)
results_df.to_csv("../Data/ENSO/ONI/OCO2_SIF.csv", index=False)
print("匹配结果已保存到 SIF_ONI_matched.csv")

# ==== 绘图 ====
plt.figure(figsize=(12, 6))
plt.plot(pd.to_datetime(results_df[['Year','Month']].assign(DAY=1)), results_df['SIF_mean'], label='SIF mean', color='green')
plt.plot(pd.to_datetime(results_df[['Year','Month']].assign(DAY=1)), results_df['ONI'], label='ONI', color='red')
plt.axhline(0.5, color='gray', linestyle='--', label='El Niño threshold')
plt.axhline(-0.5, color='gray', linestyle='--', label='La Niña threshold')
plt.legend()
plt.xlabel("Time")
plt.ylabel("Value")
plt.title("OCO-2 SIF vs ONI (2014-2020)")
plt.tight_layout()
plt.savefig("../Data/ENSO/ONI/OCO2_SIF_timeseries.png", dpi=300)
plt.show()
