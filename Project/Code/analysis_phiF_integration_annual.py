import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
import os

for year in range(2014, 2021):
    print(f"\n📅 正在处理年份：{year}")
    
    phiF_dir = f"../Results/PhiF/{year}"
    output_path = f"../Results/Plot/phiF/Longitudinal Integration Plot/PhiF_{year}_annual_mean_ab_with_profiles.png"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    monthly_means = []

    # === 逐月读取、a+b平均后累加 ===
    for month in range(1, 13):
        month_str = f"{month:02d}"
        file_a = os.path.join(phiF_dir, f"PhiF_{year}_{month_str}_a.nc")
        file_b = os.path.join(phiF_dir, f"PhiF_{year}_{month_str}_b.nc")

        if not os.path.exists(file_a) or not os.path.exists(file_b):
            print(f"❌ 缺失 {file_a} 或 {file_b}，跳过")
            continue

        da_a = xr.open_dataset(file_a)["phiF_a"]
        da_b = xr.open_dataset(file_b)["phiF_b"]
        da_month = (da_a + da_b) / 2.0

        monthly_means.append(da_month)

    if not monthly_means:
        print(f"⚠️ {year} 没有有效月数据，跳过该年")
        continue

    print(f"📊 使用有效月份数量进行平均，共使用 {len(monthly_means)} 个月")

    # 有效像素计数
    valid_counts = xr.concat([da.notnull() for da in monthly_means], dim="month").sum(dim="month")
    sum_data = xr.concat(monthly_means, dim="month").sum(dim="month", skipna=True)
    da_annual = sum_data / valid_counts
    da_annual = da_annual.where(valid_counts > 0)

    # 纬向/经向平均
    zonal_mean = da_annual.mean(dim="lon", skipna=True)
    meridional_mean = da_annual.mean(dim="lat", skipna=True)

    # === 绘图 ===
    fig = plt.figure(figsize=(10, 6))
    gs = fig.add_gridspec(2, 2, width_ratios=(5, 1.5), height_ratios=(4, 1.2),
                          left=0.08, right=0.88, bottom=0.1, top=0.92, wspace=0.05, hspace=0.05)

    ax_map = fig.add_subplot(gs[0, 0])
    img = da_annual.plot.imshow(ax=ax_map, cmap='viridis', add_colorbar=False,
                                vmin=0.0, vmax=0.04)
    ax_map.set_title(f"φF Annual Mean in {year} (a + b averaged)")

    ax_right = fig.add_subplot(gs[0, 1], sharey=ax_map)
    ax_right.plot(zonal_mean, da_annual["lat"])
    ax_right.set_xlabel("φF")
    ax_right.grid(True)
    plt.setp(ax_right.get_yticklabels(), visible=False)

    ax_bottom = fig.add_subplot(gs[1, 0], sharex=ax_map)
    ax_bottom.plot(da_annual["lon"], meridional_mean)
    ax_bottom.set_ylabel("φF")
    ax_bottom.grid(True)
    plt.setp(ax_bottom.get_xticklabels(), visible=False)

    ax_empty = fig.add_subplot(gs[1, 1])
    ax_empty.axis("off")

    cax = fig.add_axes([0.9, 0.2, 0.02, 0.6])
    cbar = fig.colorbar(img, cax=cax)
    cbar.set_label("φF")

    plt.savefig(output_path, dpi=300)
    plt.close()
    print(f"✅ 年平均 φF 图已保存：{output_path}")
