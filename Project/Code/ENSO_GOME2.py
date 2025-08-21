# ENSO_GOME2_masked_new.py
import pandas as pd
import xarray as xr
import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt

# ========= 路径与文件模板 =========
oni_path = Path("../Data/ONI.csv")

# —— GOME-2 SIF（优先用你新生成的 0–360 月度单文件）
GOME2_SIF_PATTERNS = [
    "../Results/GOME2/SIF/GOME2_lon0360/GOME2B_SIF_{YYYY}_{MM}_land_lon0360.nc",
]

# —— GOME-2 φF（若也另存了 lon0360，把相应模板放在前面）
GOME2_PHIF_PATTERNS = [
    "../Results/fesc_GOME2/fesc_phiF_{YYYY}_{MM}_vzaAll.nc"
]

# —— 年度掩膜（LC 1–10 & 12）
MASK_PATTERN = "../Data/landcover/mask/landcover_{YYYY}_1deg_mask_1to10_12.nc"

# 输出
out_dir = Path("../Data/ENSO/ONI")
out_dir.mkdir(parents=True, exist_ok=True)

# 可选：限定时间段（与 OCO-2 口径一致）
LIMIT_RANGE = True
RANGE_START = "2014-09-01"
RANGE_END   = "2020-04-30"

# ========= 小工具 =========
def _find_existing(patterns, YYYY, MM) -> Path:
    for pat in patterns:
        p = Path(pat.format(YYYY=YYYY, MM=f"{MM:02d}"))
        if p.exists():
            return p
    return None

def _std_latlon(da: xr.DataArray) -> xr.DataArray:
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

def _to_lon0360(da: xr.DataArray) -> xr.DataArray:
    lon_new = (da.lon % 360 + 360) % 360
    da = da.assign_coords(lon=lon_new).sortby("lon")
    da.lon.attrs.update(units="degrees_east", long_name="longitude (0-360)")
    return da

def _pick_var(ds: xr.Dataset, hints=("sif","phif","phi")) -> xr.DataArray:
    nums = [v for v in ds.data_vars if np.issubdtype(ds[v].dtype, np.number)]
    for h in hints:
        for v in nums:
            if h.lower() in v.lower():
                return ds[v]
    if not nums:
        raise ValueError(f"没有数值型变量：{list(ds.data_vars)}")
    return ds[nums[0]]

def _open_mask(year: int) -> xr.DataArray | None:
    fp = Path(MASK_PATTERN.format(YYYY=year))
    if not fp.exists():
        return None
    ds = xr.open_dataset(fp)
    var = "LC_Mask_1to10_12" if "LC_Mask_1to10_12" in ds.data_vars else \
          next(iter(ds.data_vars))
    mk = ds[var]
    mk = _std_latlon(mk)
    mk = _to_lon0360(mk)
    return xr.where(np.isfinite(mk) & (mk == 1), 1, np.nan)

def _align_like(da: xr.DataArray, ref: xr.DataArray):
    # 坐标若完全一致就返回自身；否则用最近邻对齐，避免 reindex 造 NaN
    try:
        if np.allclose(da.lat, ref.lat) and np.allclose(da.lon, ref.lon):
            return da
    except Exception:
        pass
    return da.interp_like(ref, method="nearest")

# —— 核心：计算单月掩膜均值，返回(均值, 有效像元数, 状态)
def _masked_month_mean(year: int, month: int, patterns, hints, value_filter, mask: xr.DataArray):
    fp = _find_existing(patterns, year, month)
    if fp is None:
        return None, 0, "missing_file"
    with xr.open_dataset(fp) as ds:
        da = _pick_var(ds, hints=hints)
        da = _std_latlon(da)
        da = _to_lon0360(da)
        if mask is not None:
            da = _align_like(da, mask).where(mask == 1)
        if value_filter is not None:
            da = da.where(value_filter(da))
        n_valid = int(np.isfinite(da).sum().item())
        mean_v = float(da.mean(skipna=True).item()) if n_valid > 0 else np.nan
        status = "ok" if n_valid > 0 else "all_nan_after_mask_or_filter"
        return mean_v, n_valid, status

# ========= ONI：3月滑动窗口展开到月份 =========
oni_df = pd.read_csv(oni_path)
oni_df = oni_df.melt(id_vars=['Year'], var_name='Season', value_name='ONI')
season_to_months = {
    'DJF':[12,1,2],'JFM':[1,2,3],'FMA':[2,3,4],'MAM':[3,4,5],
    'AMJ':[4,5,6],'MJJ':[5,6,7],'JJA':[6,7,8],'JAS':[7,8,9],
    'ASO':[8,9,10],'SON':[9,10,11],'OND':[10,11,12],'NDJ':[11,12,1],
}
oni_monthly=[]
for _,r in oni_df.iterrows():
    y=int(r['Year']); v=float(r['ONI']); s=r['Season']
    for m in season_to_months[s]:
        yy=y
        if s in ['DJF','NDJ'] and m==12: yy=y-1
        oni_monthly.append({'Year':yy,'Month':m,'ONI':v})
oni_monthly_df=(pd.DataFrame(oni_monthly)
                .drop_duplicates(['Year','Month'])
                .sort_values(['Year','Month']))
oni_monthly_df["Date"]=pd.to_datetime(oni_monthly_df[['Year','Month']].assign(DAY=1))

# ========= 遍历月份 =========
recs=[]
for year in range(2014, 2021):
    mask_year = _open_mask(year)
    for month in range(1, 13):
        # SIF：只要求非负
        sif_mean,  sif_n,  sif_status  = _masked_month_mean(
            year, month, GOME2_SIF_PATTERNS, hints=("sif",), value_filter=lambda d: d>=0, mask=mask_year
        )
        # φF：限制在 0–0.05（按你的口径）
        phif_mean, phif_n, phif_status = _masked_month_mean(
            year, month, GOME2_PHIF_PATTERNS, hints=("phif","phi"), value_filter=lambda d: (d>=0)&(d<=0.05), mask=mask_year
        )

        # 诊断输出（断线定位）
        tag=f"{year}-{month:02d}"
        if sif_mean is None: print(f"[{tag}] SIF : 文件缺失")
        elif np.isnan(sif_mean): print(f"[{tag}] SIF : 有效像元=0 → 掩膜/对齐/阈值导致全 NaN")
        if phif_mean is None: print(f"[{tag}] φF  : 文件缺失")
        elif np.isnan(phif_mean): print(f"[{tag}] φF  : 有效像元=0 → 掩膜/对齐/阈值导致全 NaN")

        if (sif_mean is None) and (phif_mean is None):
            continue

        date = pd.to_datetime(f"{year}-{month:02d}-01")
        oni_val = oni_monthly_df.loc[oni_monthly_df["Date"]==date, "ONI"]
        oni_val = float(oni_val.values[0]) if not oni_val.empty else np.nan

        recs.append({
            "Date": date,
            "SIF_mean":  (sif_mean  if sif_mean  is not None else np.nan),
            "phiF_mean": (phif_mean*100 if (phif_mean is not None and not np.isnan(phif_mean)) else np.nan),
            "ONI": oni_val
        })

df = pd.DataFrame(recs).sort_values("Date")
if LIMIT_RANGE:
    df = df[(df["Date"]>=RANGE_START) & (df["Date"]<=RANGE_END)]

# ========= 保存与作图 =========
csv_out = out_dir / "GOME2_SIF_phiF_masked_new.csv"
png_out = out_dir / "GOME2_SIF_phiF_timeseries_masked_new.png"
df.to_csv(csv_out, index=False)
print(f"[OK] 保存到: {csv_out}")

# 【仅用于可视化】如想避免断线，可对曲线做插值绘图（CSV 仍保留 NaN）
plot_sif  = df["SIF_mean"].interpolate(limit_direction="both")
plot_phi  = df["phiF_mean"].interpolate(limit_direction="both")

plt.figure(figsize=(14,7))
plt.plot(df["Date"], plot_sif,  label="GOME-2 SIF mean")
plt.plot(df["Date"], plot_phi,  label="GOME-2 φF mean ×100")
plt.plot(df["Date"], df["ONI"], label="ONI (3-mo running mean)")

plt.axhline(0.5,  linestyle="--", label="El Niño threshold (0.5)")
plt.axhline(-0.5, linestyle="--", label="La Niña threshold (-0.5)")
plt.xlabel("Time"); plt.ylabel("Value")
plt.title("GOME-2 SIF & φF (masked by LC 1–10 & 12) vs ONI")
plt.legend(); plt.tight_layout()
plt.savefig(png_out, dpi=300); plt.show()
print(f"[OK] 保存到: {png_out}")
