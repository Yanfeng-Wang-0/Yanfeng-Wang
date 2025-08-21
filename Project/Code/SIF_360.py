# sif_lon0360_and_plot_batch.py
import re
import xarray as xr
import numpy as np
from pathlib import Path
from tqdm import tqdm
import matplotlib.pyplot as plt

# ==== 可配置区 ====
YEARS = range(2014, 2021)           # 2014–2020
IN_DIR  = Path("../Results/SIF_monthly/2018")   # 输入目录（放原始月度 SIF）
OUT_DIR = Path("../Results/SIF_lon0360")   # 输出 NetCDF
FIG_DIR = Path("../Results/SIF_lon0360")  # 输出 PNG 图
GLOB_PATTERN = "*{year}*.nc"         # 每年匹配模式
SUFFIX = "_lon0360.nc"               # 另存后缀
VMIN, VMAX = 0, 7                    # 颜色范围（按需调整）
CMAP = "YlOrRd"                      # 色图（按需调整）
TITLE_PREFIX = "OCO2 SIF"  # 图标题前缀（按需调整）
# ==================

OUT_DIR.mkdir(parents=True, exist_ok=True)
FIG_DIR.mkdir(parents=True, exist_ok=True)

def find_lon_name(ds):
    for name in ["lon", "longitude", "x", "Longitudes", "LONGITUDE"]:
        if name in ds.coords or name in ds.variables:
            return name
    # 猜一个（非纬度的那个）
    for name in ds.coords:
        if "lat" not in name.lower():
            return name
    raise ValueError("无法识别经度变量名。")

def find_lat_name(ds):
    for name in ["lat", "latitude", "y", "LATITUDE"]:
        if name in ds.coords or name in ds.variables:
            return name
    for name in ds.coords:
        if "lon" not in name.lower():
            return name
    raise ValueError("无法识别纬度变量名。")

def pick_main_var(ds):
    # 优先挑名字里含 sif 的变量；否则取第一个数据变量
    sif_like = [v for v in ds.data_vars if "sif" in v.lower()]
    if sif_like:
        return sif_like[0]
    return list(ds.data_vars)[0]

def to_0360(ds, lon_name=None):
    if lon_name is None:
        lon_name = find_lon_name(ds)
    lon = np.asarray(ds[lon_name].values)
    if np.nanmin(lon) >= 0 and np.nanmax(lon) <= 360:
        return ds.sortby(lon_name)
    lon_new = (lon % 360 + 360) % 360
    ds = ds.assign_coords({lon_name: lon_new}).sortby(lon_name)
    ds[lon_name].attrs["units"] = "degrees_east"
    ds[lon_name].attrs["long_name"] = "longitude (0-360)"
    return ds

def compress_encoding(ds):
    enc = {}
    for v in ds.data_vars:
        enc[v] = {"zlib": True, "complevel": 4, "shuffle": True}
    return enc

def out_nc_path(in_path: Path) -> Path:
    return OUT_DIR / f"{in_path.stem}{SUFFIX}"

def out_png_path(in_path: Path) -> Path:
    return FIG_DIR / f"{in_path.stem}{SUFFIX.replace('.nc','')}.png"

def parse_year_month(stem: str):
    # 尝试从文件名中提取 YYYY 和 MM
    m = re.search(r"(20\d{2})[-_]?(\d{2})", stem)
    if m:
        return m.group(1), m.group(2)
    return None, None

def plot_ds(ds, varname, nc_in: Path, png_out: Path):
    lon_name = find_lon_name(ds)
    lat_name = find_lat_name(ds)
    data = ds[varname]

    year, month = parse_year_month(nc_in.stem)
    ym = f"{year}-{month}" if year and month else ""

    # 优先使用 cartopy；没有则回退
    try:
        import cartopy.crs as ccrs
        proj = ccrs.PlateCarree(central_longitude=180)  # 适配 0–360
        pc = ccrs.PlateCarree()

        fig = plt.figure(figsize=(12, 6))
        ax = plt.axes(projection=proj)
        # extent 选填：显示全球
        ax.set_global()
        ax.coastlines(linewidth=0.5)

        # pcolormesh 需要 2D 网格或 1D lon/lat
        im = ax.pcolormesh(
            ds[lon_name], ds[lat_name], data,
            transform=pc, shading="auto", vmin=VMIN, vmax=VMAX, cmap=CMAP
        )
 
        cb = plt.colorbar(im, ax=ax, orientation="vertical", fraction=0.025, pad=0.02)
        cb.set_label("SIF 740 nm")

        title = f"{TITLE_PREFIX} - {ym}" if ym else TITLE_PREFIX
        ax.set_title(title)
        plt.tight_layout()
        fig.savefig(png_out, dpi=200)
        plt.close(fig)
    except Exception as _:
        # 回退方案：不带海岸线
        fig = plt.figure(figsize=(14, 5))
        ax = plt.gca()
        im = data.plot(ax=ax, vmin=VMIN, vmax=VMAX, cmap=CMAP, add_colorbar=True)
        ax.set_title(f"{TITLE_PREFIX} - {ym}" if ym else TITLE_PREFIX)
        plt.tight_layout()
        fig.savefig(png_out, dpi=200)
        plt.close(fig)

def process_one(nc_path: Path):
    nc_out = out_nc_path(nc_path)
    png_out = out_png_path(nc_path)

    with xr.open_dataset(nc_path, decode_times=False) as ds:
        lon_name = find_lon_name(ds)
        ds2 = to_0360(ds, lon_name=lon_name)
        varname = pick_main_var(ds2)

        # 保存 nc
        if not nc_out.exists():
            ds2.to_netcdf(nc_out, encoding=compress_encoding(ds2))

        # 生成 PNG
        plot_ds(ds2, varname, nc_path, png_out)

def main():
    files = []
    for y in YEARS:
        files.extend(sorted(IN_DIR.glob(GLOB_PATTERN.format(year=y))))
    if not files:
        raise SystemExit("未找到任何匹配的 nc 文件。请检查 IN_DIR 与 GLOB_PATTERN。")

    for f in tqdm(files, desc="Converting & plotting"):
        try:
            process_one(f)
        except Exception as e:
            print(f"[ERROR] {f.name}: {e}")

    print(f"\n完成：\n  NetCDF -> {OUT_DIR.resolve()}\n  PNG    -> {FIG_DIR.resolve()}")

if __name__ == "__main__":
    main()
