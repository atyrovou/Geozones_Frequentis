from flask import Flask, jsonify
import requests

app = Flask(__name__)

CLIENT_ID = "mu-utm-sales"
CLIENT_SECRET = "lcjiTTVmssAqKX4RqwfpwVw8wYTw0ebx"

TOKEN_URL = "https://test.utm-labs-frequentis.com/keycloak/auth/realms/swim/protocol/openid-connect/token"
ZONE_URL = "https://test.utm-labs-frequentis.com/ras-manager/api/3.0.0/uas-zones"


def get_token():
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "User-Agent": "curl/8.0",
        "Accept": "*/*"
    }

    data = {
        "grant_type": "client_credentials",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET
    }

    response = requests.post(TOKEN_URL, headers=headers, data=data)
    response.raise_for_status()
    return response.json()["access_token"]


@app.get("/zone/<country>/<identifier>")
def get_zone(country, identifier):
    token = get_token()
    headers = {"Authorization": f"Bearer {token}"}

    url = f"{ZONE_URL}/{country}/{identifier}"
    response = requests.get(url, headers=headers)
    response.raise_for_status()

    return jsonify(response.json())


@app.get("/zones/bergen")
def get_zones_bergen():
    token = get_token()
    headers = {"Authorization": f"Bearer {token}"}

    zone_ids = ["NOR001", "NORAIR1"]
    features = []

    for zid in zone_ids:
        url = f"{ZONE_URL}/NOR/{zid}"
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            data = response.json()
            features.append(data["features"][0])

    return jsonify({
        "type": "FeatureCollection",
        "features": features
    })


@app.get("/map")
def map_view():
    return """
<!DOCTYPE html>
<html>
<head>
    <title>Bergen GeoZones</title>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0">

    <link rel="stylesheet"
          href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />

    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>

    <style>
        #map { height: 100vh; }
    </style>
</head>
<body>

<div id="map"></div>

<script>
    var map = L.map('map').setView([60.30, 5.22], 11);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19
    }).addTo(map);

    fetch('/zones/bergen')
        .then(response => response.json())
        .then(data => {
            data.features.forEach(feature => {
                var coords = feature.geometry.coordinates[0].map(function(c) {
                    return [c[1], c[0]];
                });

                var polygon = L.polygon(coords, {
                    color: 'red',
                    weight: 2
                }).addTo(map);

                polygon.bindPopup(feature.properties.name[0].text);
            });
        });
</script>

</body>
</html>
"""

app.run(port=5000)