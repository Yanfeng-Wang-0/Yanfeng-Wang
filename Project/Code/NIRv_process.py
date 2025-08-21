# NIRV_process_fixed.py
import os
import glob
import xarray as xr
import numpy as np

# ========= 路径设置（按你的机器修改） =========
NIRV_ROOT = os.path.expanduser("~/Documents/Project/Data/NIRv")  # 2014/…/2020 子目录
IMERG_MASK_FILE = os.path.expanduser("~/Documents/Project/Data/IMERG_land_mask_1deg.nc")
# 你也可以用绝对路径：IMERG_MASK_FILE = "/mnt/data/IMERG_land_mask_1deg.nc"
OUT_SUBFOLDER = "../Data/NIRv_processed"   # 每个年份目录里新建这个输出文件夹

# ========= 工具函数 =========
def to_0360(lon):
    """把经度统一到 [0, 360)"""
    lon = np.asarray(lon)
    lon = np.mod(lon, 360.0)
    return lon

def build_mask_for_target(mask_path:str, target_like:xr.Dataset, varname="land_mask",
                          coarsen_to_1deg=True, thresh=0.5) -> xr.DataArray:
    """
    读取 IMERG 掩膜 ->(可选)聚合到1° -> 对齐到 NIRv 网格 -> 再二值化
    返回布尔掩膜：True=陆地，False=海洋
    """
    mds = xr.open_dataset(mask_path)
    m = mds[varname]

    # 统一经度到 [0,360)
    if "lon" in m.coords:
        m = m.assign_coords(lon=to_0360(m["lon"]))
        m = m.sortby("lon")

    # 0.1° -> 1°：箱平均得到浮点掩膜（0~1）
    if coarsen_to_1deg:
        m1 = m.coarsen(lat=10, lon=10, boundary="trim").mean()
    else:
        m1 = m

    # 先对齐到目标网格（保持为数值型，便于 interp）
    tgt_lon = to_0360(target_like["lon"].values)
    tgt_lat = target_like["lat"].values
    m1 = m1.sortby(["lat", "lon"])

    m_on_target = m1.interp(
        lat=xr.DataArray(tgt_lat, dims=("lat",)),
        lon=xr.DataArray(tgt_lon, dims=("lon",)),
        method="nearest"
    )

    # 使用目标数据的坐标（避免 89.95/89.5 等微小差异）
    m_on_target = m_on_target.assign_coords(lat=target_like["lat"], lon=target_like["lon"])

    # 现在再阈值化成布尔
    land_bool = (m_on_target > thresh).astype(bool).rename("land_mask_bool")
    return land_bool

def apply_mask_to_file(nc_path:str, land_mask:xr.DataArray, out_path:str, fill_ocean_nan=True):
    """对单个 NIRv 文件应用掩膜并保存"""
    ds = xr.open_dataset(nc_path)

    # 经度到 [0,360)
    if "lon" in ds.coords:
        ds = ds.assign_coords(lon=to_0360(ds["lon"].values))
        ds = ds.sortby("lon")

    if fill_ocean_nan:
        masked = ds.where(land_mask)              # 海洋 -> NaN
    else:
        masked = ds.where(land_mask, other=0.0)   # 海洋 -> 0

    comp = dict(zlib=True, complevel=4, _FillValue=np.nan)
    encoding = {v: comp for v in masked.data_vars}
    masked.to_netcdf(out_path, encoding=encoding)
    print(f"saved: {out_path}")

# ========= 主流程 =========
years = list(range(2014, 2021))

# 用第一个可见文件确定目标网格
sample_file = None
for y in years:
    cand = sorted(glob.glob(os.path.join(NIRV_ROOT, str(y), f"NIRv_{y}_??_1x1.nc")))
    if cand:
        sample_file = cand[0]
        break
if sample_file is None:
    raise FileNotFoundError("未找到 NIRv_YYYY_MM_1x1.nc，请检查 NIRV_ROOT 路径与命名。")

sample_ds = xr.open_dataset(sample_file)
land_mask = build_mask_for_target(IMERG_MASK_FILE, sample_ds)

for y in years:
    in_dir = os.path.join(NIRV_ROOT, str(y))
    out_dir = os.path.join(in_dir, OUT_SUBFOLDER)
    os.makedirs(out_dir, exist_ok=True)

    files = sorted(glob.glob(os.path.join(in_dir, f"NIRv_{y}_??_1x1.nc")))
    if not files:
        print(f"[{y}] 未找到该年的 NIRv 文件，跳过。")
        continue

    print(f"=== Year {y}: {len(files)} files ===")
    for f in files:
        base = os.path.basename(f)
        out_path = os.path.join(out_dir, base.replace(".nc", "_IMERGmask.nc"))
        apply_mask_to_file(f, land_mask, out_path, fill_ocean_nan=True)
