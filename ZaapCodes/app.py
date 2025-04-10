import os
import requests
import psycopg2 as psycopg
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import chatbot
#from scraper import scrape_fulton_building_code;
from Code import Code
from ChatItem import ChatItem
from scraper import extract_full_pdf_text;

# from bs4 import BeautifulSoup



load_dotenv() # loads the environment variables

app = Flask(__name__) # creates the Flask app

# CODE PAGE DEMO 
# TODO : move to appropriate file
codes = [
    Code(
        title="Code 1 Title",
        short_description="Code 1 short description",
        full_description="Code 1 full description",
        source_link="link to code 1"
    ),
    Code(
        title="Code 2 Title",
        short_description="Code 2 short description",
        full_description="Code 2 full description",
        source_link="link to code 2"
    ),
    Code(
        title="Code 3 Title",
        short_description="Code 3 short description",
        full_description="Code 3 full description",
        source_link="link to code 3"
    )
]

###
# Convers an address into latitude and longitude using the Google Maps Geocoding API
# 1. sends a request to the Google Maps Geocoding API
# 2. parses the JSON response to extract the latitude and longitude
# 3. Returns (lat, lon) if successful; otherwise, returns (None, None).
# @param address: The address to geocode
###
def geocode_address(address):
    url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {
        'address': address,
        'region': 'us',       # Bias results to U.S.
        'components': 'administrative_area:GA|country:US',  # Prefer Georgia addresses
        'key': os.getenv("GOOGLE_API_KEY")
    }

    try:
        response = requests.get(url, params=params)
        data = response.json()

        if data['status'] == 'OK':
            loc = data['results'][0]['geometry']['location']
            return loc['lat'], loc['lng']
        else:
            print(f"Google Geocoding failed: {data['status']}")
            return None, None
    except Exception as e:
        print(f"Error during geocoding: {e}")
        return None, None

def get_county_url(county_name):
    county_name = county_name + '_county'
    # Convert the county name to the format used in the URL
    formatted_name = county_name.lower().replace(" ", "").replace("-", "")
    
    # Construct the URL
    base_url = "https://library.municode.com/ga"
    county_url = f"{base_url}/{formatted_name}/codes/code_of_ordinances"
    #  https://library.municode.com/ga/fulton/codes/code_of_ordinances

    return county_url

###
# Connects to PostgreSQL database using credentials from environment variables
# @return: The database connection object
###
def connect_db():
    return psycopg.connect(
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

# Renders the homepage (index.html).
@app.route('/')
def index():
    app.logger.debug('codes: ' + str(codes))
    return render_template('index.html', codes=codes)

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
    code_type = request.json.get('codeType')
    if not address or not code_type:
        return jsonify({'error': 'Address required'}), 400

    lat, lon = geocode_address(address)
    if lat is None or lon is None:
        return jsonify({'error': 'Failed to geocode address'}), 400

    jurisdiction, geojson = get_county(lat, lon)
    print(jurisdiction)
    county_url = get_county_url(jurisdiction)
    # Always return a JSON response
    #print(county_url)
    # hard coded for now but we will build database or table for this info
    #county_name = jurisdiction.split()[0]  # Simple way to normalize "Fulton County" to "Fulton"
    code_info = f"Click below to view the {code_type.replace('_', ' ').title()} Codes."
# If no manual code found, try scraping
#     if not code_info and county_name == "Fulton" and code_type == "building":
#         code_info = scrape_fulton_building_code()

# # If still nothing found, default error message
#     if not code_info:
#         code_info = "Code information not available for this selection."

    return jsonify({
        'jurisdiction': jurisdiction,
        'geojson': geojson,
        'lat': lat,
        'lon': lon,
        'county_url': county_url,
        'code_type': code_type,
        'code_info': code_info
    }), 200

code_type_to_pdf = {
    "building": "IBC 2025 Amendments.pdf",
    "residential": "irc_2024_amendments.pdf",
    "plumbing": "ipc_2024_amendments.pdf",
    "mechanical": "imc_2024_amendments.pdf",
    "fuel_gas": "ifgc_2022_amendments.pdf",
    "energy_conservation": "iecc_2024_amendments.pdf"
}

@app.route('/codes/<code_type>')
def code_page(code_type):
    pdf_filename = code_type_to_pdf.get(code_type)

    if not pdf_filename:
        return "Invalid code type.", 404
    county_name = request.args.get('county', 'Georgia') # default Georgia if a real county name has not been passed in
    pdf_path = f"pdfs/{pdf_filename}"
    full_text = extract_full_pdf_text(pdf_path)

    return render_template('building_codes.html', full_text=full_text, code_type=code_type, county_name = county_name, code_type_to_pdf=code_type_to_pdf) 

# def get_code(id: int) -> Code:
#     return codes[id]

# @app.route('/<int:id>/code_page', methods=['GET'])
# def specific_code_page(id):
#     code = get_code(id)

#     app.logger.debug("opening code page for : " + code.title)

#     return render_template(
#         'code_page.html',
#         code=code
#     )

# CHAT STUFF   

# openai.api_key = os.getenv("OPENAI_API_KEY")  # Store API key in .env
# TODO: scroll down to bottom of chatbox
# TODO: save chats
# TODO: add context when on code page
# TODO: add suggestions
# TODO: error handling
chat_items = []
@app.route('/chat', methods=['POST'])
def chat():
    app.logger.debug("/chat/request :", request.form['chat-input'])
    response = chatbot.simple_request_gemini(request.form['chat-input'])
    app.logger.debug("ChatBot Response: ", response)

    chat_items.append(
        ChatItem(text=request.form['chat-input'], item_type='user')
    )
    chat_items.append(
        ChatItem(text=response, item_type='bot')
    )

    # TODO: ideally we should refresh the chatbot box instead of the whole page somehow
    return render_template('index.html', chat_items=chat_items, chatbot_open=True)

# runs the app 
if __name__ == '__main__':
    app.run(debug=True, port=5001)
