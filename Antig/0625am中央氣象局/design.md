# Weather Temperature Visualization Design

## 1. Project Goal

Build a web dashboard that visualizes **CWA temperature observation data** on a **Windy map**.

The main idea:

```text
CWA Temperature Data → Clean JSON → Windy Map → Leaflet Overlay → Temperature Visualization
```

Windy provides the beautiful weather map background.
Leaflet is used to draw custom CWA temperature data on top of the Windy map.

---

## 2. Data Source

### CWA OpenData

Recommended dataset:

```text
O-A0001-001
Surface Weather Observation Data
```

Use this dataset for:

* Station name
* Latitude
* Longitude
* Temperature
* Observation time
* Weather station information

CWA OpenData page:
https://opendata.cwa.gov.tw/dataset/observation/O-A0001-001

---

## 3. Visualization Tool

### Windy Map Forecast API

Windy Map Forecast API is used as the base map.

It supports:

* Weather map layers
* Windy-style weather visualization
* Map zoom and movement
* Leaflet-based map interaction

Windy documentation:
https://api.windy.com/map-forecast/docs

Windy hello world example:
https://api.windy.com/map-forecast/tutorials/hello-world

---

## 4. Why Leaflet Is Needed

Windy Map Forecast API is built on Leaflet.

After Windy initializes, it gives us a Leaflet map object:

```javascript
windyInit(options, windyAPI => {
  const { map } = windyAPI;
});
```

Then we can add our own CWA data:

```javascript
L.circleMarker([lat, lon]).addTo(map);
```

Windy = beautiful weather map
Leaflet = custom CWA data overlay

---

## 5. System Architecture

```text
┌──────────────────────────────┐
│ CWA OpenData API             │
│ O-A0001-001                  │
└───────────────┬──────────────┘
                │
                ▼
┌──────────────────────────────┐
│ Data Cleaning                │
│ - station name               │
│ - latitude                   │
│ - longitude                  │
│ - temperature                │
│ - observation time           │
└───────────────┬──────────────┘
                │
                ▼
┌──────────────────────────────┐
│ Frontend                     │
│ - Windy Map API              │
│ - Leaflet                    │
│ - Temperature markers        │
│ - Popup cards                │
└───────────────┬──────────────┘
                │
                ▼
┌──────────────────────────────┐
│ User Dashboard               │
│ - Taiwan temperature map     │
│ - color temperature markers  │
│ - station popup              │
│ - temperature legend         │
└──────────────────────────────┘
```

---

## 6. Data Format

Convert CWA data into this simple format:

```json
[
  {
    "stationName": "Taipei",
    "lat": 25.0375,
    "lon": 121.5637,
    "temperature": 31.2,
    "obsTime": "2026-07-02 09:00"
  },
  {
    "stationName": "Taichung",
    "lat": 24.1477,
    "lon": 120.6736,
    "temperature": 30.5,
    "obsTime": "2026-07-02 09:00"
  }
]
```

---

## 7. Temperature Color Design

Use color to show temperature level.

| Temperature | Meaning     | Color  |
| ----------- | ----------- | ------ |
| `< 15°C`    | Cold        | Blue   |
| `15–22°C`   | Cool        | Green  |
| `22–28°C`   | Comfortable | Yellow |
| `28–34°C`   | Hot         | Orange |
| `> 34°C`    | Very hot    | Red    |

Example function:

```javascript
function getTempColor(temp) {
  if (temp < 15) return "#2b83ba";
  if (temp < 22) return "#abdda4";
  if (temp < 28) return "#ffffbf";
  if (temp < 34) return "#fdae61";
  return "#d7191c";
}
```

---

## 8. Windy Map Setup

HTML:

```html
<div id="windy"></div>
```

CSS:

```css
#windy {
  width: 100%;
  height: 100vh;
}
```

JavaScript libraries:

```html
<script src="https://unpkg.com/leaflet@1.4.0/dist/leaflet.js"></script>
<script src="https://api.windy.com/assets/map-forecast/libBoot.js"></script>
```

Windy initialization:

```javascript
const options = {
  key: "YOUR_WINDY_API_KEY",
  lat: 23.8,
  lon: 121.0,
  zoom: 7,
  overlay: "temp"
};

windyInit(options, windyAPI => {
  const { map } = windyAPI;

  loadCwaTemperatureData(map);
});
```

---

## 9. Add CWA Temperature Markers

```javascript
function addTemperatureMarker(map, item) {
  const color = getTempColor(item.temperature);

  const marker = L.circleMarker([item.lat, item.lon], {
    radius: 8,
    color: color,
    fillColor: color,
    fillOpacity: 0.85,
    weight: 1
  }).addTo(map);

  marker.bindPopup(`
    <b>${item.stationName}</b><br>
    Temperature: ${item.temperature} °C<br>
    Time: ${item.obsTime}
  `);
}
```

---

## 10. Load CWA Data

Example:

```javascript
async function loadCwaTemperatureData(map) {
  const response = await fetch("/api/cwa-temperature");
  const data = await response.json();

  data.forEach(item => {
    addTemperatureMarker(map, item);
  });
}
```

---

## 11. Recommended Dashboard Layout

```text
┌──────────────────────────────────────────────┐
│ Header: CWA Temperature Map                  │
├──────────────────────────────────────────────┤
│ Windy Map                                    │
│ - temperature layer                          │
│ - CWA station markers                        │
│ - popup information                          │
├──────────────────────────────────────────────┤
│ Bottom panel                                 │
│ - average temperature                        │
│ - highest temperature                        │
│ - lowest temperature                         │
│ - observation time                           │
└──────────────────────────────────────────────┘
```

---

## 12. Main Features

### Basic Version

* Show Windy map
* Show CWA temperature markers
* Marker color changes by temperature
* Popup shows station name and temperature

### Advanced Version

* Add temperature legend
* Add search by city
* Add heatmap layer
* Add station filter
* Add temperature trend chart
* Auto-refresh every 10 minutes

---

## 13. File Structure

```text
weather-windy-dashboard/
│
├── index.html
├── style.css
├── app.js
├── README.md
└── design.md
```

Optional backend version:

```text
weather-windy-dashboard/
│
├── backend/
│   ├── main.py
│   └── requirements.txt
│
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── app.js
│
├── README.md
└── design.md
```

---

## 14. API Key Requirements

You need:

1. CWA OpenData API key
2. Windy API key

Store keys safely.

Do not commit API keys to GitHub.

Bad:

```javascript
const key = "real-api-key";
```

Better:

```javascript
const key = "YOUR_API_KEY";
```

For production, use a backend proxy to protect keys.

---

## 15. Final Recommendation

Use this design:

```text
Windy Map Forecast API
+ Leaflet circle markers
+ CWA O-A0001-001 temperature data
+ color temperature legend
+ popup station cards
```

This is simple, beautiful, and suitable for a weather visualization dashboard.
