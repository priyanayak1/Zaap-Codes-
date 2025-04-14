import os
import requests
import psycopg as psycopg
from flask import Flask, render_template, request, jsonify, redirect, url_for
from dotenv import load_dotenv
import chatbot
<<<<<<< HEAD
=======
import auth

>>>>>>> main
from Code import Code
from ChatItem import ChatItem
from scraper import extract_full_pdf_text;


load_dotenv() # loads the environment variables

app = Flask(__name__) # creates the Flask app
app.register_blueprint(auth.bp)

<<<<<<< HEAD
=======
# CODE PAGE DEMO 
# TODO : move to appropriate file
global_codes = [
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

def scrape_county_codes(county_name):
    # Construct the URL for the county's page on the Municode website
    base_url = "https://library.municode.com/ga"
    search_url = f"{base_url}/search?q={county_name.replace(' ', '%20')}"
    
    try:
        # Send a GET request to the search URL
        response = requests.get(search_url)
        response.raise_for_status()  # Raise an error for bad status codes
        
        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find the link to the county's specific page (this selector might need adjustment)
        county_link = soup.find('a', text=lambda t: t and county_name.lower() in t.lower())
        if not county_link:
            print(f"County link not found for {county_name}")
            return []  # Return an empty list if no link is found
        
        # Follow the link to the county's page
        county_page_url = base_url + county_link['href']
        county_page_response = requests.get(county_page_url)
        county_page_response.raise_for_status()
        
        # Parse the county's page to extract codes (this part will vary based on the page structure)
        county_soup = BeautifulSoup(county_page_response.text, 'html.parser')
        codes = []
        
        # Example: Find all elements with a specific class that contains the codes
        for code_element in county_soup.find_all('div', class_='code'):
            codes.append(code_element.text.strip())
        if not codes:
            print(f"No codes found for {county_name}")
        return codes
    except Exception as e:
        print(f"Error scraping codes for {county_name}: {e}")
        return []

>>>>>>> main
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
@app.route('/search', methods=['GET'])
def index():
<<<<<<< HEAD
    return render_template('index.html')

# new page for about us 
@app.route('/about-us')
def about_us():
    return render_template('about_us.html')

# new page for projects  
@app.route('/projects')
def projects():
    return render_template('projects.html')

@app.route('/contact-us')
def contact_us():
    return render_template('contact_us.html')
=======
    codes = global_codes
    app.logger.debug('codes: ' + str(codes))
    return render_template('index.html', codes=codes)
>>>>>>> main

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
    ####
    # commented out the stuff below to hard code it to fulton 
    ###
    jurisdiction, geojson = get_county(lat, lon)
    print(jurisdiction)

    code_info = f"Click below to view the {code_type.replace('_', ' ').title()} Codes."


    return jsonify({
        'jurisdiction': jurisdiction,
        'geojson': geojson,
        'lat': lat,
        'lon': lon,
        # 'county_url': county_url,
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

<<<<<<< HEAD
# runs the app 
if __name__ == '__main__':
    app.run(debug=True, port=5001)
=======
def get_code(id: int) -> Code:
    return global_codes[id]

@app.route('/<int:id>/code_page', methods=['GET'])
def code_page(id):
    code = get_code(id)
    codes = global_codes

    app.logger.debug("opening code page for : " + code.title)

    return render_template(
        'code_page.html',
        code=code,
        global_codes=global_codes
    )

user_codes = []
@app.route('/<int:id>/save_code', methods=['POST', 'GET'])
def save_code(id):
    app.logger.debug("Saving new code.")
    user_codes.append(get_code(id))
    return redirect(url_for("saved"))

@app.route('/saved')
def saved():
    # need to select codes for user
    codes = user_codes
    app.logger.debug(codes)
    return render_template(
        "saved_codes.html",
        codes = codes
    )

@app.route('/zappy', methods=['GET'])
def zappy():
    return render_template('zappy.html')

@app.route('/projects', methods=['GET'])
def projects():
    return render_template('projects.html')

@app.route('/privacy', methods=['GET'])
def privacy():
    return render_template('privacy.html')

# runs the app 
if __name__ == '__main__':
    app.secret_key = 'parangaricutirimicuaro'
    app.run(debug=True, port=5001)
>>>>>>> main
