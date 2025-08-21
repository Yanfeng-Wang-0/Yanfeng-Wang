import numpy as np
import pandas as pd
import xarray as xr
from pvlib.solarposition import get_solarposition
import pytz
from datetime import datetime
from joblib import Parallel, delayed
from tqdm import tqdm

# 参数设置
latitudes = np.arange(-89.5, 90.5, 1.0)       # 纬度：1° 分辨率
longitudes = np.arange(0, 360, 1.0)       # 经度：1° 分辨率
times = pd.date_range("2020-01-01", "2020-12-31", freq="16D")
timezone = pytz.UTC

# 栅格计算函数
def compute_daylength(lat, lon, times):
    result = np.full(len(times), np.nan)
    for i, date in enumerate(times):
        try:
            time_range = pd.date_range(datetime(date.year, date.month, date.day, 0, 0, 0, tzinfo=timezone),
                                       periods=96, freq="15min")
            sp = get_solarposition(time_range, latitude=lat, longitude=lon)
            result[i] = (sp['apparent_elevation'] > 0).sum() * 15  # 每个时间段 15 分钟
        except Exception:
            continue
    return lat, lon, result

# 并行计算所有网格（约64800个）
results = Parallel(n_jobs=-1, backend="loky", verbose=10)(
    delayed(compute_daylength)(lat, lon, times)
    for lat in latitudes for lon in longitudes
)

# 初始化 3D 数据数组
day_arr = np.full((len(times), len(latitudes), len(longitudes)), np.nan)

# 写入数组
for lat, lon, values in results:
    i = np.where(latitudes == lat)[0][0]
    j = np.where(longitudes == lon)[0][0]
    day_arr[:, i, j] = values

# 构造 xarray Dataset
ds = xr.Dataset(
    {
        "daylength_min": (["time", "lat", "lon"], day_arr)
    },
    coords={
        "time": times,
        "lat": latitudes,
        "lon": longitudes
    }
)

# 保存为 NetCDF 文件
ds.to_netcdf("../Data/global_daylength.nc")
print("✅ NetCDF 文件已生成：global_daylength.nc")
