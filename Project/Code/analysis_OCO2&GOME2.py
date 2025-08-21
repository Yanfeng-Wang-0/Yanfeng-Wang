import os
import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import mean_squared_error, mean_absolute_error
from scipy.stats import pearsonr
import pandas as pd

start_year, end_year = 2014, 2020
gome_base = "../Data/GOME2/final"
oco_base = "../Data/SIF_final"
out_base = "../Results/Plot/OCO2_GOME2"

for YEAR in range(start_year, end_year + 1):
    gome_dir = os.path.join(gome_base, str(YEAR))
    oco_dir = os.path.join(oco_base, str(YEAR))
    save_dir = os.path.join(out_base, str(YEAR))
    os.makedirs(save_dir, exist_ok=True)

    results = []
    months = [f"{i:02d}" for i in range(1, 13)]

    for month in months:
        gome_file = os.path.join(gome_dir, f"GOME2B_SIF_{YEAR}_{month}_land.nc")
        oco_file_a = os.path.join(oco_dir, f"sif_ann_{YEAR}{month}a_land.nc")
        oco_file_b = os.path.join(oco_dir, f"sif_ann_{YEAR}{month}b_land.nc")

        missing = []
        if not os.path.exists(gome_file): missing.append("GOME2")
        if not os.path.exists(oco_file_a): missing.append("OCO2-a")
        if not os.path.exists(oco_file_b): missing.append("OCO2-b")
        if missing:
            print(f"⚠️ {YEAR}-{month} 缺失：{', '.join(missing)}，跳过")
            continue

        # === 加载数据 ===
        gome_ds = xr.open_dataset(gome_file)
        gome_var = [v for v in gome_ds.data_vars if gome_ds[v].ndim == 2][0]
        sif_gome = gome_ds[gome_var]

        oco_a = xr.open_dataset(oco_file_a)["sif_ann"]
        oco_b = xr.open_dataset(oco_file_b)["sif_ann"]
        sif_oco = (oco_a + oco_b) / 2 / 1000  # OCO2单位换算 mW ➝ W
        sif_oco = sif_oco.interp_like(sif_gome, method="nearest")

        # === 有效值筛选 ===
        g_flat = sif_gome.values.flatten()
        o_flat = sif_oco.values.flatten()
        mask = np.isfinite(g_flat) & np.isfinite(o_flat)
        g_valid = g_flat[mask]
        o_valid = o_flat[mask]
        if len(g_valid) == 0:
            print(f"⚠️ {YEAR}-{month} 无有效像元，跳过")
            continue

        # === 指标计算 ===
        bias = np.mean(g_valid - o_valid)
        rmse = np.sqrt(mean_squared_error(o_valid, g_valid))
        mae = mean_absolute_error(o_valid, g_valid)
        r, _ = pearsonr(o_valid, g_valid)
        results.append({"year": YEAR, "month": month, "bias": bias, "rmse": rmse, "mae": mae, "r": r})

        print(f"✅ {YEAR}-{month}: r={r:.3f}, RMSE={rmse:.3f}, Bias={bias:.3f}")

        # ==== 图 1: 差值图 ====
        plt.figure(figsize=(6, 4))
        (sif_gome - sif_oco).plot(cmap="bwr", center=0)
        plt.title(f"Diff: GOME2 - OCO2 {YEAR}-{month}")
        plt.tight_layout()
        plt.savefig(os.path.join(save_dir, f"SIF_Diff_{YEAR}_{month}.png"), dpi=300)
        plt.close()

        # ==== 图 2: 散点图（自动缩放） ====
        max_val = max(g_valid.max(), o_valid.max())
        plt.figure(figsize=(6, 6))
        plt.scatter(o_valid, g_valid, alpha=0.2, s=2)
        plt.plot([0, max_val], [0, max_val], 'r--')
        plt.xlim(0, max_val)
        plt.ylim(0, max_val)
        plt.xlabel("OCO-2 SIF (W m⁻² sr⁻¹ nm⁻¹)")
        plt.ylabel("GOME2 SIF (W m⁻² sr⁻¹ nm⁻¹)")
        plt.title(f"Scatter: {YEAR}-{month}\nr={r:.2f}, RMSE={rmse:.3f}, Bias={bias:.3f}")
        plt.grid(True)
        plt.tight_layout()
        plt.savefig(os.path.join(save_dir, f"SIF_Scatter_{YEAR}_{month}.png"), dpi=300)
        plt.close()

        # ==== 图 3: 纬度剖面 ====
        zonal_gome = sif_gome.mean(dim="lon", skipna=True)
        zonal_oco = sif_oco.mean(dim="lon", skipna=True)
        plt.figure(figsize=(6, 5))
        plt.plot(zonal_gome, sif_gome.lat, label="GOME2", lw=2)
        plt.plot(zonal_oco, sif_oco.lat, label="OCO-2", lw=2)
        plt.xlabel("Zonal Mean SIF")
        plt.ylabel("Latitude")
        plt.title(f"Zonal Mean SIF: {YEAR}-{month}")
        plt.grid(True)
        plt.legend()
        plt.tight_layout()
        plt.savefig(os.path.join(save_dir, f"SIF_Zonal_{YEAR}_{month}.png"), dpi=300)
        plt.close()

        # ==== 图 4: 误差直方图 ====
        diff = g_valid - o_valid
        plt.figure(figsize=(6, 4))
        plt.hist(diff, bins=50, color="gray", edgecolor="black")
        plt.axvline(bias, color="red", linestyle="--", label=f"Bias = {bias:.3f}")
        plt.xlabel("GOME2 - OCO2")
        plt.ylabel("Frequency")
        plt.title(f"Bias Histogram: {YEAR}-{month}")
        plt.legend()
        plt.tight_layout()
        plt.savefig(os.path.join(save_dir, f"SIF_HistDiff_{YEAR}_{month}.png"), dpi=300)
        plt.close()

    # === 保存年度统计表 ===
    if results:
        df = pd.DataFrame(results)
        df.to_csv(os.path.join(save_dir, f"stats_GOME2_OCO2_{YEAR}.csv"), index=False)
        print(f"📁 {YEAR} 完成，结果保存至：{save_dir}")
