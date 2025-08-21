import os
import numpy as np
import matplotlib.pyplot as plt
import xarray as xr
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
from matplotlib.colors import LogNorm

# 设置年份范围
start_year, end_year = 2014, 2020

# 设定路径
phiF_root = "../Results/PhiF"
sif_root = "../Data/SIF_Processed"

phiF_list = []
sif_list = []

# 遍历年份和月份
for year in range(start_year, end_year + 1):
    for month in range(1, 13):
        mm = f"{month:02d}"
        phiF_file_a = os.path.join(phiF_root, f"{year}", f"PhiF_{year}_{mm}_a.nc")
        phiF_file_b = os.path.join(phiF_root, f"{year}", f"PhiF_{year}_{mm}_b.nc")
        sif_file_a = os.path.join(sif_root, f"{year}", f"sif_ann_{year}{mm}a.nc")
        sif_file_b = os.path.join(sif_root, f"{year}", f"sif_ann_{year}{mm}b.nc")

        if not all(os.path.exists(p) for p in [phiF_file_a, phiF_file_b, sif_file_a, sif_file_b]):
            print(f"⏭️ 缺数据，跳过 {year}-{mm}")
            continue

        phiF_a = xr.open_dataset(phiF_file_a)["phiF_a"]
        phiF_b = xr.open_dataset(phiF_file_b)["phiF_b"]
        sif_a = xr.open_dataset(sif_file_a)["sif_ann"] * 1e-9  # mW → W
        sif_b = xr.open_dataset(sif_file_b)["sif_ann"] * 1e-9

        # 对齐并平均
        phiF = ((phiF_a + phiF_b) / 2.0).broadcast_like(sif_a)
        sif = (sif_a + sif_b) / 2.0

        phiF_list.append(phiF.values.flatten())
        sif_list.append(sif.values.flatten())

# 合并所有年份的值
phiF_all = np.concatenate(phiF_list)
sif_all = np.concatenate(sif_list)

# 数据清洗
mask = np.isfinite(phiF_all) & np.isfinite(sif_all)
x = sif_all[mask].reshape(-1, 1)
y = phiF_all[mask]

# 拟合回归线
model = LinearRegression().fit(x, y)
y_pred = model.predict(x)
r2 = r2_score(y, y_pred)

# 绘图
plt.figure(figsize=(8, 7))
plt.hist2d(x.flatten(), y, bins=250, cmap="PuBuGn", norm=LogNorm(), cmin=10)

# 1:1 红线
min_val = min(x.min(), y.min())
max_val = max(x.max(), y.max())
plt.plot([min_val, max_val], [min_val, max_val], 'r--', label="1:1 Line")

# 拟合线
plt.plot(x, y_pred, color='black', linewidth=1.5, alpha=0.8, label=f"Fit (R²={r2:.2f})")

# 坐标范围建议
plt.xlim(0, np.percentile(x, 99.5))
plt.ylim(0, np.percentile(y, 99.5))

# 标签
plt.xlabel("SIF [W/m²/sr/nm]", fontsize=14)
plt.ylabel("φF", fontsize=14)
plt.title("φF vs. SIF (2014–2020)", fontsize=16)
plt.tick_params(labelsize=12)
plt.legend(fontsize=12)
plt.colorbar(label="Point Density")

plt.tight_layout()
output_dir = "../Results/Plot/PhiF_vs_SIF"
os.makedirs(output_dir, exist_ok=True)
plt.savefig(os.path.join(output_dir, "phiF_vs_SIF_all_years.png"), dpi=300)
plt.show()

print("✅ φF vs SIF 综合图已保存")
