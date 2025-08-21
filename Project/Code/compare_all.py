# make_multi_year_diff_maps_lon0360_outline.py
import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
from pathlib import Path
from datetime import datetime

# ========= 配置 =========
START_YM = "2014-09"
END_YM   = "2020-07"

# —— 优先使用你“新生成的 0–360 文件”的路径模板（按顺序匹配，最前为首选）
OCO2_SIF_PATTERNS = [
    "../Results/SIF_lon0360/sif_ann_{YYYY}{MM}_ab_land_lon0360.nc",
]
GOME2_SIF_PATTERNS = [
    "../Results/GOME2/SIF/GOME2_lon0360/GOME2B_SIF_{YYYY}_{MM}_land_lon0360.nc",
]

OCO2_PHIF_PATTERNS = [
    # 你当前 φF 单月单文件（如果也另存了 lon0360，可把它放到更前）
    "../Results/fesc_OCO2/fesc_phiF_{YYYY}_{MM}_vza5.nc",
]
GOME2_PHIF_PATTERNS = [
    "../Results/fesc_GOME2/fesc_phiF_{YYYY}_{MM}_vzaAll.nc",
]

# 变量名提示
SIF_VAR_HINTS  = ["sif", "sif_ann"]
PHIF_VAR_HINTS = ["phif", "phi"]

# 单位缩放（很多项目里 GOME-2 SIF 需要 ×1000；若已统一单位，改为 1.0）
SCALE_SIF  = {"oco2": 1.0, "gome2": 1.0}
SCALE_PHIF = {"oco2": 1.0, "gome2": 1.0}

# 输出目录
OUTDIR = Path("../Results/Plot/analysis4")
OUTDIR.mkdir(parents=True, exist_ok=True)
# ======================


# ========= 工具函数 =========
def ym_range(start_ym: str, end_ym: str):
    s = datetime(*map(int, start_ym.split("-")), 1)
    e = datetime(*map(int, end_ym.split("-")), 1)
    cur = s
    while cur <= e:
        yield cur.year, cur.month
        y, m = cur.year, cur.month + 1
        if m == 13: y, m = y + 1, 1
        cur = datetime(y, m, 1)

def _find_existing(patterns, YYYY, MM) -> Path:
    for pat in patterns:
        p = Path(pat.format(YYYY=YYYY, MM=f"{MM:02d}"))
        if p.exists():
            return p
    raise FileNotFoundError(f"找不到文件：{YYYY}-{MM:02d}\n" + "\n".join(patterns))

def _pick_var(ds: xr.Dataset, hints) -> xr.DataArray:
    # 先按关键词挑数值变量，找不到就回退第一个数值变量
    for hint in hints:
        for v in ds.data_vars:
            if hint.lower() in v.lower() and np.issubdtype(ds[v].dtype, np.number):
                return ds[v]
    nums = [v for v in ds.data_vars if np.issubdtype(ds[v].dtype, np.number)]
    if not nums:
        raise ValueError(f"没有数值型变量：{list(ds.data_vars)}")
    return ds[nums[0]]

def _standardize_lat_lon(da: xr.DataArray) -> xr.DataArray:
    # 统一经纬度命名
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
    # 强制经度到 [0,360)，并排序
    lon_new = (da.lon % 360 + 360) % 360
    da = da.assign_coords(lon=lon_new).sortby("lon")
    da.lon.attrs.update(units="degrees_east", long_name="longitude (0-360)")
    return da

def _open_month(patterns, y, m, hints, scale) -> xr.DataArray:
    path = _find_existing(patterns, y, m)
    ds = xr.open_dataset(path)
    da = _pick_var(ds, hints).astype("float32") * scale
    da = _standardize_lat_lon(da)
    da = _to_lon0360_sorted(da)   # —— 统一 0–360
    return da

def _concat_period(patterns, hints, scale_map, product: str):
    arrs = []
    for y, m in ym_range(START_YM, END_YM):
        try:
            arrs.append(_open_month(patterns, y, m, hints, scale_map[product]).expand_dims(time=[f"{y}-{m:02d}"]))
        except FileNotFoundError:
            # 某些月份缺文件 → 跳过
            continue
    if not arrs:
        raise RuntimeError(f"该产品在区间内没有找到任何月文件：{patterns}")
    return xr.concat(arrs, dim="time")

def _ensure_same_grid(ref: xr.DataArray, tgt: xr.DataArray) -> xr.DataArray:
    same = (
        ref.sizes["lat"] == tgt.sizes["lat"] and
        ref.sizes["lon"] == tgt.sizes["lon"] and
        np.allclose(ref.lat.values, tgt.lat.values) and
        np.allclose(ref.lon.values, tgt.lon.values)
    )
    if same:
        return tgt
    # 如需重网格，解除注释（需 pip install xesmf）
    # import xesmf as xe
    # regridder = xe.Regridder(tgt.to_dataset(name="v"), ref.to_dataset(name="v"),
    #                          "bilinear", reuse_weights=True)
    # return xr.concat([regridder(tgt.isel(time=i)) for i in range(tgt.sizes["time"])], dim="time")
    raise ValueError("两数据网格不同：请先统一网格或启用 xESMF 重网格。")

def _draw_diff_map(diff_mean: xr.DataArray, label: str, unit: str, outpng: Path):
    vlim = float(np.nanpercentile(np.abs(diff_mean.values), 98)) if np.isfinite(diff_mean).any() else 1.0
    try:
        import cartopy.crs as ccrs
        import cartopy.feature as cfeature

        proj = ccrs.PlateCarree(central_longitude=180)  # 适配 0–360
        pc   = ccrs.PlateCarree()

        fig = plt.figure(figsize=(9, 4))
        ax  = plt.axes(projection=proj)
        ax.set_global(); ax.set_facecolor("white")

        im = ax.pcolormesh(diff_mean.lon, diff_mean.lat, diff_mean,
                           transform=pc, shading="auto", cmap="RdBu_r",
                           vmin=-vlim, vmax=vlim, zorder=2)

        # —— 陆地轮廓（只描边）
        ax.add_feature(cfeature.LAND, facecolor="none", edgecolor="black", linewidth=0.6, zorder=5)
        ax.add_feature(cfeature.COASTLINE, linewidth=0.6, edgecolor="black", zorder=5)
        ax.add_feature(cfeature.BORDERS, linewidth=0.3, edgecolor="black", alpha=0.6, zorder=5)

        cb = plt.colorbar(im, ax=ax, shrink=0.9, pad=0.03)
        cb.set_label(f"Δ{label}")

        ax.set_title(f"Multi-year mean Δ{label} (OCO-2 − GOME-2)\n{START_YM} to {END_YM}")
        fig.savefig(outpng, dpi=300, bbox_inches="tight")
        plt.close(fig)
    except Exception as e:
        # 回退（无 Cartopy 也能出图，但无轮廓）
        print(f"[WARN] Cartopy 绘制失败或未安装：{e}")
        fig, ax = plt.subplots(figsize=(9, 4), constrained_layout=True)
        im = ax.pcolormesh(diff_mean.lon, diff_mean.lat, diff_mean, shading="auto", cmap="RdBu_r")
        im.set_clim(-vlim, vlim)
        cb = fig.colorbar(im, ax=ax, shrink=0.9, label=f"Δ{label} ({unit})")
        ax.set_title(f"Multi-year mean Δ{label} (OCO-2 − GOME-2)\n{START_YM} to {END_YM}")
        ax.set_xlabel("Longitude (°E)"); ax.set_ylabel("Latitude (°)")
        ax.set_xlim(0, 360)
        fig.savefig(outpng, dpi=300, bbox_inches="tight")
        plt.close(fig)

# ========= 主流程 =========
def make_multi_year(label, oco2_patterns, gome2_patterns, hints, scale_map, unit, outname):
    print(f"[{label}] 读取 OCO-2 …")
    oco2_all  = _concat_period(oco2_patterns, hints, scale_map, "oco2")
    print(f"[{label}] 读取 GOME-2 …")
    gome2_all = _concat_period(gome2_patterns, hints, scale_map, "gome2")

    # 网格一致性
    gome2_all = _ensure_same_grid(oco2_all, gome2_all)

    # 多年平均差值（OCO2 − GOME2）
    diff_mean = oco2_all.mean("time") - gome2_all.mean("time")
    _draw_diff_map(diff_mean, label, unit, OUTDIR / outname)
    print("Saved:", OUTDIR / outname)

# —— 生成两张图：φF 与 SIF 的多年平均差值（带陆地轮廓、经度 0–360）
make_multi_year("φF",  OCO2_PHIF_PATTERNS, GOME2_PHIF_PATTERNS, PHIF_VAR_HINTS, SCALE_PHIF,
                "unitless", "multi_year_diff_phiF_lon0360_outline.png")
make_multi_year("SIF", OCO2_SIF_PATTERNS,  GOME2_SIF_PATTERNS,  SIF_VAR_HINTS,  SCALE_SIF,
                "mW m$^{-2}$ sr$^{-1}$ nm$^{-1}$", "multi_year_diff_SIF_lon0360_outline.png")

