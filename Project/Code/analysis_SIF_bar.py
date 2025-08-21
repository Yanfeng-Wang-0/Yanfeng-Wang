import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
import os

start_year, end_year = 2014, 2020
output_dir = "../Results/Plot/SIF/Bar Plot"
os.makedirs(output_dir, exist_ok=True)

# 准备统一色图
months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
x = np.arange(1, 13)

all_years_data = {}

for year in range(start_year, end_year + 1):
    print(f"\n📊 正在处理年份：{year}")
    sif_dir = f"../Data/SIF_final/{year}"
    mask_path = f"../Data/landcover/mask/landcover_{year}_1deg_mask_1to10.nc"

    if not os.path.exists(mask_path):
        print(f"⚠️ 掩膜文件不存在：{mask_path}，跳过 {year}")
        continue

    mask = xr.open_dataset(mask_path)["LC_Mask_1to10"]
    monthly_means = []

    for month in range(1, 13):
        month_str = f"{month:02d}"
        file_a = os.path.join(sif_dir, f"sif_ann_{year}{month_str}a_land.nc")
        file_b = os.path.join(sif_dir, f"sif_ann_{year}{month_str}b_land.nc")

        if not os.path.exists(file_a) or not os.path.exists(file_b):
            print(f"❌ 缺失 {file_a} 或 {file_b}，跳过")
            monthly_means.append(np.nan)
            continue

        da_a = xr.open_dataset(file_a)["sif_ann"] * 1e-9
        da_b = xr.open_dataset(file_b)["sif_ann"] * 1e-9

        da_a = da_a.assign_coords(lon=((da_a.lon + 360) % 360)).sortby("lon")
        da_b = da_b.assign_coords(lon=((da_b.lon + 360) % 360)).sortby("lon")

        da_month = (da_a + da_b) / 2.0
        da_masked = da_month.where((mask == 1) & (da_month > 0))

        weights = np.cos(np.deg2rad(da_masked['lat']))
        weights_2d = weights.broadcast_like(da_masked)

        weighted_sum = (da_masked * weights_2d).sum(dim=["lat", "lon"], skipna=True)
        total_weights = weights_2d.where(np.isfinite(da_masked)).sum(dim=["lat", "lon"], skipna=True)

        mean_value = (weighted_sum / total_weights).item()
        monthly_means.append(mean_value)
        print(f"✅ {year}-{month_str} 平均 SIF: {mean_value:.4e}")

    all_years_data[year] = monthly_means

    # 每年单独输出图
    plt.figure(figsize=(9, 5))
    plt.bar(x, monthly_means, color="seagreen", edgecolor="black")
    plt.xticks(ticks=x, labels=months)
    plt.ylabel("Monthly Mean SIF (W m⁻² sr⁻¹ nm⁻¹)")
    plt.xlabel("Month")
    plt.title(f"Global Monthly Mean SIF in {year} (Landcover 1–10, Weighted)")
    plt.grid(axis="y", linestyle="--", alpha=0.5)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, f"SIF_monthly_barplot_{year}_weighted.png"), dpi=300)
    plt.close()

# ==== 输出所有年份对比图 ====
if all_years_data:
    plt.figure(figsize=(11, 6))
    for year, values in all_years_data.items():
        plt.plot(x, values, marker='o', label=str(year))

    plt.xticks(ticks=x, labels=months)
    plt.ylabel("Monthly Mean SIF (W m⁻² sr⁻¹ nm⁻¹)")
    plt.xlabel("Month")
    plt.title("Comparison of Global Monthly Mean SIF (2014–2020)")
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "SIF_monthly_trends_2014_2020.png"), dpi=300)
    plt.close()

print("\n✅ 所有年份分析与输出完成")
