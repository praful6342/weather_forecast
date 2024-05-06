from flask import Flask, render_template, request, jsonify
from flask_mail import Mail, Message
import os
import requests
import logging
import geocoder
import pandas as pd
from sklearn.cluster import KMeans

# Load the weather data from data.csv
weather_data = pd.read_csv('data.csv')

# Apply k-means clustering
kmeans = KMeans(n_clusters=3, random_state=0)  # You can adjust the number of clusters as needed
# Extract the feature columns
X = weather_data[['temperature', 'humidity', 'pressure', 'windspeed']].values
kmeans.fit(X)

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your_secret_key')

OPENWEATHER_API_KEY = os.environ.get('OPENWEATHER_API_KEY', '545cf9247039c6d223ef47c8b2417059')
NEWS_API_KEY = os.environ.get('NEWS_API_KEY', '20def5e8a6204946af3526923e0b790d')

logging.basicConfig(filename='app.log', level=logging.ERROR, format='%(asctime)s %(levelname)s: %(message)s')

@app.route("/", methods=["GET"])
def index():
    try:
        location = geocoder.ip('me')
        latitude = location.latlng[0]
        longitude = location.latlng[1]

        current_weather_data = get_current_weather(latitude, longitude, OPENWEATHER_API_KEY)
        weather_data = parse_weather_data(current_weather_data)

        # Determine the weather icon based on the weather description
        if weather_data['weather'].lower() in ['clear', 'sunny']:
            weather_icon = 'sunny.png'
        elif weather_data['weather'].lower() in ['clouds', 'cloudy']:
            weather_icon = 'cloudy.png'
        elif weather_data['weather'].lower() in ['rain', 'rainy']:
            weather_icon = 'rainy.png'
        elif weather_data['weather'].lower() in ['snow', 'snowy']:
            weather_icon = 'snowy.png'
        else:
            weather_icon = 'unknown.png'

        return render_template("index.html", weather_data=weather_data, weather_icon=weather_icon)

    except Exception as e:
        logging.error(f"Error: {e}")
        return render_template("404.html")

@app.route("/news")
def show_news():
    news_data = get_weather_news(NEWS_API_KEY)
    return render_template("news.html", news_data=news_data)

@app.route("/predict", methods=["GET", "POST"])
def predict_weather():
    predicted_weather = ""  # Initialize predicted_weather variable
    if request.method == "POST":
        form_data = request.form.to_dict()
        predicted_weather = perform_weather_prediction(form_data)
    return render_template("predict.html", predicted_weather=predicted_weather)

@app.route("/weather_alerts")
def weather_alerts():
    alert_data = get_weather_alerts()  # Function to fetch weather alerts from the API
    return render_template("weather_alerts.html", alert_data=alert_data)

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

def perform_weather_prediction(form_data):
    # Use the k-means model to predict the cluster for the input data
    input_data = [form_data['temperature'], form_data['humidity'], form_data['pressure'], form_data['windspeed']]
    cluster = kmeans.predict([input_data])[0]

    # Based on the cluster, assign a weather prediction
    if cluster == 0:
        return "Sunny"
    elif cluster == 1:
        return "Cloudy"
    else:
        return "Rainy"

def get_current_weather(lat, lon, api_key):
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        current_weather_data = response.json()
        return current_weather_data
    except requests.exceptions.RequestException as e:
        logging.error(f"Error retrieving weather data: {e}")
        return None
    
def get_weather_alerts():
    # Make API request to fetch weather alerts
    alert_api_url = 'YOUR_WEATHER_ALERT_API_URL'
    api_key = 'YOUR_WEATHER_ALERT_API_KEY'
    
    params = {
        'key': api_key,
        'location': 'Bangalore',  # Example location
    }

    response = requests.get(alert_api_url, params=params)
    if response.status_code == 200:
        alert_data = response.json()
        return alert_data
    else:
        logging.error(f"Error fetching weather alerts: {response.text}")
        return None

def parse_weather_data(data):
    if not data:
        return {
            "weather": "Error",
            "description": "",
            "temperature": None,
            "humidity": None,
            "wind_speed": None,
            "pressure": None,
        }

    temperature = data["main"].get("temp")
    if temperature is None:
        temperature = None
    else:
        temperature = temperature - 273.15

    humidity = data["main"].get("humidity")
    wind_speed = data["wind"].get("speed")
    pressure = data["main"].get("pressure")

    return {
        "weather": data["weather"][0]["main"],
        "description": data["weather"][0]["description"],
        "temperature": temperature,
        "humidity": humidity,
        "wind_speed": wind_speed,
        "pressure": pressure,
    }

def get_weather_news(api_key):
    url = f"https://newsapi.org/v2/top-headlines?country=us&category=weather&apiKey={api_key}"
    params = {
        'apiKey': api_key,
        'q': 'weather',  # Search query for weather-related news
        'sortBy': 'publishedAt',  # Sort by publication date
        'language': 'en',  # Specify language (e.g., English)
        'pageSize': 10  # Number of articles to retrieve
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        news_data = response.json()
        if news_data.get('status') == 'ok':
            print(news_data)
            return news_data
        else:
            logging.error(f"Error retrieving news data: {news_data.get('message', 'Unknown error')}")
            return None
    except requests.exceptions.RequestException as e:
        logging.error(f"Error retrieving news data: {e}")
        return None
    except Exception as e:
        logging.error(f"Unexpected error retrieving news data: {e}")
        return None

if __name__ == "__main__":
    app.run(debug=True)