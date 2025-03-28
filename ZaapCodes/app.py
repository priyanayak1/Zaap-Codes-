import os
import requests
import psycopg
import openai
from flask import Flask, render_template, request, jsonify, redirect, url_for
from dotenv import load_dotenv

# from bs4 import BeautifulSoup

from bs4 import BeautifulSoup

import chatbot
import code_lookup

# my api key
# GOOGLE_API_KEY=AIzaSyB9csfU7JVByjXZTZjRFHlHPuHoQGRTgu0

load_dotenv() # loads the environment variables

app = Flask(__name__) # creates the Flask app

# def scrape_county_codes(county_name):
#     # Construct the URL for the county's page on the Municode website
#     base_url = "https://library.municode.com/ga"
#     search_url = f"{base_url}/search?q={county_name.replace(' ', '%20')}"
    
#     try:
#         # Send a GET request to the search URL
#         response = requests.get(search_url)
#         response.raise_for_status()  # Raise an error for bad status codes
        
#         # Parse the HTML content
#         soup = BeautifulSoup(response.text, 'html.parser')
        
#         # Find the link to the county's specific page (this selector might need adjustment)
#         county_link = soup.find('a', text=lambda t: t and county_name.lower() in t.lower())
#         if not county_link:
#             print(f"County link not found for {county_name}")
#             return []  # Return an empty list if no link is found
        
#         # Follow the link to the county's page
#         county_page_url = base_url + county_link['href']
#         county_page_response = requests.get(county_page_url)
#         county_page_response.raise_for_status()
        
#         # Parse the county's page to extract codes (this part will vary based on the page structure)
#         county_soup = BeautifulSoup(county_page_response.text, 'html.parser')
#         codes = []
        
#         # Example: Find all elements with a specific class that contains the codes
#         for code_element in county_soup.find_all('div', class_='code'):
#             codes.append(code_element.text.strip())
#         if not codes:
#             print(f"No codes found for {county_name}")
#         return codes
#     except Exception as e:
#         print(f"Error scraping codes for {county_name}: {e}")
#         return []

    # url = "https://nominatim.openstreetmap.org/search"
    # params = {
    #     "q": address,
    #     "format": "json",
    #     "limit": 1
    # }
    # headers = {
    #     "User-Agent": "YourApp/1.0 (you@example.com)"
    # }

    # try:
    #     response = requests.get(url, params=params, headers=headers)
    #     response.raise_for_status()
    #     data = response.json()

    #     if not data:
    #         print("No results from geocoder.")
    #         return None, None

    #     lat = float(data[0]['lat'])
    #     lon = float(data[0]['lon'])
    #     return lat, lon
    # except Exception as e:
    #     print(f"Error during geocoding: {e}")
    #     return None, None


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
        return f"Connected! {count} rows in Counties2018."
    except Exception as e:
        return f"Database connection failed: {e}"

# Renders the homepage (index.html).
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/lookup', methods=['POST'])
def lookup():
    return code_lookup.simple_lookup(request.json.get('address'))


# CHAT STUFF   

openai.api_key = os.getenv("OPENAI_API_KEY")  # Store API key in .env

@app.route('/chat', methods=['POST'])
def chat():
    app.logger.debug("/chat/request :", request.form['chat-input'])
    response = chatbot.simple_request(request.form['chat-input'])
    app.logger.debug("ChatBot Response: ", response)

    # TODO: this should probably be a global type
    chat_items = []
    chat_items.append(response)

    # TODO: ideally we should refresh the chatbot box instead of the whole page somehow
    return render_template('index.html', chat_items=chat_items, chatbot_open=True)

# runs the app 
if __name__ == '__main__':
    app.run(debug=True, port=5001, host="0.0.0.0")
