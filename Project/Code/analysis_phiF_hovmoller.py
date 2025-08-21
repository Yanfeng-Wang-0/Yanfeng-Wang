# analysis_phiF_hovmoller.py  —— 修复版：对齐掩膜 & 经度统一 0–360
import os
from pathlib import Path
import numpy as np
import pandas as pd
import xarray as xr
import matplotlib.pyplot as plt

# ================= 配置 =================
START_YEAR, END_YEAR = 2014, 2020
DATA_DIR = Path("../Results/fesc_OCO2")                 # 每月一个 φF 文件
MASK_DIR = Path("../Data/landcover/mask")               # 年度掩膜目录
FILENAME_FMT = "fesc_phiF_{year}_{month:02d}_vza5.nc"   # φF 文件名
MASK_FILE_FMT = "landcover_{year}_1deg_mask_1to10_12.nc"
OUT_PNG = Path("../Results/Plot/phiF/phiF_zonal_anomaly_hovmoller_masked.png")
OUT_PNG.parent.mkdir(parents=True, exist_ok=True)

VMIN, VMAX = -0.005, 0.005
# ======================================

# --------- 辅助函数 ---------
def find_lat_name(ds):
    for k in ["lat", "latitude", "y"]:
        if k in ds.coords or k in ds.dims:
            return k
    raise ValueError("未发现纬度坐标（lat/latitude）。")

def find_lon_name(ds):
    for k in ["lon", "longitude", "x"]:
        if k in ds.coords or k in ds.dims:
            return k
    raise ValueError("未发现经度坐标（lon/longitude）。")

def std_latlon(da: xr.DataArray) -> xr.DataArray:
    """把经纬维/坐标名统一到 lat/lon。"""
    lat = next((d for d in da.dims if d.lower() in ("lat","latitude","y")), None)
    lon = next((d for d in da.dims if d.lower() in ("lon","longitude","x")), None)
    if lat is None:
        lat = next((c for c in da.coords if c.lower() in ("lat","latitude","y")), None)
    if lon is None:
        lon = next((c for c in da.coords if c.lower() in ("lon","longitude","x")), None)
    if lat is None or lon is None:
        raise ValueError(f"无法识别经纬度：dims={da.dims}, coords={list(da.coords)}")
    if lat != "lat": da = da.rename({lat: "lat"})
    if lon != "lon": da = da.rename({lon: "lon"})
    return da

def to_lon0360(da: xr.DataArray) -> xr.DataArray:
    """经度统一到 [0,360) 并排序。"""
    lon_new = (da.lon % 360 + 360) % 360
    da = da.assign_coords(lon=lon_new).sortby("lon")
    da.lon.attrs.update(units="degrees_east", long_name="longitude (0-360)")
    return da

def pick_mask_var(ds):
    if "LC_Mask_1to10_12" in ds.data_vars:
        return ds["LC_Mask_1to10_12"]
    cands = [v for v in ds.data_vars if "mask" in v.lower()]
    if not cands:
        raise ValueError(f"掩膜变量未找到，现有变量：{list(ds.data_vars)}")
    return ds[cands[0]]

def pick_phif_var(ds):
    num_vars = [v for v in ds.data_vars if np.issubdtype(ds[v].dtype, np.number)]
    pref = [v for v in num_vars if "phif" in v.lower()] or \
           [v for v in num_vars if "phi" in v.lower()]
    if pref:
        return ds[pref[0]]
    if not num_vars:
        raise ValueError(f"没有数值型数据变量，现有变量：{list(ds.data_vars)}")
    return ds[num_vars[0]]

def align_mask_to_data(mask: xr.DataArray, da: xr.DataArray) -> xr.DataArray:
    """把掩膜对齐到数据网格：最近邻（避免 reindex 造成整列 NaN）。"""
    mask = std_latlon(mask); mask = to_lon0360(mask)
    da   = std_latlon(da)   ; da   = to_lon0360(da)
    # 坐标完全一致则直接返回
    try:
        if np.allclose(mask.lat, da.lat) and np.allclose(mask.lon, da.lon):
            return mask
    except Exception:
        pass
    return mask.interp_like(da, method="nearest")

# ---------------------------

all_list = []

for year in range(START_YEAR, END_YEAR + 1):
    # 读取该年的掩膜并标准化
    mask_path = MASK_DIR / MASK_FILE_FMT.format(year=year)
    if not mask_path.exists():
        print(f"⚠️ 掩膜缺失：{mask_path}，跳过该年")
        continue
    ds_mask = xr.open_dataset(mask_path)
    mask_raw = pick_mask_var(ds_mask)

    for month in range(1, 13):
        f = DATA_DIR / FILENAME_FMT.format(year=year, month=month)
        if not f.exists():
            print(f"❌ 缺失：{f.name}，跳过")
            continue

        with xr.open_dataset(f) as ds:
            da = pick_phif_var(ds)
            da = std_latlon(da); da = to_lon0360(da)
            mask = align_mask_to_data(mask_raw, da)

            # 应用掩膜与合理范围（避免极值）
            da_use = da.where((mask == 1) & np.isfinite(da) & (da >= 0.0) & (da <= 0.05))

            # 诊断：该月各纬带有效像元数量的最小值
            valid_per_lat = np.isfinite(da_use).sum(dim="lon")
            if int(valid_per_lat.max()) == 0:
                print(f"[{year}-{month:02d}] 掩膜对齐后该月所有纬度均无有效像元（全 NaN）")
            elif int(valid_per_lat.min()) == 0:
                lats_empty = da_use["lat"].values[(valid_per_lat==0).values]
                print(f"[{year}-{month:02d}] 某些纬度无有效像元：{np.round(lats_empty,1)}")

            # 赋时间坐标（当月 15 号）
            da_use = da_use.assign_coords(time=pd.to_datetime(f"{year}-{month:02d}-15"))

            all_list.append(da_use)

# 合并 (time, lat, lon)
if not all_list:
    raise SystemExit("没有可用的 φF 数据，检查路径/文件名/掩膜。")
phiF_all = xr.concat(all_list, dim="time").sortby("time")
# —— 删掉最后 3 个月
DROP_N_LAST = 3
if phiF_all.sizes["time"] > DROP_N_LAST:
    phiF_all = phiF_all.isel(time=slice(None, -DROP_N_LAST))
else:
    raise SystemExit("可用月份不足以删除最后3个月")
phiF_all = phiF_all.sortby("lat")  # 保证纬度从南到北
print("✅ 合并完成：", {k: int(v) for k, v in phiF_all.sizes.items()})

# 多年同月平均（climatology）与距平（anomaly）
phiF_clim = phiF_all.groupby("time.month").mean("time")
phiF_anom = phiF_all.groupby("time.month") - phiF_clim

# 沿经度平均，得到 Hovmöller（lat × time）
phiF_zonal_anom = phiF_anom.mean(dim="lon")

# 检测整列 NaN 的月份与整行 NaN 的纬度
nan_months = phiF_zonal_anom.isnull().all(dim="lat")
missing_times = phiF_zonal_anom["time"].values[nan_months.values]
nan_lats = phiF_zonal_anom.isnull().all(dim="time")
missing_lats = phiF_zonal_anom["lat"].values[nan_lats.values]
print(f"📅 缺失月份数：{len(missing_times)}；缺失整条纬带：{np.round(missing_lats,1)}")

# 绘图
fig, ax = plt.subplots(figsize=(11, 5))
# 为了更容易发现 NaN，设 NaN 显示为浅灰
cmap = plt.get_cmap("RdBu_r").copy()
cmap.set_bad(color="#f0f0f0")

phiF_zonal_anom.T.plot(
    ax=ax, cmap=cmap, vmin=VMIN, vmax=VMAX,
    cbar_kwargs={"label": "φF Anomaly"},
    add_labels=False,
)

# 用半透明黑条标注缺失月份
for t in missing_times:
    ax.axvspan(t - np.timedelta64(15, "D"),
               t + np.timedelta64(15, "D"),
               color="black", alpha=0.12)

ax.set_title(f"Zonal Mean φF Anomalies ({START_YEAR}–{END_YEAR}, LC 1–10 & 12)")
ax.set_xlabel("Time")
ax.set_ylabel("Latitude")
plt.tight_layout()
plt.savefig(OUT_PNG, dpi=300)
plt.close()
print(f"✅ 已保存：{OUT_PNG}")
