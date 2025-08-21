# analysis_phiF_bar_hemispheres.py
import os
from pathlib import Path
import numpy as np
import xarray as xr
import matplotlib.pyplot as plt

# ========= 配置 =========
YEARS = range(2014, 2021)  # 2014–2020
DATA_DIR = Path("../Results/fesc_OCO2")        # 每月仅1个文件的目录
MASK_DIR = Path("../Data/landcover/mask")      # 存放 landcover 掩膜
MASK_NAME_PREFERRED = "LC_Mask_1to10_12"       # 期望的掩膜变量名
FILENAME_FMT = "fesc_phiF_{year}_{month:02d}_vza5.nc"

OUT_DIR = Path("../Results/Plot/phiF")
OUT_DIR.mkdir(parents=True, exist_ok=True)
# =======================

def find_lat_name(ds):
    for k in ["lat", "latitude", "y"]:
        if k in ds.coords or k in ds.dims:
            return k
    raise ValueError("未找到纬度坐标（lat/latitude）。")

def find_lon_name(ds):
    for k in ["lon", "longitude", "x"]:
        if k in ds.coords or k in ds.dims:
            return k
    raise ValueError("未找到经度坐标（lon/longitude）。")

def pick_mask_var(ds):
    """优先使用 LC_Mask_1to10_12；否则挑包含 'mask' 的变量。"""
    if MASK_NAME_PREFERRED in ds.data_vars:
        return ds[MASK_NAME_PREFERRED]
    cands = [v for v in ds.data_vars if "mask" in v.lower()]
    if not cands:
        raise ValueError(f"掩膜变量未找到，现有变量：{list(ds.data_vars)}")
    return ds[cands[0]]

def pick_phif_var(ds):
    """优先 phif / phi；回退第一个数值变量。"""
    num_vars = [v for v in ds.data_vars if np.issubdtype(ds[v].dtype, np.number)]
    pref = [v for v in num_vars if "phif" in v.lower()] or \
           [v for v in num_vars if "phi" in v.lower()]
    if pref:
        return ds[pref[0]]
    if not num_vars:
        raise ValueError(f"没有数值型数据变量，现有变量：{list(ds.data_vars)}")
    return ds[num_vars[0]]

def area_weighted_mean_hemi(da: xr.DataArray, mask: xr.DataArray, hemisphere: str):
    """
    对 da 应用掩膜（=1 保留）并在指定半球做 cos(lat) 加权均值。
    hemisphere: 'NH' 或 'SH'
    """
    lat_name = find_lat_name(da.to_dataset())
    lon_name = find_lon_name(da.to_dataset())

    lat = da[lat_name]
    if hemisphere.upper() == "NH":
        hemi_cond = lat >= 0
    elif hemisphere.upper() == "SH":
        hemi_cond = lat < 0
    else:
        raise ValueError("hemisphere 只能是 'NH' 或 'SH'")

    # 半球筛选 + 掩膜 + 合理范围
    da_masked = da.where(hemi_cond)
    da_masked = da_masked.where((mask == 1) & np.isfinite(da_masked) &
                                (da_masked >= 0.0) & (da_masked <= 0.05))

    # 权重：cos(lat)（同样只在半球有效）
    w1d = np.cos(np.deg2rad(lat)).where(hemi_cond)
    weights = xr.ones_like(da_masked) * w1d
    weights = weights.where(np.isfinite(da_masked))  # 仅对有效格点计权

    num = (da_masked * weights).sum(dim=[lat_name, lon_name], skipna=True)
    den = weights.sum(dim=[lat_name, lon_name], skipna=True)
    if float(den) == 0 or np.isnan(den):
        return np.nan
    return float(num / den)

def main():
    for year in YEARS:
        print(f"\n📅 处理中：{year}")
        mask_path = MASK_DIR / f"landcover_{year}_1deg_mask_1to10_12.nc"
        if not mask_path.exists():
            print(f"⚠️ 掩膜缺失：{mask_path}，跳过 {year}")
            continue

        # 读取掩膜
        ds_mask = xr.open_dataset(mask_path)
        mask_da = pick_mask_var(ds_mask)
        print(f"✅ 掩膜变量：{mask_da.name}  形状={tuple(mask_da.shape)}")

        monthly_NH, monthly_SH = [], []

        for m in range(1, 13):
            fn = DATA_DIR / FILENAME_FMT.format(year=year, month=m)
            if not fn.exists():
                print(f"❌ 缺失 {fn.name} → NH/SH 记为 NaN")
                monthly_NH.append(np.nan)
                monthly_SH.append(np.nan)
                continue

            with xr.open_dataset(fn) as ds:
                phif = pick_phif_var(ds)
                # 诊断打印
                try:
                    vmin = float(phif.min()); vmax = float(phif.max())
                except Exception:
                    vmin = vmax = np.nan
                print(f"  {fn.name:<28} var={phif.name:<15} range[{vmin:.5f}, {vmax:.5f}]")

                mean_nh = area_weighted_mean_hemi(phif, mask_da, "NH")
                mean_sh = area_weighted_mean_hemi(phif, mask_da, "SH")
                monthly_NH.append(mean_nh)
                monthly_SH.append(mean_sh)
                print(f"    → NH={mean_nh:.5f}  SH={mean_sh:.5f}")

        # —— 画图：北半球
        plt.figure(figsize=(9, 5))
        plt.bar(range(1, 13), monthly_NH, edgecolor="black")
        plt.xticks(ticks=range(1, 13),
                   labels=["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"])
        plt.ylabel("Monthly Mean φF (Area-Weighted, NH)")
        plt.xlabel("Month")
        plt.title(f"Northern Hemisphere Monthly Mean φF in {year} (LC 1–10 & 12)")
        plt.grid(axis="y", linestyle="--", alpha=0.4)
        plt.tight_layout()
        out_png_nh = OUT_DIR / f"PhiF_monthly_barplot_{year}_NH_weighted.png"
        plt.savefig(out_png_nh, dpi=300); plt.close()
        print(f"✅ 图像已保存：{out_png_nh}")

        # —— 画图：南半球
        plt.figure(figsize=(9, 5))
        plt.bar(range(1, 13), monthly_SH, edgecolor="black", color="salmon")
        plt.xticks(ticks=range(1, 13),
                   labels=["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"])
        plt.ylabel("Monthly Mean φF (Area-Weighted, SH)")
        plt.xlabel("Month")
        plt.title(f"Southern Hemisphere Monthly Mean φF in {year} (LC 1–10 & 12)")
        plt.grid(axis="y", linestyle="--", alpha=0.4)
        plt.tight_layout()
        out_png_sh = OUT_DIR / f"PhiF_monthly_barplot_{year}_SH_weighted.png"
        plt.savefig(out_png_sh, dpi=300); plt.close()
        print(f"✅ 图像已保存：{out_png_sh}")

if __name__ == "__main__":
    main()
