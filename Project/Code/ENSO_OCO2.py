# ENSO_OCO2_masked_new.py
import pandas as pd
import xarray as xr
import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt

# ========= 路径与文件模板 =========
oni_path = Path("../Data/ONI.csv")

# —— OCO-2 SIF：优先使用你新生成的 0–360 月度单文件（已 a/b 合并）
SIF_CANDIDATES = [
    "../Results/SIF_lon0360/sif_ann_{YYYY}{MM}_ab_land_lon0360.nc"
]

# —— OCO-2 φF：你当前的新产物（每月一个文件）
PHIF_PATTERN = "../Results/fesc_OCO2/fesc_phiF_{YYYY}_{MM}_vza5.nc"

# —— 年度掩膜（LC 1–10 & 12）
MASK_PATTERN = "../Data/landcover/mask/landcover_{YYYY}_1deg_mask_1to10_12.nc"

# 输出
out_dir = Path("../Data/ENSO/ONI")
out_dir.mkdir(parents=True, exist_ok=True)

# 限定时段（与论文口径一致）
LIMIT_RANGE = True
RANGE_START = "2014-09-01"
RANGE_END   = "2020-04-30"

# ========= 工具函数 =========
def _find_existing(patterns, YYYY, MM) -> Path:
    for pat in patterns:
        p = Path(pat.format(YYYY=YYYY, MM=f"{MM:02d}"))
        if p.exists():
            return p
    return None

def _standardize_lat_lon(da: xr.DataArray) -> xr.DataArray:
    # 统一经纬维/坐标名
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

def _to_lon0360_sorted(da: xr.DataArray) -> xr.DataArray:
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

def _open_mask(year: int) -> xr.DataArray:
    fp = Path(MASK_PATTERN.format(YYYY=year))
    if not fp.exists():
        return None
    ds = xr.open_dataset(fp)
    v = "LC_Mask_1to10_12" if "LC_Mask_1to10_12" in ds.data_vars else list(ds.data_vars)[0]
    mk = ds[v]
    # 标准化经纬与经度 0–360
    mk = _standardize_lat_lon(mk)
    mk = _to_lon0360_sorted(mk)
    # 掩膜为1时有效
    mk = xr.where(np.isfinite(mk) & (mk == 1), 1, np.nan)
    return mk

def _align_like(da: xr.DataArray, ref: xr.DataArray):
    # 坐标名已标准化后再对齐网格；先尝试严格索引对齐，失败则最近邻插值
    try:
        return da.reindex_like(ref, method=None)
    except Exception:
        return da.interp_like(ref, method="nearest")

def _open_month_mean_sif(year: int, month: int, mask: xr.DataArray):
    fp = _find_existing(SIF_CANDIDATES, year, month)
    if fp is None:
        return None
    with xr.open_dataset(fp) as ds:
        da = _pick_var(ds, hints=("sif","sif_ann"))
        da = _standardize_lat_lon(da)
        da = _to_lon0360_sorted(da)
        if mask is not None:
            da = _align_like(da, mask).where(mask == 1)
        da = da.where(da >= 0)  # SIF 非负
        return float(da.mean(skipna=True).item())

def _open_month_mean_phif(year: int, month: int, mask: xr.DataArray):
    fp = Path(PHIF_PATTERN.format(YYYY=year, MM=f"{month:02d}"))
    if not fp.exists():
        return None
    with xr.open_dataset(fp) as ds:
        da = _pick_var(ds, hints=("phif","phi"))
        da = _standardize_lat_lon(da)
        da = _to_lon0360_sorted(da)
        if mask is not None:
            da = _align_like(da, mask).where(mask == 1)
        da = da.where((da >= 0.0) & (da <= 0.05))  # 合理范围
        return float(da.mean(skipna=True).item())

# ========= ONI：从季节到月份 =========
oni_df = pd.read_csv(oni_path)
oni_df = oni_df.melt(id_vars=['Year'], var_name='Season', value_name='ONI')
season_to_months = {
    'DJF':[12,1,2],'JFM':[1,2,3],'FMA':[2,3,4],'MAM':[3,4,5],
    'AMJ':[4,5,6],'MJJ':[5,6,7],'JJA':[6,7,8],'JAS':[7,8,9],
    'ASO':[8,9,10],'SON':[9,10,11],'OND':[10,11,12],'NDJ':[11,12,1]
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

# ========= 遍历月份，计算掩膜均值 =========
recs=[]
for year in range(2014, 2021):
    mask_year = _open_mask(year)
    for month in range(1, 13):
        sif_mean  = _open_month_mean_sif(year, month, mask_year)
        phif_mean = _open_month_mean_phif(year, month, mask_year)
        if sif_mean is None and phif_mean is None:
            continue
        date = pd.to_datetime(f"{year}-{month:02d}-01")
        oni_val = oni_monthly_df.loc[oni_monthly_df["Date"]==date, "ONI"]
        oni_val = float(oni_val.values[0]) if not oni_val.empty else np.nan
        recs.append({"Date":date, "SIF_mean":sif_mean, "phiF_mean":phif_mean*100 if phif_mean is not None else np.nan,
                     "ONI":oni_val})

df = pd.DataFrame(recs).sort_values("Date")
if LIMIT_RANGE:
    df = df[(df["Date"]>=RANGE_START) & (df["Date"]<=RANGE_END)]

# ========= 保存与作图 =========
csv_out = out_dir / "OCO2_SIF_phiF_masked_new.csv"
png_out = out_dir / "OCO2_SIF_phiF_timeseries_masked_new.png"
df.to_csv(csv_out, index=False)
print(f"[OK] 保存到: {csv_out}")

plt.figure(figsize=(14,7))
plt.plot(df["Date"], df["SIF_mean"],  label="OCO-2 SIF mean")
plt.plot(df["Date"], df["phiF_mean"], label="OCO-2 φF mean ×100")
plt.plot(df["Date"], df["ONI"],       label="ONI (3-mo running mean)")
plt.axhline(0.5,  linestyle="--", label="El Niño threshold (0.5)")
plt.axhline(-0.5, linestyle="--", label="La Niña threshold (-0.5)")
plt.xlabel("Time"); plt.ylabel("Value")
plt.title("OCO-2 SIF & φF (masked by LC 1–10 & 12) vs ONI")
plt.legend(); plt.tight_layout()
plt.savefig(png_out, dpi=300)
plt.show()
print(f"[OK] 保存到: {png_out}")
