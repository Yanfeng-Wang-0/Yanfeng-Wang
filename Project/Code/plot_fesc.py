import os, re, glob
import numpy as np
import xarray as xr
import matplotlib.pyplot as plt

# ===== 配置 =====
data_dir = "/home/yanfeng-wang/Documents/Project/Results/fesc_OCO2"  # 你的nc所在目录
out_dir  = "/home/yanfeng-wang/Documents/Project/Results/fesc_OCO2/quick_maps"
os.makedirs(out_dir, exist_ok=True)

# 匹配文件：fesc_phiF_YYYY_MM_vza5.nc
pattern = os.path.join(data_dir, "fesc_phiF_*_*.nc")
files = sorted(glob.glob(pattern))

# 用正则从文件名中提取 YYYY-MM
ym_re = re.compile(r"fesc_phiF_(\d{4})_(\d{2})", re.IGNORECASE)

def plot_phiF(arr, lats, lons, title_text, save_path, vmin=0.0, vmax=0.04):
    plt.figure(figsize=(10,5))
    ax = plt.gca()
    ax.set_facecolor("white")  # NaN 显示为白底

    # xarray 数据 -> numpy，并确保经纬度是单调递增
    data = np.array(arr)
    lat = np.array(lats)
    lon = np.array(lons)

    if lat[0] > lat[-1]:
        lat = lat[::-1]
        data = data[::-1, :]
    if lon[0] > lon[-1]:
        lon = lon[::-1]
        data = data[:, ::-1]

    extent = [lon.min(), lon.max(), lat.min(), lat.max()]
    data = np.ma.masked_invalid(data)

    im = plt.imshow(
        data, origin="lower", extent=extent, aspect="auto",
        vmin=vmin, vmax=vmax
    )
    cbar = plt.colorbar(im)
    cbar.set_label(r"$\varphi F$")  # 色标标签：φF

    plt.title(title_text)           # <-- 修正了变量名，并使用希腊字母标题
    plt.xlabel("Longitude")
    plt.ylabel("Latitude")
    plt.tight_layout()
    plt.savefig(save_path, dpi=300)
    plt.close()

for f in files:
    m = ym_re.search(os.path.basename(f))
    if not m:
        continue
    yyyy, mm = m.group(1), m.group(2)

    try:
        ds = xr.open_dataset(f)
        # 变量名按你数据：phiF_emitted（如不同，改这里）
        phiF = ds["phiF_emitted"]
        phiF = xr.where(phiF < 0, 0, phiF)

        save_png = os.path.join(out_dir, f"map_phiF_{yyyy}_{mm}.png")
        # 标题里用希腊字母：OCO-2 φF (YYYY-MM)
        title = rf"OCO-2 $\varphi F$ ({yyyy}-{mm})"   # 也可以换成 r"OCO-2 $\phi F$"
        plot_phiF(phiF, ds["lat"], ds["lon"], title, save_png, vmin=0.0, vmax=0.04)
        print(f"完成：{save_png}")
    except Exception as e:
        print(f"[跳过] {f} -> {e}")
