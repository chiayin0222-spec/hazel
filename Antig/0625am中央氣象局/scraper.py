import os
import json
import requests
import pandas as pd
import urllib3

# 停用 SSL 警告（當 verify=False 時）
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 載入環境變數 (支援 python-dotenv，若未安裝則手動解析)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # 簡易手動解析 .env 檔案
    env_path = os.path.join(os.path.dirname(__file__), ".env") if "__file__" in locals() else ".env"
    if os.path.exists(env_path):
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    key, _, value = line.partition('=')
                    os.environ[key.strip()] = value.strip().strip('"').strip("'")

# 從環境變數讀取 Token，並提供預設值
CWA_TOKEN = os.getenv("CWA_TOKEN", "CWA-A05A0E95-BC3F-4C86-8E84-DD99B50E716D")

# 中央氣象局觀測資料 API (O-A0001-001)
API_URL = f"https://opendata.cwa.gov.tw/fileapi/v1/opendataapi/O-A0001-001?Authorization={CWA_TOKEN}&downloadType=WEB&format=JSON"
JSON_OUTPUT = "weather_observation.json"
CSV_OUTPUT = "weather_observation.csv"
JSON_CLEAN_OUTPUT = "weather_clean.json"

def fetch_weather_data(url):
    """
    向氣象局 API 發送請求以下載最新的觀測資料 (忽略 SSL 憑證驗證)
    """
    print(f"正在從 {url} 下載資料...")
    try:
        # 使用 verify=False 繞過憑證驗證問題
        response = requests.get(url, timeout=30, verify=False)
        response.raise_for_status()
        data = response.json()
        print("資料下載成功！")
        return data
    except requests.exceptions.RequestException as e:
        print(f"下載失敗，發生錯誤: {e}")
        return None

def save_raw_json(data, filepath):
    """
    將原始的 JSON 資料儲存至指定路徑
    """
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"原始 JSON 資料已儲存至: {filepath}")
    except Exception as e:
        print(f"儲存 JSON 失敗: {e}")

def parse_to_csv(data, filepath):
    """
    解析 JSON 中的測站資料並儲存為 CSV 格式 (支援 Excel 讀取)
    """
    try:
        dataset = data.get("cwaopendata", {}).get("dataset", {})
        stations = dataset.get("Station", [])
        if not stations:
            print("找不到測站觀測資料 (Station list is empty)。")
            return
        
        parsed_records = []
        for station in stations:
            # 取得測站基本資訊
            station_name = station.get("StationName")
            station_id = station.get("StationId")
            
            obs_time = None
            if isinstance(station.get("ObsTime"), dict):
                obs_time = station["ObsTime"].get("DateTime")
                
            geo_info = station.get("GeoInfo", {})
            county_name = geo_info.get("CountyName")
            town_name = geo_info.get("TownName")
            altitude = geo_info.get("StationAltitude")
            
            # 抓取 WGS84 座標系統的經緯度
            coordinates = geo_info.get("Coordinates", [])
            lat = None
            lon = None
            for coord in coordinates:
                if coord.get("CoordinateName") == "WGS84":
                    lat = coord.get("StationLatitude")
                    lon = coord.get("StationLongitude")
                    break
            if not lat and coordinates:
                lat = coordinates[0].get("StationLatitude")
                lon = coordinates[0].get("StationLongitude")
                
            # 取得天氣觀測要素
            weather_elem = station.get("WeatherElement", {})
            weather = weather_elem.get("Weather")
            
            precipitation = None
            if isinstance(weather_elem.get("Now"), dict):
                precipitation = weather_elem["Now"].get("Precipitation")
                
            wind_dir = weather_elem.get("WindDirection")
            wind_speed = weather_elem.get("WindSpeed")
            temp = weather_elem.get("AirTemperature")
            rh = weather_elem.get("RelativeHumidity")
            pressure = weather_elem.get("AirPressure")
            
            # 取得當日極值 (最高溫與最低溫及其發生時間)
            daily_extreme = weather_elem.get("DailyExtreme", {})
            daily_high_temp = daily_extreme.get("DailyHigh", {}).get("TemperatureInfo", {}).get("AirTemperature")
            daily_high_time = daily_extreme.get("DailyHigh", {}).get("TemperatureInfo", {}).get("Occurred_at", {}).get("DateTime")
            daily_low_temp = daily_extreme.get("DailyLow", {}).get("TemperatureInfo", {}).get("AirTemperature")
            daily_low_time = daily_extreme.get("DailyLow", {}).get("TemperatureInfo", {}).get("Occurred_at", {}).get("DateTime")
            
            record = {
                "測站名稱": station_name,
                "測站ID": station_id,
                "縣市": county_name,
                "鄉鎮": town_name,
                "高度(m)": altitude,
                "緯度(WGS84)": lat,
                "經度(WGS84)": lon,
                "觀測時間": obs_time,
                "天氣狀況": weather,
                "氣溫(℃)": temp,
                "相對濕度(%)": rh,
                "氣壓(hPa)": pressure,
                "降雨量(mm)": precipitation,
                "風速(m/s)": wind_speed,
                "風向(度)": wind_dir,
                "今日最高溫(℃)": daily_high_temp,
                "最高溫時間": daily_high_time,
                "今日最低溫(℃)": daily_low_temp,
                "最低溫時間": daily_low_time
            }
            parsed_records.append(record)
            
        df = pd.DataFrame(parsed_records)
        # 使用 utf-8-sig 編碼以確保 Excel 開啟時中文不會亂碼
        df.to_csv(filepath, index=False, encoding='utf-8-sig')
        print(f"解析完成，CSV 資料已儲存至: {filepath} (共 {len(parsed_records)} 筆測站資料)")
    except Exception as e:
        print(f"解析並儲存 CSV 失敗: {e}")

def save_clean_json(data, filepath):
    """
    解析 JSON 中的測站資料並儲存為適合前端地圖顯示的乾淨 JSON 格式
    """
    try:
        dataset = data.get("cwaopendata", {}).get("dataset", {})
        stations = dataset.get("Station", [])
        if not stations:
            print("找不到測站觀測資料 (Station list is empty)。")
            return
        
        clean_records = []
        for station in stations:
            station_name = station.get("StationName")
            station_id = station.get("StationId")
            
            obs_time = None
            if isinstance(station.get("ObsTime"), dict):
                obs_time = station["ObsTime"].get("DateTime")
                
            geo_info = station.get("GeoInfo", {})
            county_name = geo_info.get("CountyName")
            town_name = geo_info.get("TownName")
            
            # WGS84 座標
            coordinates = geo_info.get("Coordinates", [])
            lat = None
            lon = None
            for coord in coordinates:
                if coord.get("CoordinateName") == "WGS84":
                    lat = coord.get("StationLatitude")
                    lon = coord.get("StationLongitude")
                    break
            if not lat and coordinates:
                lat = coordinates[0].get("StationLatitude")
                lon = coordinates[0].get("StationLongitude")
                
            # 轉換 lat, lon 為 float
            try:
                lat = float(lat) if lat else None
                lon = float(lon) if lon else None
            except ValueError:
                lat = None
                lon = None
                
            if lat is None or lon is None:
                continue
                
            weather_elem = station.get("WeatherElement", {})
            
            # 取得氣溫 (排除 -99 等無效值)
            temp_val = weather_elem.get("AirTemperature")
            try:
                temp = float(temp_val) if temp_val is not None else None
                if temp is not None and temp <= -90:
                    temp = None
            except ValueError:
                temp = None
                
            # 只有當氣溫有效時才加入
            if temp is None:
                continue
                
            # 相對濕度
            rh_val = weather_elem.get("RelativeHumidity")
            try:
                rh = float(rh_val) if rh_val is not None else None
                if rh is not None and rh < 0:
                    rh = None
            except ValueError:
                rh = None
                
            # 氣壓
            press_val = weather_elem.get("AirPressure")
            try:
                pressure = float(press_val) if press_val is not None else None
                if pressure is not None and pressure < 0:
                    pressure = None
            except ValueError:
                pressure = None
                
            # 降雨量
            prec_val = None
            if isinstance(weather_elem.get("Now"), dict):
                prec_val = weather_elem["Now"].get("Precipitation")
            try:
                precipitation = float(prec_val) if prec_val is not None else None
                if precipitation is not None and precipitation < 0:
                    precipitation = None
            except ValueError:
                precipitation = None
                
            record = {
                "stationName": station_name,
                "stationId": station_id,
                "county": county_name,
                "town": town_name,
                "lat": lat,
                "lon": lon,
                "temperature": temp,
                "humidity": rh,
                "pressure": pressure,
                "precipitation": precipitation,
                "obsTime": obs_time
            }
            clean_records.append(record)
            
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(clean_records, f, ensure_ascii=False, indent=2)
        print(f"乾淨 JSON 資料已儲存至: {filepath} (共 {len(clean_records)} 筆有效測站資料)")
    except Exception as e:
        print(f"儲存乾淨 JSON 失敗: {e}")

def main():
    data = fetch_weather_data(API_URL)
    if data:
        save_raw_json(data, JSON_OUTPUT)
        parse_to_csv(data, CSV_OUTPUT)
        save_clean_json(data, JSON_CLEAN_OUTPUT)
    else:
        print("無法取得資料，結束執行。")

if __name__ == "__main__":
    main()
