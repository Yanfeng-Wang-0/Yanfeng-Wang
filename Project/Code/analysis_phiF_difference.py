import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
import os

# === 设置年份和路径 ===
year1 = 2019
year2 = 2020
phiF_dir = "../Results/PhiF"
mask_path = "../Data/IMERG_land_mask_1deg.nc"
save_path = f"../Results/Plot/phiF/difference/PhiF_diff_{year2}_{year1}_landmask.png"

def get_valid_months(year):
    path = f"{phiF_dir}/{year}"
    valid = []
    for m in range(1, 13):
        mm = f"{m:02d}"
        file_a = os.path.join(path, f"PhiF_{year}_{mm}_a.nc")
        file_b = os.path.join(path, f"PhiF_{year}_{mm}_b.nc")
        if os.path.exists(file_a) and os.path.exists(file_b):
            valid.append(m)
    return valid

def load_phiF_selected_months(year, selected_months):
    path = f"{phiF_dir}/{year}"
    monthly = []
    for m in selected_months:
        mm = f"{m:02d}"
        file_a = os.path.join(path, f"PhiF_{year}_{mm}_a.nc")
        file_b = os.path.join(path, f"PhiF_{year}_{mm}_b.nc")
        da_a = xr.open_dataset(file_a)["phiF_a"]
        da_b = xr.open_dataset(file_b)["phiF_b"]
        da_month = (da_a + da_b) / 2.0
        monthly.append(da_month)
    # 有效月数加权平均
    valid_counts = xr.concat([da.notnull() for da in monthly], dim="month").sum(dim="month")
    sum_data = xr.concat(monthly, dim="month").sum(dim="month", skipna=True)
    da_annual = sum_data / valid_counts
    return da_annual.where(valid_counts > 0)

# === 获取两个年份的共同有效月份 ===
valid1 = set(get_valid_months(year1))
valid2 = set(get_valid_months(year2))
common_months = sorted(valid1 & valid2)

if not common_months:
    raise ValueError("❌ 两年份无共同有效月份，无法计算差值")

print(f"📅 使用共同月份：{[f'{m:02d}' for m in common_months]}")

# === 计算两年的年均值（只用共同月份）===
phiF1 = load_phiF_selected_months(year1, common_months)
phiF2 = load_phiF_selected_months(year2, common_months)
delta_phiF = phiF2 - phiF1

# === 加载并修复 land mask ===
land_mask = xr.open_dataset(mask_path)["land_mask"]
land_mask = land_mask.assign_coords(lon=((land_mask.lon + 360) % 360))
_, unique_idx = np.unique(land_mask.lon, return_index=True)
land_mask = land_mask.isel(lon=unique_idx).sortby("lon")
land_mask_interp = land_mask.interp_like(delta_phiF, method="nearest")

# 构建背景掩膜图层
background = xr.where(land_mask_interp == 1, np.nan, 1.0)

# === 绘图 ===
plt.figure(figsize=(12, 6))
plt.pcolormesh(
    delta_phiF.lon.values,
    delta_phiF.lat.values,
    background.values,
    shading="auto",
    cmap="Greys",
    vmin=0,
    vmax=1,
    alpha=0.3
)

img = delta_phiF.plot.imshow(
    cmap="RdBu_r",
    vmin=-0.01,
    vmax=0.01,
    add_colorbar=True,
    cbar_kwargs={"label": f"ΔφF ({year2} - {year1})"}
)

plt.title(f"Change in φF: {year2} - {year1} (Matched Months)")
plt.tight_layout()
plt.savefig(save_path, dpi=300)
plt.close()
print(f"✅ φF 差值图已保存（共同月份）：{save_path}")
