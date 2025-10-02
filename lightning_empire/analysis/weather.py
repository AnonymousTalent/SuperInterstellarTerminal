# 檔名：fengjia_driver_protection.py
# 功能：司機降溫 + 小雨保護版
# Python3 + pip install requests pandas matplotlib numpy

import requests, datetime
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# 逢甲 / 台中經緯度
LAT, LON = 24.1477, 120.6736

# 時間範圍：未來 24 小時
now = datetime.datetime.utcnow()
start_date = now.date()
end_date = (now + datetime.timedelta(days=1)).date()

# 抓取氣象資料（含降水）
url = (
    f"https://api.open-meteo.com/v1/forecast?latitude={LAT}&longitude={LON}"
    "&hourly=temperature_2m,relativehumidity_2m,windspeed_10m,precipitation"
    f"&start_date={start_date}&end_date={end_date}"
    "&timezone=UTC"
)

r = requests.get(url, timeout=15)
r.raise_for_status()
data = r.json()

# 建立 DataFrame
df = pd.DataFrame({
    'time': pd.to_datetime(data['hourly']['time']),
    'temp_c': data['hourly']['temperature_2m'],
    'rh': data['hourly']['relativehumidity_2m'],
    'wind_m_s': data['hourly']['windspeed_10m'],
    'precip_mm': data['hourly']['precipitation']
})

# vectorized 計算 vapour pressure 與體感溫度
df['vapour_hpa'] = (df['rh']/100) * 6.105 * np.exp(17.27 * df['temp_c'] / (237.7 + df['temp_c']))
df['app_temp_c'] = df['temp_c'] + 0.33*df['vapour_hpa'] - 0.7*df['wind_m_s'] - 4.0
df['cooling_delta'] = df['temp_c'] - df['app_temp_c']

# 標示明顯降溫（可調閾值）
COOL_THRESHOLD = 1.5
df['noticeable_cool'] = df['cooling_delta'] >= COOL_THRESHOLD

# 判斷小雨（0.1 ~ 2 mm/h）
df['light_rain'] = (df['precip_mm'] >= 0.1) & (df['precip_mm'] <= 2.0)

# 警示：降溫或小雨
df['alert'] = df['noticeable_cool'] | df['light_rain']

# 找出最熱時段（體感溫度最高前5）
hottest_periods = df.nlargest(5, 'app_temp_c')[['time','temp_c','app_temp_c','wind_m_s','rh','precip_mm']]
print("🔥 最熱時段提醒司機休息或補水 🔥")
print(hottest_periods)

# 顯示有警示的時間段
alerts = df.loc[df['alert'], ['time','temp_c','app_temp_c','wind_m_s','precip_mm','noticeable_cool','light_rain']]
print("🌦️ 明顯降溫或小雨提醒時間段：")
print(alerts)

# 畫圖：溫度 vs 體感溫度 + 小雨標示
plt.figure(figsize=(12,5))
plt.plot(df['time'], df['temp_c'], label='實測溫度 (°C)', color='orange')
plt.plot(df['time'], df['app_temp_c'], label='體感溫度 (°C)', color='red')

# 標記明顯降溫點
plt.scatter(df.loc[df['noticeable_cool'], 'time'],
            df.loc[df['noticeable_cool'], 'app_temp_c'],
            color='blue', label='明顯降溫', zorder=5)

# 標記小雨點
plt.scatter(df.loc[df['light_rain'], 'time'],
            df.loc[df['light_rain'], 'app_temp_c'],
            color='cyan', label='小雨', marker='x', zorder=5)

plt.xlabel('UTC 時間')
plt.ylabel('溫度 (°C)')
plt.title('司機降溫保護 — 未來24小時溫度 vs 體感溫度 + 小雨提醒')
plt.legend()
plt.tight_layout()
plt.show()

# 匯出 CSV
df.to_csv('fengjia_driver_protection.csv', index=False)
print("✅ 匯出 fengjia_driver_protection.csv 完成")