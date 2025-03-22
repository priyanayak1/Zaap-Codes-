import os
import requests
import psycopg2
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv

load_dotenv() # loads the environment variables

app = Flask(__name__) # creates the Flask app

###
# Convers an address into latitude and longitude using the Google Maps Geocoding API
# 1. sends a request to the Google Maps Geocoding API
# 2. parses the JSON response to extract the latitude and longitude
# 3. Returns (lat, lon) if successful; otherwise, returns (None, None).
# @param address: The address to geocode
###

def geocode_address(address):
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": address,
        "format": "json",
        "limit": 1
    }
    headers = {
        "User-Agent": "YourApp/1.0 (you@example.com)"
    }

    try:
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        data = response.json()

        if not data:
            print("No results from geocoder.")
            return None, None

        lat = float(data[0]['lat'])
        lon = float(data[0]['lon'])
        return lat, lon
    except Exception as e:
        print(f"Error during geocoding: {e}")
        return None, None


# def geocode_address(address):
#     url = "https://maps.googleapis.com/maps/api/geocode/json"
#     params = {'address': address, 'key': os.getenv("GOOGLE_API_KEY")}
#     response = requests.get(url, params=params)
#     data = response.json()
#     if data['status'] == 'OK':
#         loc = data['results'][0]['geometry']['location']
#         return loc['lat'], loc['lng']
#     return None, None

###
# Connects to PostgreSQL database using credentials from environment variables
# @return: The database connection object
###
def connect_db():
    return psycopg2.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT")
    )

@app.route('/test-db')
def test_db():
    try:
        conn = connect_db()
        cur = conn.cursor()
        cur.execute('SELECT COUNT(*) FROM "Counties2018";')
        count = cur.fetchone()[0]
        cur.close()
        conn.close()
        return f"✅ Connected! {count} rows in Counties2018."
    except Exception as e:
        return f"❌ Database connection failed: {e}"


def get_county(lat, lon):
    conn = connect_db()
    cur = conn.cursor()

    sql = (
        'SELECT "NAME", ST_AsGeoJSON(geom) '
        'FROM "Counties2018" '
        'WHERE ST_Intersects('
        '  geom, '
        '  ST_SetSRID(ST_Point(%s, %s), 4326)'
        ');'
    )

    print(f"🔎 Querying for point (lon, lat): ({lon}, {lat})")

    try:
        cur.execute(sql, (lon, lat))
        result = cur.fetchone()
        print(f"🧠 Query result: {result}")
    except Exception as e:
        print(f"❌ Database query failed: {e}")
        result = None
    finally:
        cur.close()
        conn.close()

    if result:
        return result[0], result[1]
    else:
        return "No county found", None



# def get_county(lat, lon):
#     conn = connect_db()
#     cur = conn.cursor()

#     sql = """
#         SELECT "name", ST_AsGeoJSON(geom)
#         FROM "Counties2018"
#         WHERE ST_Contains(
#             geom,
#             ST_SetSRID(ST_Point(%s, %s), 4326)
#         );
#     """

#     try:
#         cur.execute(sql, (lon, lat))  # note: lon first!
#         result = cur.fetchone()
#     except Exception as e:
#         print(f"Database error: {e}")
#         result = None
#     finally:
#         cur.close()
#         conn.close()

#     if result:
#         return result[0], result[1]  # county name, geojson
#     else:
#         return "No county found", None

###
# Purpose: Finds the jurisdiction (e.g., county) for a given latitude and longitude.
# Steps:
# 1. Connects to the database.
# 2. Executes a spatial query to check which jurisdiction contains the point (lat, lon).
# 3. Returns the jurisdiction name and its geometry in GeoJSON format.
# 4. Closes the database connection.
###
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
    # if no jursidiction found, return None, None
    if result:
        return result[0], result[1]
    else: 
        # hardcode a default jurisdiction for now
        default_jurisdiction = 'Fulton County'
        default_geojson = '{"type":"Polygon","coordinates":[[[32.0179692,-081.4385431]]]}'
        return default_jurisdiction, default_geojson
    return None, None

###
# Purpose: Retrieves construction codes for a given jurisdiction.
# Steps:
# 1. Connects to the database.
# 2. Executes a query to fetch all construction codes for the jurisdiction.
# 3. Returns a list of code descriptions.
# 4. Closes the database connection.
###
# def get_codes(jurisdiction_name):
#     conn = connect_db()
#     cur = conn.cursor()
#     cur.execute(
#         "SELECT code_description FROM construction_codes WHERE jurisdiction_name = %s;",
#         (jurisdiction_name,)
#     )
#     codes = [row[0] for row in cur.fetchall()]
#     cur.close()
#     conn.close()
#     return codes

# Renders the homepage (index.html).
@app.route('/')
def index():
    return render_template('index.html')

###
# Purpose: handles address lookup request 
# steps: 
# 1. Extracts the address from the request's JSON payload.
# 2. Geocodes the address to get latitude and longitude.
# 3. Finds the jurisdiction for the given latitude and longitude.
# 4. Retrieves construction codes for the jurisdiction.
# 5. Returns a JSON response containing the jurisdiction name, GeoJSON geometry, and construction codes.
###
@app.route('/lookup', methods=['POST'])
def lookup():
    address = request.json.get('address')
    if not address:
        return jsonify({'error': 'Address required'}), 400

    lat, lon = geocode_address(address)
    if lat is None or lon is None:
        return jsonify({'error': 'Failed to geocode address'}), 400

    jurisdiction, geojson = get_county(lat, lon)

    # Always return a JSON response
    return jsonify({
        'jurisdiction': jurisdiction,
        'geojson': geojson,
        'lat': lat,
        'lon': lon
    }), 200
    # codes = get_codes(jurisdiction)
# runs the app 
if __name__ == '__main__':
    app.run(debug=True)
