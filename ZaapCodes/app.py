import os
import requests
import psycopg2
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

def geocode_address(address):
    url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {'address': address, 'key': os.getenv("GOOGLE_API_KEY")}
    response = requests.get(url, params=params)
    data = response.json()
    if data['status'] == 'OK':
        loc = data['results'][0]['geometry']['location']
        return loc['lat'], loc['lng']
    return None, None

def connect_db():
    return psycopg2.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT")
    )

def find_jurisdiction(lat, lon):
    conn = connect_db()
    cur = conn.cursor()
    query = """
    SELECT name, ST_AsGeoJSON(geom)
    FROM georgia_counties
    WHERE ST_Contains(geom, ST_SetSRID(ST_MakePoint(%s, %s), 4326));
    """
    cur.execute(query, (lon, lat))
    result = cur.fetchone()
    cur.close()
    conn.close()
    if result:
        return result[0], result[1]
    return None, None

def get_codes(jurisdiction_name):
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("SELECT code_description FROM construction_codes WHERE jurisdiction_name = %s;", (jurisdiction_name,))
    codes = [row[0] for row in cur.fetchall()]
    cur.close()
    conn.close()
    return codes

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/lookup', methods=['POST'])
def lookup():
    address = request.json['address']
    lat, lon = geocode_address(address)
    if lat is None:
        return jsonify({'error': 'Invalid address'}), 400

    jurisdiction, geojson = find_jurisdiction(lat, lon)
    if not jurisdiction:
        return jsonify({'error': 'Jurisdiction not found'}), 404

    codes = get_codes(jurisdiction)
    return jsonify({
        'jurisdiction': jurisdiction,
        'geojson': geojson,
        'codes': codes
    })

if __name__ == '__main__':
    app.run(debug=True)
