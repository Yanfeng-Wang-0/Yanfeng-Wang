# ENSO_spatial_v3.py
import pandas as pd
import numpy as np
import xarray as xr
from pathlib import Path
import matplotlib.pyplot as plt

# ===================== 配置 =====================
ONI_CSV       = Path("../Data/ONI.csv")
OCO2_SIF_DIR  = Path("../Data/SIF_final")       # OCO-2 SIF (a,b)
OCO2_PHIF_DIR = Path("../Results/PhiF")         # OCO-2 phiF (a,b)
GOME2_SIF_DIR = Path("../Data/GOME2/final")     # GOME-2 SIF (单月)
GOME2_PHIF_DIR= Path("../Results/GOME2/phiF")   # GOME-2 phiF (多为 a)
MASK_DIR      = Path("../Data/landcover/mask")
OUT_DIR       = Path("../Data/ENSO/ENSO_spatial")
OUT_DIR.mkdir(parents=True, exist_ok=True)

START_YM = "2014-09"
END_YM   = "2020-07"

STRONG_EN_THRESHOLD = 1.5
NEUTRAL_LOW, NEUTRAL_HIGH = -0.5, 0.5
PHIF_SCALE_FOR_PLOT = 100.0   # φF 展示缩放

# ===================== 工具函数 =====================
def oni_to_months(oni_csv):
    seas = ['DJF','JFM','FMA','MAM','AMJ','MJJ','JJA','JAS','ASO','SON','OND','NDJ']
    df = pd.read_csv(oni_csv)[['Year'] + seas]
    long = df.melt(id_vars='Year', var_name='Season', value_name='ONI')
    center = {'DJF':1,'JFM':2,'FMA':3,'MAM':4,'AMJ':5,'MJJ':6,'JJA':7,'JAS':8,'ASO':9,'SON':10,'OND':11,'NDJ':12}
    rows = []
    for _, r in long.iterrows():
        y = int(r['Year']); m = center[r['Season']]
        rows.append({'Year': y, 'Month': m, 'YM': f"{y:04d}-{m:02d}", 'ONI': float(r['ONI'])})
    mon = pd.DataFrame(rows).sort_values(['Year','Month']).reset_index(drop=True)
    return mon[(mon['YM'] >= START_YM) & (mon['YM'] <= END_YM)]

def load_year_mask(year:int):
    f = MASK_DIR / f"landcover_{year}_1deg_mask_1to10.nc"
    if not f.exists(): return None
    with xr.open_dataset(f) as ds:
        v = list(ds.data_vars)[0]
        da = ds[v].load()
    mask = xr.where(np.isfinite(da) & (da > 0), 1, np.nan)
    rename = {}
    for cand, std in [('latitude','lat'),('Latitude','lat'),('y','lat'),
                      ('longitude','lon'),('Longitude','lon'),('x','lon')]:
        if cand in mask.coords and std not in mask.coords: rename[cand]=std
    if rename: mask = mask.rename(rename)
    return mask

def align_like(da:xr.DataArray, ref:xr.DataArray):
    if da is None: return None
    rename = {}
    for cand, std in [('latitude','lat'),('Latitude','lat'),('y','lat'),
                      ('longitude','lon'),('Longitude','lon'),('x','lon')]:
        if cand in da.coords and std not in da.coords: rename[cand]=std
    if rename: da = da.rename(rename)
    if 'lat' in da.coords and 'lat' in ref.coords:
        if (da.lat[0] > da.lat[-1]) and (ref.lat[0] < ref.lat[-1]): da = da.sortby('lat')
        if (da.lat[0] < da.lat[-1]) and (ref.lat[0] > ref.lat[-1]): da = da.sortby('lat', ascending=False)
    try:
        da = da.reindex_like(ref, method=None)
    except Exception:
        da = da.interp_like(ref, method="nearest")
    return da

def open_masked_da(nc:Path, mask:xr.DataArray):
    if not nc.exists(): return None
    ds = xr.open_dataset(nc)
    var = list(ds.data_vars)[0]
    da = ds[var]
    if mask is not None:
        da = align_like(da, mask).where(mask==1)
    return da

def average_ab(da_list):
    das = [d for d in da_list if d is not None]
    if not das: return None
    base = das[0]
    if len(das) > 1:
        aligned = [base] + [d.interp_like(base, method="nearest") for d in das[1:]]
        return xr.concat(aligned, dim="src").mean("src", skipna=True)
    return base

def month_da(product:str, varname:str, year:int, month:int):
    mask = load_year_mask(year)
    if product=="OCO2" and varname=="SIF":
        da = average_ab([
            open_masked_da(OCO2_SIF_DIR/f"{year}"/f"sif_ann_{year}{month:02d}a_land.nc", mask),
            open_masked_da(OCO2_SIF_DIR/f"{year}"/f"sif_ann_{year}{month:02d}b_land.nc", mask)
        ])
        return da
    if product=="OCO2" and varname=="phiF":
        da = average_ab([
            open_masked_da(OCO2_PHIF_DIR/f"{year}"/f"PhiF_{year}_{month:02d}_a.nc", mask),
            open_masked_da(OCO2_PHIF_DIR/f"{year}"/f"PhiF_{year}_{month:02d}_b.nc", mask)
        ])
        return None if da is None else da*PHIF_SCALE_FOR_PLOT
    if product=="GOME2" and varname=="SIF":
        return open_masked_da(GOME2_SIF_DIR/f"{year}"/f"GOME2B_SIF_{year}_{month:02d}_land.nc", mask)
    if product=="GOME2" and varname=="phiF":
        da = average_ab([
            open_masked_da(GOME2_PHIF_DIR/f"{year}"/f"PhiF_{year}_{month:02d}_a.nc", mask),
            open_masked_da(GOME2_PHIF_DIR/f"{year}"/f"PhiF_{year}_{month:02d}_b.nc", mask)
        ])
        return None if da is None else da*PHIF_SCALE_FOR_PLOT
    return None

def period_mean(product:str, varname:str, ym_list:list):
    das=[]
    for ym in ym_list:
        y,m = map(int, ym.split("-"))
        da = month_da(product,varname,y,m)
        if da is not None: das.append(da)
    if not das: return None
    base=das[0]
    if len(das)>1:
        aligned=[base]+[d.interp_like(base, method="nearest") for d in das[1:]]
        return xr.concat(aligned, dim="time").mean("time", skipna=True)
    return base

def robust_limits(arrays, q=0.995, fallback=1.0):
    arrays=[a for a in arrays if a is not None]
    if not arrays: return -fallback, fallback
    vals=np.concatenate([a.values.ravel() for a in arrays])
    vals=vals[np.isfinite(vals)]
    if vals.size==0: return -fallback, fallback
    vmax=float(np.quantile(np.abs(vals), q))
    vmax=max(vmax,1e-12)
    return -vmax, vmax

# ===================== 计算 ENSO 月份清单 =====================
oni_mon = oni_to_months(ONI_CSV)
elnino_months = oni_mon[oni_mon['ONI'] >= STRONG_EN_THRESHOLD]['YM'].tolist()
neutral_months = oni_mon[(oni_mon['ONI'] > NEUTRAL_LOW) & (oni_mon['ONI'] < NEUTRAL_HIGH)]['YM'].tolist()
print(f"[INFO] Strong El Niño months: {len(elnino_months)}; Neutral months: {len(neutral_months)}")

# ===================== 期均与异常 =====================
results = {}
for var in ["SIF","phiF"]:
    for prod in ["OCO2","GOME2"]:
        en = period_mean(prod,var,elnino_months)
        nt = period_mean(prod,var,neutral_months)
        if (en is None) or (nt is None):
            print(f"[WARN] 缺少数据：{prod} {var}")
            continue
        results[(prod,var)]={"en":en,"nt":nt,"anom":en-nt}
        # 可选：另存 NetCDF
        results[(prod,var)]["en"].to_netcdf(OUT_DIR/f"{prod}_{var}_ElNino_mean.nc")
        results[(prod,var)]["nt"].to_netcdf(OUT_DIR/f"{prod}_{var}_Neutral_mean.nc")
        results[(prod,var)]["anom"].to_netcdf(OUT_DIR/f"{prod}_{var}_Anomaly.nc")

# ---------- 计算色标范围 & 提取变量 ----------
sif_left  = results.get(("OCO2","SIF"),{}).get("anom")
sif_right = results.get(("GOME2","SIF"),{}).get("anom")
ph_left   = results.get(("OCO2","phiF"),{}).get("anom")
ph_right  = results.get(("GOME2","phiF"),{}).get("anom")

sif_vmin, sif_vmax = robust_limits([sif_left, sif_right], q=0.995, fallback=1.0)
ph_vmin,  ph_vmax  = robust_limits([ph_left, ph_right], q=0.995, fallback=1.0)

# ===================== 画 1×2 地图（色条独立列）函数 =====================
def plot_pair_with_cbar(left_da, right_da, vmin, vmax,
                        left_title, right_title, cbar_label, out_png):
    """
    1×2 面板 + 独立色条列（不遮挡右图）
    """
    from matplotlib import gridspec
    fig = plt.figure(figsize=(12, 4.8))
    gs = gridspec.GridSpec(nrows=1, ncols=3, width_ratios=[1.0, 1.0, 0.04], wspace=0.12)

    axL = fig.add_subplot(gs[0, 0])
    axR = fig.add_subplot(gs[0, 1])
    cax = fig.add_subplot(gs[0, 2])

    im_ref = None
    if left_da is not None:
        im_ref = left_da.plot(ax=axL, cmap="RdBu_r", vmin=vmin, vmax=vmax, add_colorbar=False)
        axL.set_title(left_title)
    else:
        axL.set_visible(False)

    if right_da is not None:
        im = right_da.plot(ax=axR, cmap="RdBu_r", vmin=vmin, vmax=vmax, add_colorbar=False)
        axR.set_title(right_title)
        if im_ref is None:
            im_ref = im
    else:
        axR.set_visible(False)

    if im_ref is not None:
        cb = fig.colorbar(im_ref, cax=cax)
        cb.set_label(cbar_label)

    fig.savefig(out_png, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"[OK] 保存: {out_png}")

# ===================== 画 SIF 1×2 =====================
plot_pair_with_cbar(
    left_da=sif_left,
    right_da=sif_right,
    vmin=sif_vmin, vmax=sif_vmax,
    left_title="OCO2 SIF anomaly (El Niño − Neutral)",
    right_title="GOME2 SIF anomaly (El Niño − Neutral)",
    cbar_label="SIF anomaly",
    out_png=OUT_DIR/"ENSO_anomaly_SIF_1x2.png"
)

# ===================== 画 φF 1×2 =====================
plot_pair_with_cbar(
    left_da=ph_left,
    right_da=ph_right,
    vmin=ph_vmin, vmax=ph_vmax,
    left_title="OCO2 φF anomaly (El Niño − Neutral)",
    right_title="GOME2 φF anomaly (El Niño − Neutral)",
    cbar_label="φF anomaly (*100)",
    out_png=OUT_DIR/"ENSO_anomaly_phiF_1x2.png"
)

# ===================== 纬度剖面（两张） =====================
# SIF
plt.figure(figsize=(7,4.2))
if sif_left  is not None:  sif_left.mean(dim="lon").plot(label="OCO2 SIF")
if sif_right is not None:  sif_right.mean(dim="lon").plot(label="GOME2 SIF")
plt.legend(); plt.xlabel("Latitude"); plt.ylabel("Anomaly")
plt.title("Latitude profiles: SIF anomaly (El Niño − Neutral)")
plt.tight_layout()
plt.savefig(OUT_DIR/"ENSO_anomaly_latprof_SIF.png", dpi=300)
plt.close()

# φF
plt.figure(figsize=(7,4.2))
if ph_left  is not None:  ph_left.mean(dim="lon").plot(label="OCO2 φF")
if ph_right is not None:  ph_right.mean(dim="lon").plot(label="GOME2 φF")
plt.legend(); plt.xlabel("Latitude"); plt.ylabel("Anomaly")
plt.title("Latitude profiles: φF anomaly (El Niño − Neutral)")
plt.tight_layout()
plt.savefig(OUT_DIR/"ENSO_anomaly_latprof_phiF.png", dpi=300)
plt.close()

print("[DONE] All figures saved.")
