# compare_phif_oco2_gome2_lon0360_outline.py
import numpy as np
import xarray as xr
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# ========= 配置 =========
# 想批量跑全年可用：MONTHS = [f"{y}-{m:02d}" for y in range(2014, 2021) for m in range(1,13)]
MONTHS = ["2015-11", "2019-11"]

# 你“最新生成”的 φF 月度单文件（优先使用 *_lon0360.nc；找不到再回退旧路径）
OCO2_CANDIDATES = [
    "../Results/fesc_OCO2/fesc_phiF_{YYYY}_{MM}_vza5.nc",
]
GOME2_CANDIDATES = [
    "../Results/fesc_GOME2/fesc_phiF_{YYYY}_{MM}_vzaAll.nc",
]

# φF 变量名自动匹配关键字（从前到后优先）
PHIF_VAR_HINTS = ["phif", "phi_f", "phi"]

# φF 无单位，通常不需要缩放
SCALE = {"oco2": 1.0, "gome2": 1.0}

# 输出目录
OUTDIR = Path("../Results/Plot/analysis3")
OUTDIR.mkdir(parents=True, exist_ok=True)
# =======================


# ---------- 工具 ----------
def _find_existing(patterns, YYYY, MM) -> Path:
    for pat in patterns:
        p = Path(pat.format(YYYY=YYYY, MM=MM))
        if p.exists():
            return p
    raise FileNotFoundError(f"找不到匹配文件（{YYYY}-{MM}）：\n" + "\n".join(patterns))

def _pick_phif_var(ds: xr.Dataset) -> xr.DataArray:
    # 优先匹配含 phif/phi 的数值变量；否则回退第一个数值变量
    for hint in PHIF_VAR_HINTS:
        for v in ds.data_vars:
            if hint.lower() in v.lower() and np.issubdtype(ds[v].dtype, np.number):
                return ds[v]
    nums = [v for v in ds.data_vars if np.issubdtype(ds[v].dtype, np.number)]
    if not nums:
        raise ValueError(f"没有数值型变量：{list(ds.data_vars)}")
    return ds[nums[0]]

def _standardize_lat_lon(da: xr.DataArray) -> xr.DataArray:
    lat = next((d for d in da.dims if d.lower() in ("lat","latitude","y")), None)
    lon = next((d for d in da.dims if d.lower() in ("lon","longitude","x")), None)
    if lat is None:
        lat = next((k for k in da.coords if k.lower() in ("lat","latitude","y")), None)
    if lon is None:
        lon = next((k for k in da.coords if k.lower() in ("lon","longitude","x")), None)
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

def _open_month(product: str, ym: str) -> xr.DataArray:
    y, m = ym.split("-")
    if product == "oco2":
        path = _find_existing(OCO2_CANDIDATES, y, m)
        scale = SCALE["oco2"]
    else:
        path = _find_existing(GOME2_CANDIDATES, y, m)
        scale = SCALE["gome2"]
    ds = xr.open_dataset(path)
    da = _pick_phif_var(ds).astype("float32") * scale
    da = _standardize_lat_lon(da)
    da = _to_lon0360_sorted(da)  # 强制 0–360 经度
    return da

def _ensure_same_grid(ref: xr.DataArray, tgt: xr.DataArray) -> xr.DataArray:
    same = (
        ref.sizes["lat"] == tgt.sizes["lat"] and
        ref.sizes["lon"] == tgt.sizes["lon"] and
        np.allclose(ref.lat.values, tgt.lat.values) and
        np.allclose(ref.lon.values, tgt.lon.values)
    )
    if same:
        return tgt
    # 如需重网格，解开下面注释（需要 pip install xesmf）
    # import xesmf as xe
    # regridder = xe.Regridder(tgt.to_dataset(name="v"), ref.to_dataset(name="v"),
    #                          method="bilinear", reuse_weights=True)
    # return regridder(tgt)
    raise ValueError("两数据网格不同：请先统一网格或启用 xESMF 进行重网格。")

def _quick_stats(x, y):
    m = np.isfinite(x) & np.isfinite(y)
    if m.sum() == 0:
        return dict(n=0, bias=np.nan, rmse=np.nan, r2=np.nan)
    dx = y[m] - x[m]
    bias = float(np.mean(dx))
    rmse = float(np.sqrt(np.mean(dx**2)))
    r = np.corrcoef(x[m], y[m])[0,1] if m.sum()>1 else np.nan
    return dict(n=int(m.sum()), bias=bias, rmse=rmse, r2=float(r**2) if np.isfinite(r) else np.nan)

def _save(fig, out):
    fig.tight_layout()
    fig.savefig(out, dpi=300)
    plt.close(fig)
# -----------------------


# ========== 主流程 ==========
records = []
for ym in MONTHS:
    print(f"\n==> {ym}")
    oco2  = _open_month("oco2", ym)
    gome2 = _open_month("gome2", ym)
    gome2 = _ensure_same_grid(oco2, gome2)

    # φF 合理范围（可按需调整或注释掉）
    oco2  = oco2.where((oco2  >= 0) & (oco2  <= 0.05))
    gome2 = gome2.where((gome2 >= 0) & (gome2 <= 0.05))

    diff = oco2 - gome2
    S = _quick_stats(gome2.values.ravel(), oco2.values.ravel())
    S["month"] = ym
    records.append(S)

    # ---------- 图1：差值图（带陆地轮廓，0–360） ----------
    vlim = float(np.nanpercentile(np.abs(diff.values), 98)) if np.isfinite(diff).any() else 0.01
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

        # —— 陆地轮廓：只描边
        ax.add_feature(cfeature.LAND, facecolor="none", edgecolor="black", linewidth=0.6, zorder=5)
        ax.add_feature(cfeature.COASTLINE, linewidth=0.6, edgecolor="black", zorder=5)
        ax.add_feature(cfeature.BORDERS, linewidth=0.3, edgecolor="black", alpha=0.6, zorder=5)

        cb = plt.colorbar(im, ax=ax, shrink=0.9, pad=0.03)
        cb.set_label("ΔφF (OCO-2 − GOME-2)")

        ax.set_title(f"ΔφF (OCO-2 − GOME-2): {ym}")
        _save(fig, OUTDIR / f"phiF_diff_{ym}_lon0360_outline.png")

    except Exception as e:
        # 回退：无 Cartopy 也能出图（不带轮廓）
        print(f"[WARN] Cartopy 绘制失败或未安装：{e}")
        fig, ax = plt.subplots(figsize=(9,4))
        im = ax.pcolormesh(diff.lon, diff.lat, diff, shading="auto", cmap="RdBu_r")
        im.set_clim(-vlim, vlim)
        cb = fig.colorbar(im, ax=ax, shrink=0.85, label="ΔφF (OCO-2 − GOME-2)")
        ax.set_title(f"ΔφF (OCO-2 − GOME-2): {ym}  [lon 0–360]")
        ax.set_xlabel("Longitude (°E)"); ax.set_ylabel("Latitude (°)")
        ax.set_xlim(0, 360)
        _save(fig, OUTDIR / f"phiF_diff_{ym}_lon0360.png")

    # ---------- 图2：散点 ----------
    fig2, ax2 = plt.subplots(figsize=(4.8,4.8))
    x = gome2.values.ravel(); y = oco2.values.ravel()
    m = np.isfinite(x) & np.isfinite(y)
    ax2.scatter(x[m], y[m], s=3, alpha=0.3)
    mn = float(np.nanmin([x[m].min(), y[m].min()])) if m.any() else 0
    mx = float(np.nanmax([x[m].max(), y[m].max()])) if m.any() else 1
    ax2.plot([mn, mx], [mn, mx], "r--", lw=1)
    ax2.set_xlabel("GOME-2 φF"); ax2.set_ylabel("OCO-2 φF")
    ax2.set_title(f"{ym}\nN={S['n']}  bias={S['bias']:.4f}  RMSE={S['rmse']:.4f}  R²={S['r2']:.3f}")
    _save(fig2, OUTDIR / f"phiF_scatter_{ym}_lon0360.png")

    # ---------- 图3：纬度带平均 ----------
    fig3, ax3 = plt.subplots(figsize=(6.2,3.8))
    ax3.plot(gome2.lat, gome2.mean("lon"), label="GOME-2")
    ax3.plot(oco2.lat,  oco2.mean("lon"),  label="OCO-2")
    ax3.set_xlabel("Latitude (°)"); ax3.set_ylabel("φF")
    ax3.set_title(f"Zonal Mean φF  {ym}")
    ax3.legend()
    _save(fig3, OUTDIR / f"phiF_zonal_{ym}_lon0360.png")

    # ---------- 图4：误差直方图 ----------
    fig4, ax4 = plt.subplots(figsize=(5.2,3.6))
    ax4.hist((y[m]-x[m]), bins=60)
    ax4.set_xlabel("ΔφF = OCO-2 − GOME-2")
    ax4.set_ylabel("Count")
    ax4.set_title(f"Error Histogram φF  {ym}")
    _save(fig4, OUTDIR / f"phiF_hist_{ym}_lon0360.png")

# 汇总统计
pd.DataFrame(records)[["month","n","bias","rmse","r2"]].to_csv(OUTDIR/"phiF_summary_stats.csv", index=False)
print("✅ 完成。输出：", OUTDIR.resolve())
