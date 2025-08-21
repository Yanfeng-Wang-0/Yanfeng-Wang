import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
import os

# === 设置年份和路径 ===
year1 = 2014
year2 = 2015
sif_dir = "../Data/SIF_final"
mask_path = "../Data/IMERG_land_mask_1deg.nc"
save_path = f"../Results/Plot/SIF/difference/SIF_diff_{year2}_{year1}_landmask.png"
os.makedirs(os.path.dirname(save_path), exist_ok=True)

def get_valid_months(year):
    path = f"{sif_dir}/{year}"
    valid = []
    for m in range(1, 13):
        mm = f"{m:02d}"
        file_a = os.path.join(path, f"sif_ann_{year}{mm}a_land.nc")
        file_b = os.path.join(path, f"sif_ann_{year}{mm}b_land.nc")
        if os.path.exists(file_a) and os.path.exists(file_b):
            valid.append(m)
    return valid

def load_sif_selected_months(year, selected_months):
    path = f"{sif_dir}/{year}"
    monthly = []
    for m in selected_months:
        mm = f"{m:02d}"
        file_a = os.path.join(path, f"sif_ann_{year}{mm}a_land.nc")
        file_b = os.path.join(path, f"sif_ann_{year}{mm}b_land.nc")
        da_a = xr.open_dataset(file_a)["sif_ann"] * 1e-9
        da_b = xr.open_dataset(file_b)["sif_ann"] * 1e-9
        da_month = (da_a + da_b) / 2.0
        da_month = da_month.assign_coords(lon=((da_month.lon + 360) % 360)).sortby("lon")
        monthly.append(da_month)

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

# === 年均差值 ===
sif1 = load_sif_selected_months(year1, common_months)
sif2 = load_sif_selected_months(year2, common_months)
delta_sif = sif2 - sif1

# === 加载陆地掩膜 ===
land_mask = xr.open_dataset(mask_path)["land_mask"]
land_mask = land_mask.assign_coords(lon=((land_mask.lon + 360) % 360))
_, unique_idx = np.unique(land_mask.lon, return_index=True)
land_mask = land_mask.isel(lon=unique_idx).sortby("lon")
land_mask_interp = land_mask.interp_like(delta_sif, method="nearest")
background = xr.where(land_mask_interp == 1, np.nan, 1.0)

# === 绘图 ===
plt.figure(figsize=(12, 6))
plt.pcolormesh(
    delta_sif.lon.values,
    delta_sif.lat.values,
    background.values,
    shading="auto",
    cmap="Greys",
    vmin=0,
    vmax=1,
    alpha=0.3
)

img = delta_sif.plot.imshow(
    cmap="RdBu_r",
    vmin=-0.00000000005,
    vmax=0.00000000005,
    add_colorbar=True,
    cbar_kwargs={"label": f"ΔSIF ({year2} - {year1}) [W/m²/sr/nm]"}
)

plt.title(f"Change in SIF: {year2} - {year1} (Matched Months)")
plt.tight_layout()
plt.savefig(save_path, dpi=300)
plt.close()
print(f"✅ SIF 差值图已保存（共同月份）：{save_path}")
