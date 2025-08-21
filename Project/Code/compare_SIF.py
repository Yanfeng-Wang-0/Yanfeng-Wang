# compare_sif_oco2_gome2_lon0360_outline.py
import os
from pathlib import Path
import numpy as np
import xarray as xr
import pandas as pd
import matplotlib.pyplot as plt

# ========= 配置 =========
# 要比较的月份
MONTHS = ["2015-11", "2019-11"]

# 你“最新生成”的 lon0360 文件路径模板（按需把真实的放在最前）
OCO2_CANDIDATES = [
    "../Results/SIF_lon0360/sif_ann_{YYYY}{MM}_ab_land_lon0360.nc",
]
GOME2_CANDIDATES = [
    "../Results/GOME2/SIF/GOME2_lon0360/GOME2B_SIF_{YYYY}_{MM}_land_lon0360.nc",
]

# 变量名与单位
SIF_VAR_HINTS = ["sif", "sif_ann"]
SCALE_OCO2  = 1.0
SCALE_GOME2 = 1.0   # 若你的 GOME-2 已统一单位，请改为 1.0

OUTDIR = Path("../Results/Plot/analysis2")
OUTDIR.mkdir(parents=True, exist_ok=True)
# =======================


# ---------- 工具 ----------
def find_existing(patterns, YYYY, MM) -> Path:
    for pat in patterns:
        p = Path(pat.format(YYYY=YYYY, MM=MM))
        if p.exists():
            return p
    raise FileNotFoundError(f"找不到匹配文件（{YYYY}-{MM}）：{patterns}")

def pick_sif_var(ds: xr.Dataset) -> xr.DataArray:
    for hint in SIF_VAR_HINTS:
        for v in ds.data_vars:
            if hint.lower() in v.lower() and np.issubdtype(ds[v].dtype, np.number):
                return ds[v]
    nums = [v for v in ds.data_vars if np.issubdtype(ds[v].dtype, np.number)]
    if not nums:
        raise ValueError(f"无数值变量：{list(ds.data_vars)}")
    return ds[nums[0]]

def standardize_lat_lon(da: xr.DataArray) -> xr.DataArray:
    # 统一经纬度名字
    lat = next((d for d in da.dims if d.lower() in ("lat","latitude","y")), None)
    lon = next((d for d in da.dims if d.lower() in ("lon","longitude","x")), None)
    if lat != "lat":
        da = da.rename({lat: "lat"})
    if lon != "lon":
        da = da.rename({lon: "lon"})
    return da

def to_lon0360_sorted(da: xr.DataArray) -> xr.DataArray:
    lon_new = (da.lon % 360 + 360) % 360
    da = da.assign_coords(lon=lon_new).sortby("lon")
    da.lon.attrs.update(units="degrees_east", long_name="longitude (0-360)")
    return da

def open_month(product: str, ym: str) -> xr.DataArray:
    y, m = ym.split("-")
    if product == "oco2":
        path = find_existing(OCO2_CANDIDATES, y, m)
        scale = SCALE_OCO2
    else:
        path = find_existing(GOME2_CANDIDATES, y, m)
        scale = SCALE_GOME2
    ds = xr.open_dataset(path)
    da = pick_sif_var(ds).astype("float32") * scale
    da = standardize_lat_lon(da)
    da = to_lon0360_sorted(da)  # 统一 0–360
    return da

def maybe_regrid_to(ref: xr.DataArray, tgt: xr.DataArray) -> xr.DataArray:
    same = (
        ref.sizes["lat"] == tgt.sizes["lat"] and
        ref.sizes["lon"] == tgt.sizes["lon"] and
        np.allclose(ref.lat.values, tgt.lat.values) and
        np.allclose(ref.lon.values, tgt.lon.values)
    )
    if same:
        return tgt
    # 如需重网格，打开以下注释（需安装 xesmf）
    # import xesmf as xe
    # regridder = xe.Regridder(tgt.to_dataset(name="v"), ref.to_dataset(name="v"),
    #                          method="bilinear", reuse_weights=True)
    # return regridder(tgt)
    raise ValueError("两数据网格不同：请先统一网格或启用 xESMF。")

def quick_stats(x, y):
    m = np.isfinite(x) & np.isfinite(y)
    if m.sum() == 0:
        return dict(n=0, bias=np.nan, rmse=np.nan, r2=np.nan)
    dx = y[m] - x[m]
    bias = float(np.mean(dx))
    rmse = float(np.sqrt(np.mean(dx**2)))
    r = np.corrcoef(x[m], y[m])[0,1] if m.sum()>1 else np.nan
    return dict(n=int(m.sum()), bias=bias, rmse=rmse, r2=float(r**2) if np.isfinite(r) else np.nan)

def save_fig(fig, out):
    fig.tight_layout()
    fig.savefig(out, dpi=300)
    plt.close(fig)
# -----------------------


# ========== 主流程 ==========
records = []
for ym in MONTHS:
    print(f"\n==> {ym}")
    oco2  = open_month("oco2", ym)
    gome2 = open_month("gome2", ym)
    gome2 = maybe_regrid_to(oco2, gome2)

    # 只保留正值
    oco2  = oco2.where(oco2  > 0)
    gome2 = gome2.where(gome2 > 0)

    diff = oco2 - gome2
    S = quick_stats(gome2.values.ravel(), oco2.values.ravel())
    S["month"] = ym
    records.append(S)

    # ---------- 图1：差值图（带陆地轮廓，0–360） ----------
    vlim = float(np.nanpercentile(np.abs(diff.values), 98)) if np.isfinite(diff).any() else 1.0
    try:
        import cartopy.crs as ccrs
        import cartopy.feature as cfeature

        proj = ccrs.PlateCarree(central_longitude=180)  # 适配 0–360
        pc   = ccrs.PlateCarree()

        fig = plt.figure(figsize=(10.5, 4.6))
        ax  = plt.axes(projection=proj)
        ax.set_global()
        ax.set_facecolor("white")

        im = ax.pcolormesh(diff.lon, diff.lat, diff, transform=pc,
                           shading="auto", vmin=-vlim, vmax=vlim, cmap="RdBu_r", zorder=2)

        # —— 陆地轮廓（只描边）
        ax.add_feature(cfeature.LAND, facecolor="none", edgecolor="black",
                       linewidth=0.6, zorder=5)
        ax.add_feature(cfeature.COASTLINE, linewidth=0.6, edgecolor="black", zorder=5)
        ax.add_feature(cfeature.BORDERS, linewidth=0.3, edgecolor="black", alpha=0.6, zorder=5)

        cb = plt.colorbar(im, ax=ax, shrink=0.9, pad=0.03)
        cb.set_label("ΔSIF (OCO-2 − GOME-2)")

        ax.set_title(f"ΔSIF (OCO-2 − GOME-2): {ym}")
        plt.tight_layout()
        save_fig(fig, OUTDIR / f"diff_{ym}_lon0360_outline.png")

    except Exception as e:
        # 回退：无 Cartopy 时仍输出图（不带轮廓）
        print(f"[WARN] Cartopy 绘制失败或未安装：{e}")
        fig, ax = plt.subplots(figsize=(9,4))
        im = ax.pcolormesh(diff.lon, diff.lat, diff, shading="auto", cmap="RdBu_r")
        im.set_clim(-vlim, vlim)
        cb = fig.colorbar(im, ax=ax, shrink=0.85, label="ΔSIF (OCO-2 − GOME-2)")
        ax.set_title(f"ΔSIF (OCO-2 − GOME-2): {ym}  [lon 0–360]")
        ax.set_xlabel("Longitude (°E)"); ax.set_ylabel("Latitude (°)")
        ax.set_xlim(0, 360)
        save_fig(fig, OUTDIR / f"diff_{ym}_lon0360.png")

    # ---------- 图2：散点 ----------
    fig2, ax2 = plt.subplots(figsize=(4.8,4.8))
    x = gome2.values.ravel(); y = oco2.values.ravel()
    m = np.isfinite(x) & np.isfinite(y)
    ax2.scatter(x[m], y[m], s=3, alpha=0.3)
    mn = float(np.nanmin([x[m].min(), y[m].min()])) if m.any() else 0
    mx = float(np.nanmax([x[m].max(), y[m].max()])) if m.any() else 1
    ax2.plot([mn, mx], [mn, mx], "r--", lw=1)
    ax2.set_xlabel("GOME-2 SIF"); ax2.set_ylabel("OCO-2 SIF")
    ax2.set_title(f"{ym}\nN={S['n']}  bias={S['bias']:.3f}  RMSE={S['rmse']:.3f}  R²={S['r2']:.3f}")
    save_fig(fig2, OUTDIR / f"scatter_{ym}_lon0360.png")

    # ---------- 图3：纬度带平均 ----------
    fig3, ax3 = plt.subplots(figsize=(6.2,3.8))
    ax3.plot(gome2.lat, gome2.mean("lon"), label="GOME-2")
    ax3.plot(oco2.lat,  oco2.mean("lon"),  label="OCO-2")
    ax3.set_xlabel("Latitude (°)"); ax3.set_ylabel("SIF")
    ax3.set_title(f"Zonal Mean SIF  {ym}")
    ax3.legend()
    save_fig(fig3, OUTDIR / f"zonal_mean_{ym}_lon0360.png")

    # ---------- 图4：误差直方图 ----------
    fig4, ax4 = plt.subplots(figsize=(5.2,3.6))
    ax4.hist((y[m]-x[m]), bins=60)
    ax4.set_xlabel("ΔSIF = OCO-2 − GOME-2")
    ax4.set_ylabel("Count")
    ax4.set_title(f"Error Histogram  {ym}")
    save_fig(fig4, OUTDIR / f"hist_{ym}_lon0360.png")

# 汇总表
pd.DataFrame(records)[["month","n","bias","rmse","r2"]].to_csv(OUTDIR/"summary_stats.csv", index=False)
print("✅ 完成。输出：", OUTDIR.resolve())
