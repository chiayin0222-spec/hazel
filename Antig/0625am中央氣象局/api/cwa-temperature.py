import os
import json
import ssl
import urllib.request
from http.server import BaseHTTPRequestHandler

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # 1. Read CWA Token from environment variables (fallback to default key)
        cwa_token = os.environ.get("CWA_TOKEN", "CWA-A05A0E95-BC3F-4C86-8E84-DD99B50E716D")
        
        # 2. Construct API URL
        api_url = f"https://opendata.cwa.gov.tw/fileapi/v1/opendataapi/O-A0001-001?Authorization={cwa_token}&downloadType=WEB&format=JSON"
        
        try:
            # Bypass SSL verify issues (equivalent to verify=False)
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE

            # Fetch the CWA API
            req = urllib.request.Request(api_url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, context=ctx, timeout=30) as response:
                data = json.loads(response.read().decode('utf-8'))
                
            # 3. Clean and process the CWA data in memory
            dataset = data.get("cwaopendata", {}).get("dataset", {})
            stations = dataset.get("Station", [])
            
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
                
                # Extract WGS84 Coordinates
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
                    
                # Convert coordinates to floats
                try:
                    lat = float(lat) if lat else None
                    lon = float(lon) if lon else None
                except ValueError:
                    lat = None
                    lon = None
                    
                if lat is None or lon is None:
                    continue
                    
                weather_elem = station.get("WeatherElement", {})
                
                # Clean temperature (exclude invalid values <= -90)
                temp_val = weather_elem.get("AirTemperature")
                try:
                    temp = float(temp_val) if temp_val is not None else None
                    if temp is not None and temp <= -90:
                        temp = None
                except ValueError:
                    temp = None
                    
                # Only include station if temperature is valid
                if temp is None:
                    continue
                    
                # Clean relative humidity
                rh_val = weather_elem.get("RelativeHumidity")
                try:
                    rh = float(rh_val) if rh_val is not None else None
                    if rh is not None and rh < 0:
                        rh = None
                except ValueError:
                    rh = None
                    
                # Clean air pressure
                press_val = weather_elem.get("AirPressure")
                try:
                    pressure = float(press_val) if press_val is not None else None
                    if pressure is not None and pressure < 0:
                        pressure = None
                except ValueError:
                    pressure = None
                    
                # Clean precipitation
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
                
            # Send clean JSON response
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(clean_records, ensure_ascii=False, indent=2).encode('utf-8'))
            return
            
        except Exception as e:
            # Handle and output error
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            err_res = {"error": f"Failed to fetch or clean weather data: {str(e)}"}
            self.wfile.write(json.dumps(err_res).encode('utf-8'))
            return
