import xarray as xr
import matplotlib.pyplot as plt
import numpy as np
import os

# ===== 参数设置 =====
month_year = (2018, 7)  # 年和月
oco2_file = "../Results/SIF_monthly/2018/sif_ann_201807_ab_land.nc"
gome2_file = "../Data/GOME2/final/2018/GOME2B_SIF_2018_07_land.nc"
mask_file = "../Data/landcover/mask/landcover_2018_1deg_mask_1to10_12.nc"
output_dir = "../Results/Plot/analysis"
os.makedirs(output_dir, exist_ok=True)

# ===== 数据读取 =====
oco2 = xr.open_dataset(oco2_file)["sif_ann"]
gome2 = xr.open_dataset(gome2_file)["SIF"]  # 单位匹配
mask = xr.open_dataset(mask_file)
mask_var = list(mask.data_vars)[0]
mask_bool = mask[mask_var].where(mask[mask_var].isin(range(1, 11)))
mask_bool = ~np.isnan(mask_bool)

# 应用掩膜
oco2 = oco2.where(mask_bool)
gome2 = gome2.where(mask_bool)

# ===== 差值计算 =====
diff = oco2 - gome2

# ===== 1. 差值地图（叠加陆地形状）=====
import cartopy.crs as ccrs
import cartopy.feature as cfeature

plt.figure(figsize=(12, 5))

# 如果经度是 0–360，建议 central_longitude=180；否则用默认 PlateCarree()
proj = ccrs.PlateCarree(central_longitude=180) if float(diff.lon.max()) > 180 else ccrs.PlateCarree()
ax = plt.axes(projection=proj)

# xarray 在投影坐标轴上作图要声明数据的原始坐标系（PlateCarree）
im = diff.plot(
    ax=ax, transform=ccrs.PlateCarree(),
    cmap="RdBu_r", vmin=-1.0, vmax=1.0,
    cbar_kwargs={"label": "SIF Difference (OCO2 - GOME2)"},
    add_labels=False
)

# 叠加海岸线/国界/陆地底色（可选）
ax.coastlines(resolution="110m", linewidth=0.6)
ax.add_feature(cfeature.BORDERS.with_scale("110m"), linewidth=0.3, alpha=0.5)
# ax.add_feature(cfeature.LAND.with_scale("110m"), facecolor="none", edgecolor="none")  # 需要面填充时可开启

# 网格线与范围
gl = ax.gridlines(draw_labels=True, linestyle=":", linewidth=0.5, alpha=0.6)
gl.right_labels = False; gl.top_labels = False
ax.set_global()  # 或 ax.set_extent([0, 360, -60, 90], crs=ccrs.PlateCarree())

plt.title(f"SIF Difference Map ({month_year[0]}-{month_year[1]:02d})")
plt.tight_layout()
plt.savefig(os.path.join(output_dir, f"SIF_diff_map_{month_year[0]}_{month_year[1]:02d}.png"), dpi=300)
plt.close()

# ===== 2. Hexbin Analysis（只显示正值） =====
plt.figure(figsize=(6, 6))

# 有效像元：两边都不是 NaN 且 都 > 0
valid = (~np.isnan(oco2)) & (~np.isnan(gome2)) & (oco2 > 0) & (gome2 > 0)

x = oco2.values[valid]
y = gome2.values[valid]

# 轴范围：从 0 开始到 99 分位，避免极端值撑满画面
xmax = float(np.nanpercentile(x, 99))
ymax = float(np.nanpercentile(y, 99))
xmin, ymin = 0.0, 0.0

plt.hexbin(x, y, gridsize=50, cmap="viridis", mincnt=1)
plt.plot([xmin, max(xmax, ymax)], [ymin, max(xmax, ymax)], "r--", lw=1)  # 1:1 线
plt.xlim(xmin, xmax)
plt.ylim(ymin, ymax)
plt.xlabel("OCO2 SIF")
plt.ylabel("GOME2 SIF")
plt.colorbar(label="Counts")

# 用同一过滤后的数据计算相关
r = np.corrcoef(x, y)[0, 1]
plt.title(f"Hexbin Analysis (R²={r**2:.2f})")

plt.savefig(os.path.join(output_dir, f"SIF_hexbin_{month_year[0]}_{month_year[1]:02d}.png"), dpi=300)
plt.close()

# ===== 3. Zonal Mean Difference =====
zonal_diff = diff.mean(dim="lon")
plt.figure(figsize=(5, 6))
plt.plot(zonal_diff, zonal_diff["lat"], label="Mean Difference")
plt.axvline(0, color="gray", linestyle="--")
plt.xlabel("SIF Difference (OCO2 - GOME2)")
plt.ylabel("Latitude")
plt.title(f"Zonal Mean Difference ({month_year[0]}-{month_year[1]:02d})")
plt.grid(True)
plt.legend()
plt.savefig(os.path.join(output_dir, f"SIF_zonal_diff_{month_year[0]}_{month_year[1]:02d}.png"), dpi=300)
plt.close()
