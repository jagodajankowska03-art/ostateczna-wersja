from flask import Flask, render_template, request
import folium
import requests
import json
app = Flask(__name__, template_folder='.')
CACHE_FILE = 'cache.json'
# Wczytanie cache współrzędnych
try:
    with open(CACHE_FILE, 'r') as f:
        cache = json.load(f)
except:
    cache = {}
def geocode(adres):
    if adres in cache:
        return cache[adres]
    url = f"https://nominatim.openstreetmap.org/search?q={adres}&format=json"
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        r = response.json()
    except (ValueError, requests.exceptions.RequestException):
        r = []
    if r:
        lat = float(r[0]['lat'])
        lon = float(r[0]['lon'])
        cache[adres] = (lat, lon)
        with open(CACHE_FILE, 'w') as f:
            json.dump(cache, f)
        return lat, lon
    return None, None
@app.route("/", methods=['GET', 'POST'])
def index():
    map_html = None
    if request.method == 'POST':
        addresses = request.form.getlist('adres')
        coords = []
        for a in addresses:
            lat, lon = geocode(a)
            if lat is not None and lon is not None:
                coords.append((a, lat, lon))
        if coords:
            m = folium.Map(location=[coords[0][1], coords[0][2]], zoom_start=12)
            colors = ['red', 'blue', 'green']
            driver_coords = [[], [], []]
            for i, point in enumerate(coords):
                driver_coords[i % 3].append(point)
            for idx, driver in enumerate(driver_coords):
                color = colors[idx]
                for adres, lat, lon in driver:
                    folium.Marker([lat, lon], popup=f"Kierowca {idx+1}: {adres}",
                                  icon=folium.Icon(color=color)).add_to(m)
                if len(driver) >= 2:
                    folium.PolyLine([(lat, lon) for _, lat, lon in driver],
                                    color=color, weight=4, opacity=0.7).add_to(m)
            map_html = m._repr_html_()
    return render_template('index.html', map_html=map_html)
if __name__ == "__main__":
    app.run(debug=True)







