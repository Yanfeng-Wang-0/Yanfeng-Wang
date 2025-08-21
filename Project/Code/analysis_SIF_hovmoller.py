import os
import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import matplotlib.dates as mdates

# === 设置路径 ===
data_root = "../Data/SIF_final"
start_year, end_year = 2014, 2020
all_sif = []

# === 遍历所有年份和月份 ===
for year in range(start_year, end_year + 1):
    for month in range(1, 13):
        mm = f"{month:02d}"
        file_a = os.path.join(data_root, f"{year}", f"sif_ann_{year}{mm}a_land.nc")
        file_b = os.path.join(data_root, f"{year}", f"sif_ann_{year}{mm}b_land.nc")

        if not os.path.exists(file_a) or not os.path.exists(file_b):
            print(f"❌ 缺失 {file_a} 或 {file_b}，跳过")
            continue

        da_a = xr.open_dataset(file_a)["sif_ann"] * 1e-9
        da_b = xr.open_dataset(file_b)["sif_ann"] * 1e-9
        da_mean = ((da_a + da_b) / 2.0).assign_coords(
            time=pd.to_datetime(f"{year}-{mm}-15")
        )

        all_sif.append(da_mean)

# === 合并为一个 DataArray（time, lat, lon）===
sif_all = xr.concat(all_sif, dim="time")
sif_all = sif_all.sortby("time")
print(f"✅ 合并成功：{sif_all.sizes}")

# === 计算 climatology（多年同月平均）===
sif_climatology = sif_all.groupby("time.month").mean("time")

# === 计算 anomaly（当前月 - 平均月）===
sif_anomaly = sif_all.groupby("time.month") - sif_climatology

# === 沿经度平均，得到 time × lat 的 Hovmöller 图 ===
sif_zonal_anomaly = sif_anomaly.mean(dim="lon")

# === 检测哪些整月是全为 NaN 的 ===
nan_months = sif_zonal_anomaly.isnull().all(dim="lat")
missing_times = sif_zonal_anomaly["time"].values[nan_months.values]
print(f"📅 缺失月份数量: {len(missing_times)}")

# === 可视化 ===
fig, ax = plt.subplots(figsize=(11, 5))

# 主图
sif_zonal_anomaly.T.plot(
    ax=ax,
    cmap="RdBu_r",
    vmin=-4e-11,
    vmax=4e-11,
    cbar_kwargs={"label": "SIF Anomaly [W/m²/sr/nm]"}
)

# 黑色半透明遮罩缺失月份
for t in missing_times:
    ax.axvspan(t - np.timedelta64(15, "D"), t + np.timedelta64(15, "D"),
               color="black", alpha=0.15)

# 标题与坐标轴
plt.title("Zonal Mean SIF Anomalies (2014–2020)")
plt.xlabel("Time")
plt.ylabel("Latitude")
plt.tight_layout()

# 保存图像
output_path = "../Results/Plot/SIF/sif_zonal_anomaly_hovmoller_masked_black.png"
os.makedirs(os.path.dirname(output_path), exist_ok=True)
plt.savefig(output_path, dpi=300)
plt.show()
print(f"✅ 图像已保存：{output_path}")
