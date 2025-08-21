#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import glob
import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
from pathlib import Path

# =============================
# 配置（按需修改）
# =============================
# LAI 根目录（PATTERNS 会在该目录下匹配 2014–2020 文件）
LAI_DIR   = "../Data/LAI/2020"
# 高分辨率陆海掩膜文件（变量名自动识别，值为 0/1 或 0..1 都可）
MASK_FILE = "../Data/IMERG_land_mask_1deg.nc"
# 输出目录
OUT_DIR   = "../Data/LAI_processed"
Path(OUT_DIR).mkdir(parents=True, exist_ok=True)

# 匹配 2014–2020 的月度文件
PATTERNS = [
    "LAI_2014_??_1x1*.nc*", "LAI_2015_??_1x1*.nc*", "LAI_2016_??_1x1*.nc*",
    "LAI_2017_??_1x1*.nc*", "LAI_2018_??_1x1*.nc*", "LAI_2019_??_1x1*.nc*",
    "LAI_2020_??_1x1*.nc*",
]

# 绘图色标（仅影响 PNG 展示）
VMIN, VMAX = 0.0, 7.0

# =============================
# 工具函数
# =============================
def find_var(ds: xr.Dataset, candidates):
    """从候选名中挑变量；都没有就取一个二维/三维变量"""
    for k in candidates:
        if k in ds.data_vars:
            return ds[k]
    for k, v in ds.data_vars.items():
        if v.ndim >= 2:
            return v
    raise KeyError("未找到合适数据变量，请检查变量名。")

def get_coords(ds: xr.Dataset):
    """返回 (lat_name, lon_name)"""
    lat_names = ["lat", "latitude", "y"]
    lon_names = ["lon", "longitude", "x"]
    lat = next((n for n in lat_names if n in ds.coords), None)
    lon = next((n for n in lon_names if n in ds.coords), None)
    if lat is None or lon is None:
        raise KeyError("经纬度坐标未找到，请检查坐标名。")
    return lat, lon

def open_mask(mask_path: str) -> xr.DataArray:
    """打开高分辨率掩膜并标准化到 0/1"""
    ds = xr.open_dataset(mask_path)
    for cand in ["land_mask", "mask", "land", "lsmask", "landsea_mask"]:
        if cand in ds.data_vars:
            da = ds[cand]
            break
    else:
        da = next(v for v in ds.data_vars.values() if v.ndim >= 2)
    da = da.astype("float32")
    da = xr.where(da > 0, 1.0, 0.0)  # 统一成 0/1
    return da

def _grid_step(coord: xr.DataArray) -> float:
    dif = np.diff(coord.values)
    return float(np.median(np.abs(dif))) if dif.size else np.nan

def coarsen_to_target(mask_da: xr.DataArray,
                      target_lat: xr.DataArray,
                      target_lon: xr.DataArray) -> xr.DataArray:
    """
    将高分辨率掩膜降到目标分辨率：
    - 若步长整除，优先 block coarsen 并取 .max()（有陆即陆）；
    - 否则直接最近邻插值到目标网格。
    """
    lat_m, lon_m = get_coords(mask_da.to_dataset(name="m"))

    dlat_m = _grid_step(mask_da[lat_m])
    dlon_m = _grid_step(mask_da[lon_m])
    dlat_t = _grid_step(target_lat)
    dlon_t = _grid_step(target_lon)

    can_block = (
        np.isfinite(dlat_m) and np.isfinite(dlat_t) and
        np.isfinite(dlon_m) and np.isfinite(dlon_t) and
        dlat_t > 0 and dlon_t > 0 and
        abs((dlat_t / dlat_m) - round(dlat_t / dlat_m)) < 1e-3 and
        abs((dlon_t / dlon_m) - round(dlon_t / dlon_m)) < 1e-3
    )

    if can_block:
        f_lat = int(round(dlat_t / dlat_m))
        f_lon = int(round(dlon_t / dlon_m))
        mask_block = mask_da.coarsen({lat_m: f_lat, lon_m: f_lon}, boundary="trim").max()
        mask_on_grid = mask_block.interp({lat_m: target_lat, lon_m: target_lon}, method="nearest")
    else:
        mask_on_grid = mask_da.interp({lat_m: target_lat, lon_m: target_lon}, method="nearest")

    return mask_on_grid

def apply_mask_and_plot(lai_path: str, out_dir: str = OUT_DIR):
    # 读取 LAI
    ds = xr.open_dataset(lai_path)
    lai = find_var(ds, ["LAI", "lai"])
    lat_lai, lon_lai = get_coords(ds)

    # 读取掩膜并对齐
    mask_hi = open_mask(MASK_FILE)
    mask_on_grid = coarsen_to_target(mask_hi, ds[lat_lai], ds[lon_lai])

    # 应用掩膜：>0.5 判为陆地（若本身是 0/1，等价于 bool）
    lai_masked = lai.where(mask_on_grid > 0.5)

    # 自检：掩膜前后有效像元数
    n_before = int(np.isfinite(lai.values).sum())
    n_after  = int(np.isfinite(lai_masked.values).sum())
    print(f"valid pixels: before={n_before}, after mask={n_after} (kept {n_after/max(n_before,1):.2%})")

    # 输出文件名
    base = os.path.basename(lai_path)
    stem, _ = os.path.splitext(base)
    out_nc  = os.path.join(out_dir, f"{stem}_masked.nc")
    out_png = os.path.join(out_dir, f"{stem}_masked.png")

    # 保存掩膜后的 NetCDF（统一变量名为 LAI）
    lai_masked.to_dataset(name="LAI").to_netcdf(out_nc)

    # ===== 画图（仅展示用；先把 time 降到 2D） =====
    if "time" in lai_masked.dims:
        if int(lai_masked.sizes["time"]) == 1:
            lai_2d = lai_masked.isel(time=0)
        else:
            lai_2d = lai_masked.mean("time", skipna=True)
    else:
        lai_2d = lai_masked

    lon = ds[lon_lai].values
    lat = ds[lat_lai].values
    extent = [float(lon.min()), float(lon.max()), float(lat.min()), float(lat.max())]

    arr = np.ma.masked_invalid(lai_2d.transpose(lat_lai, lon_lai).values)

    plt.figure(figsize=(9, 4.8), dpi=150)
    im = plt.imshow(
        arr, extent=extent, origin="lower", aspect="auto",
        vmin=VMIN, vmax=VMAX, interpolation="nearest"
    )
    plt.title(f"{stem} (masked)")
    plt.xlabel("Longitude"); plt.ylabel("Latitude")
    cb = plt.colorbar(im); cb.set_label("LAI")
    plt.tight_layout()
    plt.savefig(out_png, dpi=150)
    plt.close()

    ds.close()
    return out_nc, out_png

def gather_files(patterns):
    res = []
    for pat in patterns:
        res.extend(glob.glob(os.path.join(LAI_DIR, pat)))
    return sorted(res)

# =============================
# 主流程
# =============================
def main():
    files = gather_files(PATTERNS)
    print(f"共找到 {len(files)} 个 LAI 文件待处理。")
    for i, f in enumerate(files, 1):
        try:
            out_nc, out_png = apply_mask_and_plot(f)
            print(f"[{i}/{len(files)}] 完成：{os.path.basename(f)}")
            print(f"  -> {out_nc}")
            print(f"  -> {out_png}")
        except Exception as e:
            print(f"[{i}/{len(files)}] 处理 {f} 出错：{e}")

if __name__ == "__main__":
    main()
