/**
 * app.js - CWA Temperature & Weather Visualization Dashboard Logic
 * Integrates Windy Map API / standard Leaflet Map with CWA observation data.
 */

// Global state variables
let map = null;
let mapMode = "標準 Leaflet 地圖模式";
let allStationsData = [];
let markersLayer = null;
let updateIntervalId = null;

// Active weather variable: 'temperature', 'precipitation', or 'humidity'
let activeVar = "temperature";
let activeTileLayer = null;
let showCwaObservations = true;
let showStationLabels = false;

// Map style tile options (CartoDB and OSM)
const mapStyles = {
  osm: {
    url: "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
  },
  dark: {
    url: "https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png",
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> &copy; <a href="https://carto.com/attributions">CARTO</a>'
  },
  voyager: {
    url: "https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png",
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> &copy; <a href="https://carto.com/attributions">CARTO</a>'
  },
  satellite: {
    url: "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
    attribution: 'Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community'
  }
};

// Dynamic legends for different weather variables
const legends = {
  temperature: `
    <h3 class="legend-title">溫度級距圖例</h3>
    <div class="legend-scale">
      <div class="legend-item"><span class="color-dot" style="background-color: #2b83ba;"></span><span class="legend-label">&lt; 15°C (寒冷)</span></div>
      <div class="legend-item"><span class="color-dot" style="background-color: #abdda4;"></span><span class="legend-label">15–22°C (涼爽)</span></div>
      <div class="legend-item"><span class="color-dot" style="background-color: #ffffbf; border: 1px solid rgba(255,255,255,0.2);"></span><span class="legend-label">22–28°C (舒適)</span></div>
      <div class="legend-item"><span class="color-dot" style="background-color: #fdae61;"></span><span class="legend-label">28–34°C (炎熱)</span></div>
      <div class="legend-item"><span class="color-dot" style="background-color: #d7191c;"></span><span class="legend-label">&gt; 34°C (酷熱)</span></div>
    </div>
  `,
  precipitation: `
    <h3 class="legend-title">降雨量圖例</h3>
    <div class="legend-scale">
      <div class="legend-item"><span class="color-dot" style="background-color: #94a3b8;"></span><span class="legend-label">無降雨 (0 mm)</span></div>
      <div class="legend-item"><span class="color-dot" style="background-color: #93c5fd;"></span><span class="legend-label">&lt; 2 mm (微雨)</span></div>
      <div class="legend-item"><span class="color-dot" style="background-color: #3b82f6;"></span><span class="legend-label">2–10 mm (小雨)</span></div>
      <div class="legend-item"><span class="color-dot" style="background-color: #1d4ed8;"></span><span class="legend-label">10–20 mm (大雨)</span></div>
      <div class="legend-item"><span class="color-dot" style="background-color: #701a75;"></span><span class="legend-label">&gt; 20 mm (豪雨)</span></div>
    </div>
  `,
  humidity: `
    <h3 class="legend-title">相對濕度圖例</h3>
    <div class="legend-scale">
      <div class="legend-item"><span class="color-dot" style="background-color: #fdae61;"></span><span class="legend-label">&lt; 40% (乾燥)</span></div>
      <div class="legend-item"><span class="color-dot" style="background-color: #abdda4;"></span><span class="legend-label">40–65% (舒適)</span></div>
      <div class="legend-item"><span class="color-dot" style="background-color: #60a5fa;"></span><span class="legend-label">65–85% (潮濕)</span></div>
      <div class="legend-item"><span class="color-dot" style="background-color: #1d4ed8;"></span><span class="legend-label">&gt; 85% (極潮濕)</span></div>
    </div>
  `
};

// Variable Color Coding Function (based on design.md Section 7 & enhancements)
function getVarColor(val, variable) {
  if (val == null) return "#94a3b8"; // Gray for null

  if (variable === "temperature") {
    if (val < 15) return "#2b83ba";       // Cold
    if (val < 22) return "#abdda4";       // Cool
    if (val < 28) return "#ffffbf";       // Comfortable
    if (val < 34) return "#fdae61";       // Hot
    return "#d7191c";                      // Very Hot
  }

  if (variable === "precipitation") {
    if (val <= 0) return "#94a3b8";        // No rain
    if (val < 2) return "#93c5fd";         // Light rain
    if (val < 10) return "#3b82f6";        // Moderate rain
    if (val < 20) return "#1d4ed8";        // Heavy rain
    return "#701a75";                      // Torrential rain
  }

  if (variable === "humidity") {
    if (val < 40) return "#fdae61";        // Dry (Orange)
    if (val < 65) return "#abdda4";        // Comfortable (Green)
    if (val < 85) return "#60a5fa";        // Humid (Light Blue)
    return "#1d4ed8";                      // Very Wet (Dark Blue)
  }

  return "#3b82f6";
}

// Initialize the Application
document.addEventListener("DOMContentLoaded", () => {
  setupApp();

  // Set up refresh button event listener
  document.getElementById("refresh-btn").addEventListener("click", () => {
    const btn = document.getElementById("refresh-btn");
    btn.classList.add("fa-spin");
    fetchAndRenderData().finally(() => {
      setTimeout(() => btn.classList.remove("fa-spin"), 500);
    });
  });

  // Show / hide CWA observation markers
  document.getElementById("show-cwa").addEventListener("change", (e) => {
    showCwaObservations = e.target.checked;
    filterAndRender();
  });

  // Show / hide station labels
  document.getElementById("show-labels").addEventListener("change", (e) => {
    showStationLabels = e.target.checked;
    filterAndRender();
  });

  // Set up search event listeners
  const searchInput = document.getElementById("search-input");
  const clearBtn = document.getElementById("clear-search");
  const countySelect = document.getElementById("county-select");

  searchInput.addEventListener("input", (e) => {
    const value = e.target.value.trim();
    clearBtn.style.display = value ? "block" : "none";
    // 如果使用者在搜尋框輸入文字，自動將縣市篩選重設為「全部縣市」，避免互相衝突導致查無結果
    if (value) {
      countySelect.value = "all";
    }
    filterAndRender();
  });

  clearBtn.addEventListener("click", () => {
    searchInput.value = "";
    clearBtn.style.display = "none";
    filterAndRender();
    searchInput.focus();
  });

  // Set up county filter event listener
  countySelect.addEventListener("change", (e) => {
    // 如果使用者手動選了特定縣市，自動清除搜尋關鍵字，避免衝突
    if (e.target.value !== "all") {
      searchInput.value = "";
      clearBtn.style.display = "none";
    }
    filterAndRender();
  });

  // Set up map style toggle
  document.getElementById("map-style-select").addEventListener("change", (e) => {
    setMapStyle(e.target.value);
  });

  // Set up weather variable toggles
  setupVariableToggles();

  // Start auto-refresh interval (every 10 minutes)
  updateIntervalId = setInterval(fetchAndRenderData, 10 * 60 * 1000);
});

// Setup function toggle buttons for weather variables
function setupVariableToggles() {
  const btnTemp = document.getElementById("btn-var-temp");
  const btnRain = document.getElementById("btn-var-rain");
  const btnRh = document.getElementById("btn-var-rh");

  const activateButton = (activeBtn, inactiveBtns) => {
    activeBtn.style.background = "rgba(59, 130, 246, 0.15)";
    activeBtn.style.color = "var(--accent-color)";
    activeBtn.classList.add("active");

    inactiveBtns.forEach(btn => {
      btn.style.background = "rgba(255, 255, 255, 0.04)";
      btn.style.color = "var(--text-primary)";
      btn.classList.remove("active");
    });
  };

  btnTemp.addEventListener("click", () => {
    activeVar = "temperature";
    activateButton(btnTemp, [btnRain, btnRh]);
    updateLegend();
    filterAndRender();
  });

  btnRain.addEventListener("click", () => {
    activeVar = "precipitation";
    activateButton(btnRain, [btnTemp, btnRh]);
    updateLegend();
    filterAndRender();
  });

  btnRh.addEventListener("click", () => {
    activeVar = "humidity";
    activateButton(btnRh, [btnTemp, btnRain]);
    updateLegend();
    filterAndRender();
  });

  // Set initial legend
  updateLegend();
}

// Update the legend container HTML dynamically
function updateLegend() {
  const container = document.getElementById("legend-container");
  if (container && legends[activeVar]) {
    container.innerHTML = legends[activeVar];
  }
}

// Change the Leaflet Map Base Layer Style
function setMapStyle(styleKey) {
  if (!map || mapMode === "Windy 動態天氣地圖模式") return;

  if (activeTileLayer) {
    map.removeLayer(activeTileLayer);
  }

  const style = mapStyles[styleKey] || mapStyles.osm;
  activeTileLayer = L.tileLayer(style.url, {
    attribution: style.attribution,
    maxZoom: 19
  }).addTo(map);
}

// App Setup: Config Fetching and Map Initialization
async function setupApp() {
  let windyKey = "";

  try {
    const response = await fetch("/api/config");
    if (response.ok) {
      const config = await response.json();
      windyKey = config.windyApiKey || "";
    }
  } catch (error) {
    console.warn("Could not fetch API configuration, using standard map fallback.", error);
  }

  let mapInitialized = false;

  // Fallback function to initialize standard Leaflet Map
  const initializeStandardMap = () => {
    if (mapInitialized) return;
    mapInitialized = true;
    mapMode = "標準 Leaflet 地圖模式";
    document.getElementById("map-mode-indicator").innerText = mapMode;

    try {
      // Create standard Leaflet map
      map = L.map("windy", {
        zoomControl: true,
        attributionControl: true
      }).setView([23.8, 121.0], 8);

      // Add default tile layer (OSM with Chinese labels)
      setMapStyle("osm");

      // Initialize markers layer
      markersLayer = L.layerGroup().addTo(map);

      // Fetch and display data
      fetchAndRenderData().then(hideLoadingScreen);
    } catch (e) {
      console.error("Failed to initialize standard Leaflet map:", e);
      hideLoadingScreen();
    }
  };

  // Set a 4-second timeout to fall back to standard map if Windy boot fails
  const windyTimeout = setTimeout(() => {
    if (!mapInitialized) {
      console.warn("Windy initialization timed out. Using standard Leaflet map.");
      initializeStandardMap();
    }
  }, 4000);

  // Attempt Windy initialization if a valid key is provided
  const isKeyValid = windyKey && windyKey.trim() !== "" && !windyKey.includes("YOUR_");

  if (isKeyValid && typeof windyInit === "function") {
    try {
      const options = {
        key: windyKey,
        lat: 23.8,
        lon: 121.0,
        zoom: 8,
        overlay: "temp"
      };

      windyInit(options, (windyAPI) => {
        clearTimeout(windyTimeout);
        if (mapInitialized) return;

        map = windyAPI.map;
        mapInitialized = true;
        mapMode = "Windy 動態天氣地圖模式";
        document.getElementById("map-mode-indicator").innerText = mapMode;

        // Disable base map selectors since Windy manages its background
        document.getElementById("map-style-select").disabled = true;

        // Initialize markers layer on top of Windy map
        markersLayer = L.layerGroup().addTo(map);

        // Fetch and display data
        fetchAndRenderData().then(hideLoadingScreen);
      });
    } catch (e) {
      clearTimeout(windyTimeout);
      console.error("Error launching Windy Map API, falling back to standard map:", e);
      initializeStandardMap();
    }
  } else {
    clearTimeout(windyTimeout);
    initializeStandardMap();
  }
}

// Fetch cleaned weather data from server API
async function fetchAndRenderData() {
  try {
    const response = await fetch("/api/cwa-temperature");
    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);

    const data = await response.json();
    allStationsData = data;

    // Populate county filter options
    populateCountySelect(data);

    // Render current filtered list
    filterAndRender();
  } catch (error) {
    console.error("Error fetching weather temperature data:", error);
    alert("無法取得觀測資料，請確認伺服器已啟動或 scraper.py 已執行。");
  }
}

// Populate the County Select Dropdown dynamically
function populateCountySelect(data) {
  const countySelect = document.getElementById("county-select");
  const currentValue = countySelect.value;

  // Extract unique county names, filter out falsy values
  const counties = [...new Set(data.map(item => item.county).filter(Boolean))].sort();

  // Reset and rebuild options
  countySelect.innerHTML = '<option value="all">全部縣市</option>';
  counties.forEach(county => {
    const option = document.createElement("option");
    option.value = county;
    option.textContent = county;
    countySelect.appendChild(option);
  });

  // Keep previous selection if it still exists
  if (counties.includes(currentValue)) {
    countySelect.value = currentValue;
  } else {
    countySelect.value = "all";
  }
}

// Filter data based on search and dropdown selections, then render markers & update stats
function filterAndRender() {
  if (!map || !markersLayer) return;

  const searchQuery = document.getElementById("search-input").value.trim().toLowerCase();
  const selectedCounty = document.getElementById("county-select").value;

  // Filter stations array
  const filteredStations = allStationsData.filter(station => {
    // 1. County filter
    if (selectedCounty !== "all" && station.county !== selectedCounty) {
      return false;
    }
    // 2. Search query filter
    if (searchQuery) {
      const nameMatch = station.stationName && station.stationName.toLowerCase().includes(searchQuery);
      const countyMatch = station.county && station.county.toLowerCase().includes(searchQuery);
      const townMatch = station.town && station.town.toLowerCase().includes(searchQuery);
      const idMatch = station.stationId && station.stationId.toLowerCase().includes(searchQuery);
      return nameMatch || countyMatch || townMatch || idMatch;
    }
    return true;
  });

  // Render Leaflet markers on the map
  renderMarkers(filteredStations);

  // Update statistics dashboard panels
  updateStatistics(filteredStations);
}

// Render Circle Markers for each weather station
function renderMarkers(stations) {
  markersLayer.clearLayers();

  if (!showCwaObservations) {
    return;
  }

  stations.forEach(station => {
    if (station.lat == null || station.lon == null) return;

    // Get value and color depending on selected variable
    let activeVal = null;
    let displayVal = "";
    let displayUnit = "";
    let displayLabel = "";

    if (activeVar === "temperature") {
      activeVal = station.temperature;
      displayVal = activeVal.toFixed(1);
      displayUnit = "°C";
      displayLabel = "氣溫";
    } else if (activeVar === "precipitation") {
      activeVal = station.precipitation != null ? station.precipitation : 0.0;
      displayVal = activeVal.toFixed(1);
      displayUnit = "mm";
      displayLabel = "時雨量";
    } else if (activeVar === "humidity") {
      activeVal = station.humidity;
      displayVal = activeVal != null ? activeVal.toFixed(0) : "無資料";
      displayUnit = activeVal != null ? "%" : "";
      displayLabel = "相對濕度";
    }

    const color = getVarColor(activeVal, activeVar);

    // Create interactive circle marker
    const marker = L.circleMarker([station.lat, station.lon], {
      radius: 9,
      color: "#0f172a", // Dark border for high contrast
      fillColor: color,
      fillOpacity: 0.95,
      weight: 1.5,
      className: "custom-temp-marker"
    });

    // Create custom formatted popup layout
    const popupHtml = `
      <div class="popup-card">
        <div class="popup-header">
          <span class="popup-station-name">${station.stationName}</span>
          <span class="popup-station-id">${station.stationId || ""}</span>
        </div>
        <div class="popup-temp-section">
          <span class="popup-temp-value" style="color: ${color}">${displayVal}</span>
          <span class="popup-temp-unit">${displayUnit}</span>
          <span style="font-size: 0.75rem; color: var(--text-secondary); margin-left: 6px;">(${displayLabel})</span>
        </div>
        <div class="popup-details">
          <div class="popup-detail-row">
            <span>行政區</span>
            <span class="val">${station.county || ""}${station.town || ""}</span>
          </div>
          <div class="popup-detail-row">
            <span>相對濕度</span>
            <span class="val">${station.humidity != null ? station.humidity.toFixed(0) + "%" : "無資料"}</span>
          </div>
          <div class="popup-detail-row">
            <span>氣壓</span>
            <span class="val">${station.pressure != null ? station.pressure.toFixed(1) + " hPa" : "無資料"}</span>
          </div>
          <div class="popup-detail-row">
            <span>時雨量</span>
            <span class="val">${station.precipitation != null ? station.precipitation.toFixed(1) + " mm" : "0.0 mm"}</span>
          </div>
          <div class="popup-detail-row">
            <span>觀測氣溫</span>
            <span class="val">${station.temperature != null ? station.temperature.toFixed(1) + " °C" : "無資料"}</span>
          </div>
        </div>
        <div class="popup-street-view" style="margin-top: 8px; border-top: 1px dashed rgba(255, 255, 255, 0.08); padding-top: 6px; text-align: center;">
          <a href="https://www.google.com/maps/search/?api=1&query=${station.lat},${station.lon}" target="_blank" style="color: #3b82f6; text-decoration: none; font-size: 0.75rem; display: inline-flex; align-items: center; gap: 4px; font-weight: 500;">
            <i class="fa-solid fa-street-view" style="color: #fdae61;"></i> 開啟 Google 街景與地圖
          </a>
        </div>
        <div class="popup-footer">
          更新: ${formatObsTime(station.obsTime)}
        </div>
      </div>
    `;

    marker.bindPopup(popupHtml, {
      closeButton: false,
      offset: L.point(0, -6)
    });
    if (showStationLabels) {
      marker.bindTooltip(
        `${station.stationName} ${displayVal}${displayUnit}`,
        {
          permanent: true,
          direction: "top",
          offset: [0, -10],
          className: "station-label"
        }
      );
    }

    // Hover tooltip/popup bindings for enhanced user interaction
    marker.on("mouseover", function (e) {
      this.openPopup();
    });

    // Add marker to layer group
    marker.addTo(markersLayer);
  });
}

// Update the floating dashboard analytics widgets based on activeVar
function updateStatistics(stations) {
  const totalCount = stations.length;
  document.getElementById("stat-count").innerText = totalCount;

  // Locate the Average Card UI labels
  const avgCard = document.querySelector(".avg-temp");
  const avgLabel = avgCard.querySelector(".stat-label");
  const avgValueSpan = document.getElementById("stat-avg");

  if (totalCount === 0) {
    avgValueSpan.innerHTML = `--.-`;
    document.getElementById("extreme-high-value").innerText = "--.-";
    document.getElementById("extreme-high-station").innerText = "無符合條件的測站";
    document.getElementById("extreme-high-time").innerText = "--:--";
    document.getElementById("extreme-low-value").innerText = "--.-";
    document.getElementById("extreme-low-station").innerText = "無符合條件的測站";
    document.getElementById("extreme-low-time").innerText = "--:--";
    return;
  }

  // Calculate statistics according to activeVar
  let sum = 0;
  let highest = stations[0];
  let lowest = stations[0];
  let unit = "";
  let avgLabelText = "";
  let highBadgeText = "";
  let lowBadgeText = "";

  stations.forEach(s => {
    let sVal = 0;
    let highVal = 0;
    let lowVal = 0;

    if (activeVar === "temperature") {
      sVal = s.temperature;
      highVal = highest.temperature;
      lowVal = lowest.temperature;
      unit = "°C";
      avgLabelText = "均溫";
      highBadgeText = "最高溫";
      lowBadgeText = "最低溫";
    } else if (activeVar === "precipitation") {
      sVal = s.precipitation != null ? s.precipitation : 0.0;
      highVal = highest.precipitation != null ? highest.precipitation : 0.0;
      lowVal = lowest.precipitation != null ? lowest.precipitation : 0.0;
      unit = "mm";
      avgLabelText = "平均雨量";
      highBadgeText = "最多雨";
      lowBadgeText = "最少雨";
    } else if (activeVar === "humidity") {
      sVal = s.humidity != null ? s.humidity : 0.0;
      highVal = highest.humidity != null ? highest.humidity : 0.0;
      lowVal = lowest.humidity != null ? lowest.humidity : 0.0;
      unit = "%";
      avgLabelText = "平均濕度";
      highBadgeText = "最潮濕";
      lowBadgeText = "最乾燥";
    }

    sum += sVal;

    // Evaluate extremes
    if (sVal > highVal) highest = s;
    if (sVal < lowVal) lowest = s;
  });

  const avgValue = sum / totalCount;

  // Render Average UI Panel
  avgLabel.innerText = avgLabelText;
  if (activeVar === "humidity") {
    avgValueSpan.innerHTML = `${avgValue.toFixed(0)}<span class="unit">${unit}</span>`;
  } else {
    avgValueSpan.innerHTML = `${avgValue.toFixed(1)}<span class="unit">${unit}</span>`;
  }

  // Get extreme values for rendering
  let highestVal = 0;
  let lowestVal = 0;
  if (activeVar === "temperature") {
    highestVal = highest.temperature;
    lowestVal = lowest.temperature;
  } else if (activeVar === "precipitation") {
    highestVal = highest.precipitation != null ? highest.precipitation : 0.0;
    lowestVal = lowest.precipitation != null ? lowest.precipitation : 0.0;
  } else if (activeVar === "humidity") {
    highestVal = highest.humidity != null ? highest.humidity : 0.0;
    lowestVal = lowest.humidity != null ? lowest.humidity : 0.0;
  }

  // Render Highest Extreme Station Card
  const highBadge = document.querySelector(".hot-extreme .extreme-badge");
  highBadge.innerText = highBadgeText;
  document.getElementById("extreme-high-value").innerText = activeVar === "humidity" ? `${highestVal.toFixed(0)}${unit}` : `${highestVal.toFixed(1)}${unit}`;
  document.getElementById("extreme-high-station").innerText = `${highest.stationName} (${highest.county || ""})`;
  document.getElementById("extreme-high-time").innerText = formatObsTime(highest.obsTime);

  // Render Lowest Extreme Station Card
  const lowBadge = document.querySelector(".cold-extreme .extreme-badge");
  lowBadge.innerText = lowBadgeText;
  document.getElementById("extreme-low-value").innerText = activeVar === "humidity" ? `${lowestVal.toFixed(0)}${unit}` : `${lowestVal.toFixed(1)}${unit}`;
  document.getElementById("extreme-low-station").innerText = `${lowest.stationName} (${lowest.county || ""})`;
  document.getElementById("extreme-low-time").innerText = formatObsTime(lowest.obsTime);

  // Update top general dashboard update-time display using the latest observation timestamp
  const latestTime = stations.reduce((latest, s) => {
    if (!s.obsTime) return latest;
    return !latest || s.obsTime > latest ? s.obsTime : latest;
  }, "");

  document.getElementById("update-time").innerText = latestTime ? formatObsTime(latestTime) : "--:--";
}

// Format the CWA raw ISO string (e.g. 2026-07-02T10:00:00+08:00) into a cleaner format
function formatObsTime(isoString) {
  if (!isoString) return "--:--";
  try {
    const parts = isoString.split("T");
    if (parts.length < 2) return isoString;

    const timePart = parts[1].substring(0, 5); // Returns HH:MM
    const datePart = parts[0].substring(5);    // Returns MM-DD

    return `${datePart} ${timePart}`;
  } catch (e) {
    return isoString;
  }
}

// Fade out loading screen overlay
function hideLoadingScreen() {
  const loader = document.getElementById("loading-overlay");
  if (loader) {
    loader.style.opacity = "0";
    setTimeout(() => {
      loader.style.visibility = "hidden";
    }, 500);
  }
}
