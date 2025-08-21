import xarray as xr
import numpy as np
import matplotlib.pyplot as plt

year = 2014

input_path = f"../Data/landcover/resampled/landcover_{year}_1deg.nc"
output_mask_path = f"../Data/landcover/mask/landcover_{year}_1deg_mask_1to10_12.nc"

ds = xr.open_dataset(input_path)
lc = ds["LC_Type"]

# === 关键修改：直接在 DataArray 上用 xr.where ===
classes = list(range(1, 11)) + [12]
mask = xr.where(lc.isin(classes), 1, 0)   # 保持 DataArray 类型
mask.name = "LC_Mask_1to10_12"

mask.to_netcdf(output_mask_path)
print(f"✅ 掩膜已保存: {output_mask_path}")

plt.figure(figsize=(12, 5))
mask.plot(cmap="Greens", cbar_kwargs={"label": "Mask (1: LC 1–10 & 12, 0: Other)"})
plt.title("Land Cover Mask (Types 1–10 & 12)")
plt.tight_layout()
plt.show()
