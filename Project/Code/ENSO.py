import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import ttest_ind

# ==== 1. 读取数据 ====
# 修改成你的 CSV 路径（OCO-2、GOME-2 都可以用）
csv_path = "../Data/ENSO/ONI/OCO2_SIF_phiF.csv"
df = pd.read_csv(csv_path)

# ==== 2. 划分 ENSO 阶段 ====
def classify_enso(oni):
    if oni >= 0.5:
        return "El Nino"
    elif oni <= -0.5:
        return "La Nina"
    else:
        return "Neutral"

df["ENSO_phase"] = df["ONI"].apply(classify_enso)

# ==== 3. 分阶段统计 ====
stats_df = df.groupby("ENSO_phase")[["SIF_mean", "phiF_mean"]].agg(["mean", "std", "count"])
print("\n=== ENSO 阶段统计 ===")
print(stats_df)

# ==== 4. 显著性检验（两两阶段） ====
phases = ["El Nino", "La Nina", "Neutral"]
for var in ["SIF_mean", "phiF_mean"]:
    print(f"\n=== {var} 阶段两两 t 检验 ===")
    for i in range(len(phases)):
        for j in range(i+1, len(phases)):
            group1 = df[df["ENSO_phase"] == phases[i]][var]
            group2 = df[df["ENSO_phase"] == phases[j]][var]
            t_stat, p_val = ttest_ind(group1, group2, equal_var=False)
            print(f"{phases[i]} vs {phases[j]}: T={t_stat:.3f}, p={p_val:.3e}")

# ==== 5. 可视化 ====
sns.set(style="whitegrid", font_scale=1.2)

plt.figure(figsize=(10, 5))
sns.boxplot(x="ENSO_phase", y="SIF_mean", data=df, order=phases,
            palette={"El Nino":"#d73027", "La Nina":"#4575b4", "Neutral":"#f0f0f0"})
plt.title("SIF mean across ENSO phases")
plt.savefig("../Data/ENSO/boxplot_SIF_ENSO.png", dpi=300)
plt.show()

plt.figure(figsize=(10, 5))
sns.boxplot(x="ENSO_phase", y="phiF_mean", data=df, order=phases,
            palette={"El Nino":"#d73027", "La Nina":"#4575b4", "Neutral":"#f0f0f0"})
plt.title("phiF mean across ENSO phases")
plt.savefig("../Data/ENSO/boxplot_phiF_ENSO.png", dpi=300)
plt.show()
