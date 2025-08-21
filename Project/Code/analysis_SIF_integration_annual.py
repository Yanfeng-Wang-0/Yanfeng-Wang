import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
import os

# === 设置时间范围与输出路径 ===
start_year, end_year = 2014, 2020
output_path = f"../Results/Plot/SIF/Longitudinal Integration Plot"
os.makedirs(output_path, exist_ok=True)

# === 遍历所有年份 ===
for year in range(start_year, end_year + 1):
    print(f"\n📊 正在处理年份：{year}")
    sif_dir = f"../Data/SIF_final/{year}"
    sif_monthly_means = []

    for month in range(1, 13):
        month_str = f"{month:02d}"
        file_a = os.path.join(sif_dir, f"sif_ann_{year}{month_str}a_land.nc")
        file_b = os.path.join(sif_dir, f"sif_ann_{year}{month_str}b_land.nc")

        if not os.path.exists(file_a) or not os.path.exists(file_b):
            print(f"❌ 缺失 {file_a} 或 {file_b}，跳过该月")
            continue

        da_a = xr.open_dataset(file_a)["sif_ann"] * 1e-9  # nW → W
        da_b = xr.open_dataset(file_b)["sif_ann"] * 1e-9

        # 经度调整
        da_a = da_a.assign_coords(lon=((da_a.lon + 360) % 360)).sortby("lon")
        da_b = da_b.assign_coords(lon=((da_b.lon + 360) % 360)).sortby("lon")

        da_month = (da_a + da_b) / 2.0
        sif_monthly_means.append(da_month)

    if not sif_monthly_means:
        print(f"⚠️ {year} 无有效数据，跳过")
        continue

    print(f"📊 使用 {len(sif_monthly_means)} 个月计算年平均")
    valid_counts = xr.concat([da.notnull() for da in sif_monthly_means], dim="month").sum(dim="month")
    sum_data = xr.concat(sif_monthly_means, dim="month").sum(dim="month", skipna=True)
    da_annual = sum_data / valid_counts
    da_annual = da_annual.where(valid_counts > 0)

    # 经纬剖面
    zonal_mean = da_annual.mean(dim="lon", skipna=True)
    meridional_mean = da_annual.mean(dim="lat", skipna=True)

    # === 绘图结构 ===
    fig = plt.figure(figsize=(10, 6))
    gs = fig.add_gridspec(2, 2, width_ratios=(5, 1.5), height_ratios=(4, 1.2),
                          left=0.08, right=0.88, bottom=0.1, top=0.92, wspace=0.05, hspace=0.05)

    ax_map = fig.add_subplot(gs[0, 0])
    img = da_annual.plot.imshow(ax=ax_map, cmap='plasma', add_colorbar=False,
                                vmin=0.0, vmax=np.nanpercentile(da_annual, 99))
    ax_map.set_title(f"SIF Annual Mean in {year} (a + b averaged)")

    ax_right = fig.add_subplot(gs[0, 1], sharey=ax_map)
    ax_right.plot(zonal_mean, da_annual["lat"])
    ax_right.set_xlabel("SIF (W m⁻² sr⁻¹ nm⁻¹)")
    ax_right.grid(True)
    plt.setp(ax_right.get_yticklabels(), visible=False)

    ax_bottom = fig.add_subplot(gs[1, 0], sharex=ax_map)
    ax_bottom.plot(da_annual["lon"], meridional_mean)
    ax_bottom.set_ylabel("SIF (W m⁻² sr⁻¹ nm⁻¹)")
    ax_bottom.grid(True)
    plt.setp(ax_bottom.get_xticklabels(), visible=False)

    ax_empty = fig.add_subplot(gs[1, 1])
    ax_empty.axis("off")

    cax = fig.add_axes([0.9, 0.2, 0.02, 0.6])
    cbar = fig.colorbar(img, cax=cax)
    cbar.set_label("SIF (W m⁻² sr⁻¹ nm⁻¹)")

    save_path = os.path.join(output_path, f"SIF_{year}_annual_mean_ab_with_profiles.png")
    plt.savefig(save_path, dpi=300)
    plt.close()
    print(f"✅ 已保存图像：{save_path}")

print("\n🎉 所有年份处理完毕！")
