from flask import Flask, request
import folium
import requests
import math
app = Flask(__name__)
def geocode(address):
    url = "https://nominatim.openstreetmap.org/search"
    params = {"q": address, "format": "json"}
    headers = {"User-Agent": "debiut-kierowcy"}
    r = requests.get(url, params=params, headers=headers, timeout=5)
    data = r.json()
    if not data:
        return None
    return float(data[0]["lat"]), float(data[0]["lon"])
def distance(a, b):
    return math.sqrt((a[0]-b[0])**2 + (a[1]-b[1])**2)
def optimize(points):
    route = [points.pop(0)]
    while points:
        last = route[-1]
        next_point = min(points, key=lambda p: distance(last[1:], p[1:]))
        route.append(next_point)
        points.remove(next_point)
    return route
@app.route("/", methods=["GET", "POST"])
def index():
    html = """
    <form method="POST">
        <textarea name="addresses" rows="10" cols="60"
        placeholder="Każdy adres w nowej linii"></textarea><br>
        <button type="submit">Generuj trasy</button>
    </form>
    """
    if request.method == "POST":
        raw = request.form["addresses"].splitlines()
        points = []
        for a in raw:
            geo = geocode(a)
            if geo:
                points.append((a, geo[0], geo[1]))
        if len(points) < 2:
            return html + "<p>Za mało poprawnych adresów</p>"
        drivers = [[], [], []]
        for i, p in enumerate(points):
            drivers[i % 3].append(p)
        m = folium.Map(location=[points[0][1], points[0][2]], zoom_start=11)
        colors = ["red", "blue", "green"]
        for i, driver in enumerate(drivers):
            if len(driver) < 2:
                continue
            route = optimize(driver.copy())
            folium.PolyLine(
                [(p[1], p[2]) for p in route],
                color=colors[i],
                weight=5
            ).add_to(m)
            for p in route:
                folium.Marker([p[1], p[2]],
                    popup=f"Kierowca {i+1}<br>{p[0]}",
                    icon=folium.Icon(color=colors[i])
                ).add_to(m)
        html += m._repr_html_()
    return html
if __name__ == "__main__":
    app.run()










