# gome2_sif_lon0360_match_oco2.py
import re
import xarray as xr
import numpy as np
from pathlib import Path
from tqdm import tqdm
import matplotlib.pyplot as plt

# ========== 配置 ==========
YEARS = range(2014, 2021)                  # 2014–2020
IN_DIR   = Path("../Data/GOME2/final/2018")   # 输入：GOME2 月度 SIF
OUT_DIR  = Path("../Results/GOME2/SIF/GOME2_lon0360")
FIG_DIR  = Path("../Results/GOME2/SIF/GOME2_lon0360")
GLOB_PATTERN = "*{year}*.nc"
SUFFIX = "_lon0360.nc"
VMIN, VMAX = 0.0, 2.5                       # GOME2 色条
CMAP = "YlOrRd"
TITLE_PREFIX = "GOME2 SIF"     # 标题前缀
# =========================

OUT_DIR.mkdir(parents=True, exist_ok=True)
FIG_DIR.mkdir(parents=True, exist_ok=True)

def find_lon_name(ds):
    for k in ["lon","longitude","x","Longitudes","LONGITUDE"]:
        if k in ds.coords or k in ds.variables:
            return k
    for k in ds.coords:
        if "lat" not in k.lower():
            return k
    raise ValueError("找不到经度坐标")

def find_lat_name(ds):
    for k in ["lat","latitude","y","LATITUDE"]:
        if k in ds.coords or k in ds.variables:
            return k
    for k in ds.coords:
        if "lon" not in k.lower():
            return k
    raise ValueError("找不到纬度坐标")

def pick_sif_var(ds):
    cands = [v for v in ds.data_vars if "sif" in v.lower()]
    return cands[0] if cands else list(ds.data_vars)[0]

def to_0360(ds, lon_name=None):
    lon_name = lon_name or find_lon_name(ds)
    lon = np.asarray(ds[lon_name].values)
    if np.nanmin(lon) >= 0 and np.nanmax(lon) <= 360:
        return ds.sortby(lon_name)
    lon_new = (lon % 360 + 360) % 360
    ds = ds.assign_coords({lon_name: lon_new}).sortby(lon_name)
    ds[lon_name].attrs.update(units="degrees_east", long_name="longitude (0-360)")
    return ds

def enc(ds):
    return {v: dict(zlib=True, complevel=4, shuffle=True) for v in ds.data_vars}

def out_nc(p: Path) -> Path:
    return OUT_DIR / f"{p.stem}{SUFFIX}"

def out_png(p: Path) -> Path:
    return FIG_DIR / f"{p.stem}{SUFFIX.replace('.nc','')}.png"

def parse_ym(stem: str):
    m = re.search(r"(20\d{2})[-_]?(\d{2})", stem)
    return (m.group(1), m.group(2)) if m else (None, None)

def plot_map(ds, varname, src: Path, png_out: Path):
    lon = find_lon_name(ds); lat = find_lat_name(ds)
    data = ds[varname]
    y, m = parse_ym(src.stem)
    title = f"{TITLE_PREFIX} - {y}-{m}" if y and m else TITLE_PREFIX

    # —— 与 OCO-2 完全一致的底图样式：仅 coastlines，PlateCarree(central_longitude=180)
    try:
        import cartopy.crs as ccrs
        proj = ccrs.PlateCarree(central_longitude=180)  # 与 OCO-2 相同
        pc   = ccrs.PlateCarree()

        fig = plt.figure(figsize=(12, 6))
        ax = plt.axes(projection=proj)
        ax.set_global()
        ax.coastlines(linewidth=0.5)  # 与 OCO-2 相同的轮廓

        im = ax.pcolormesh(
            ds[lon], ds[lat], data,
            transform=pc, shading="auto",
            vmin=VMIN, vmax=VMAX, cmap=CMAP
        )

        cb = plt.colorbar(im, ax=ax, orientation="vertical", fraction=0.025, pad=0.02)
        cb.set_label("SIF 740 nm")   # 与 OCO-2 脚本一致的色标名

        ax.set_title(title)
        plt.tight_layout()
        fig.savefig(png_out, dpi=200)
        plt.close(fig)
    except Exception as e:
        # 回退方案：不带海岸线
        print(f"[WARN] Cartopy 绘制失败或未安装：{e}")
        fig = plt.figure(figsize=(14,5))
        ax = plt.gca()
        data.plot(ax=ax, vmin=VMIN, vmax=VMAX, cmap=CMAP, add_colorbar=True)
        ax.set_title(title)
        plt.tight_layout()
        fig.savefig(png_out, dpi=200)
        plt.close(fig)

def process_one(p: Path):
    with xr.open_dataset(p, decode_times=False) as ds:
        ds2 = to_0360(ds)
        varname = pick_sif_var(ds2)
        nc_out = out_nc(p); png_out = out_png(p)
        if not nc_out.exists():
            ds2.to_netcdf(nc_out, encoding=enc(ds2))
        plot_map(ds2, varname, p, png_out)

def main():
    files = []
    for y in YEARS:
        files += sorted(IN_DIR.glob(GLOB_PATTERN.format(year=y)))
    if not files:
        raise SystemExit("没找到文件，检查 IN_DIR 与 GLOB_PATTERN。")
    for f in tqdm(files, desc="GOME2 -> 0–360 & PNG (match OCO-2 coastline)"):
        try:
            process_one(f)
        except Exception as e:
            print(f"[ERROR] {f.name}: {e}")
    print(f"\n完成：\n  NetCDF -> {OUT_DIR.resolve()}\n  PNG    -> {FIG_DIR.resolve()}")

if __name__ == "__main__":
    main()
