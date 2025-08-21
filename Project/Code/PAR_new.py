import xarray as xr
import numpy as np
import os

# ========== 年度设置 ==========
year = "2011"

# ========== 日照数据加载（全年只加载一次） ==========
day_file = f"../Data/global_daylength.nc"
day_ds = xr.open_dataset(day_file)["daylength_min"]

# ========== 遍历 12 个月 ==========
for m in range(1, 13):
    month = f"{m:02d}"
    par_file = f"../Data/PAR/{year}/PAR_1x1_{year}_{month}.nc"
    output_file = f"../Data/PAR_new/PAR_per_sec_{year}/PAR_per_sec_{year}_{month}.nc"
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    if not os.path.exists(par_file):
        print(f"❌ 跳过 {month}：找不到 {par_file}")
        continue

    print(f"📦 正在处理 {year}-{month}...")

    # ========== 加载 PAR ==========
    par = xr.open_dataset(par_file)["PAR"]
    if "time" in par.dims:
        par = par.mean(dim="time", skipna=True)

    # ========== 获取对应日期的日照 ==========
    if "time" in day_ds.dims:
        day = day_ds.sel(time=f"{year}-{month}-16", method="nearest")
    else:
        day = day_ds

    # ==== 转换单位 ====
    day_sec = day * 60
    day_sec = day_sec.broadcast_like(par)

    # ==== 合理掩膜 ====
    day_safe = day_sec.where(day_sec > 0)
    valid_mask = np.isfinite(par) & np.isfinite(day_safe)
    par_masked = par.where(valid_mask)
    day_masked = day_safe.where(valid_mask)

    # ========== 计算 PAR_per_sec ==========
    par_sec = par_masked / day_masked
    par_sec.name = "PAR_per_sec"
    par_sec.attrs["units"] = "mol m⁻² s⁻¹"
    par_sec.attrs["description"] = "PAR divided by daylight seconds"

    # ========== 保存 ==========
    par_sec.to_netcdf(output_file)
    print(f"✅ 已保存：{output_file}")
