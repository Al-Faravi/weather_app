from flask import Flask, render_template, request, jsonify
import requests
from datetime import datetime
import google.generativeai as genai

app = Flask(__name__)

# --- API Configuration ---
# 1. OpenWeatherMap API Key
OWM_API_KEY = "b140d4764e7e30ec785c37515da8ea5d"

# 2. Google Gemini API Key
GEMINI_API_KEY = "AIzaSyByv_7z9rCMmtVc4reEueUb69n9u5k5iuQ"

# AI কনফিগারেশন (Safe Mode: using alias)
try:
    genai.configure(api_key=GEMINI_API_KEY)
    
    # 'gemini-flash-latest' ব্যবহার করছি কারণ এটি আপনার লিস্টে আছে
    # এবং এটি অটোমেটিক স্টেবল ভার্সন ব্যবহার করবে।
    model = genai.GenerativeModel('gemini-flash-latest') 
    
except Exception as e:
    print(f"Gemini Config Error: {e}")


# --- Helper Functions ---

def get_aqi_status(aqi_value):
    if aqi_value == 1: return "Good", "#00e676"
    elif aqi_value == 2: return "Fair", "#f1c40f"
    elif aqi_value == 3: return "Moderate", "#e67e22"
    elif aqi_value == 4: return "Poor", "#e74c3c"
    elif aqi_value == 5: return "Hazardous", "#8e44ad"
    return "Unknown", "#95a5a6"

def check_weather_alerts(weather_main, wind_speed, visibility, temp):
    alerts = []
    if "Rain" in weather_main:
        alerts.append("Rainy conditions expected. Don't forget your umbrella! ☔")
    elif "Thunderstorm" in weather_main:
        alerts.append("Thunderstorm warning! Stay indoors if possible. ⚡")
    elif "Snow" in weather_main:
        alerts.append("Snowfall alert. Drive carefully. ❄️")
    
    if wind_speed > 20:
        alerts.append("High wind speeds detected. Be cautious. 💨")
    if visibility < 1.0:
        alerts.append("Low visibility alert due to fog or haze. 🌫️")
    if temp > 38:
        alerts.append("Extreme heat warning. Stay hydrated. ☀️")
        
    return alerts


# --- Routes ---

@app.route('/', methods=['GET', 'POST'])
def home():
    weather_data = None
    forecast_list = []
    hourly_labels = []
    hourly_data = []
    aqi_data = None
    alerts = []
    error_msg = None
    
    city = request.form.get('city')
    if not city and request.method == 'GET':
        city = "Dhaka"

    if city:
        try:
            geo_url = f"http://api.openweathermap.org/geo/1.0/direct?q={city}&limit=1&appid={OWM_API_KEY}"
            geo_res = requests.get(geo_url).json()

            if not geo_res:
                raise Exception("City not found")

            lat = geo_res[0]['lat']
            lon = geo_res[0]['lon']

            weather_url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={OWM_API_KEY}&units=metric"
            forecast_url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={OWM_API_KEY}&units=metric"
            aqi_url = f"http://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={OWM_API_KEY}"

            curr_res = requests.get(weather_url).json()
            fore_res = requests.get(forecast_url).json()
            aqi_res = requests.get(aqi_url).json()

            if 'list' in aqi_res:
                aqi_val = aqi_res['list'][0]['main']['aqi']
                aqi_desc, aqi_color = get_aqi_status(aqi_val)
                aqi_data = {'aqi': aqi_val, 'desc': aqi_desc, 'color': aqi_color}

            weather_main = curr_res['weather'][0]['main']
            temp = round(curr_res['main']['temp'])
            wind_speed = curr_res['wind']['speed']
            visibility_km = round(curr_res.get('visibility', 0) / 1000, 1)

            alerts = check_weather_alerts(weather_main, wind_speed, visibility_km, temp)

            weather_data = {
                'city': geo_res[0]['name'],
                'country': geo_res[0]['country'],
                'lat': lat,
                'lon': lon,
                'temp': temp,
                'desc': curr_res['weather'][0]['description'].title(),
                'main_condition': weather_main.lower(),
                'icon': curr_res['weather'][0]['icon'],
                'humidity': curr_res['main']['humidity'],
                'wind': wind_speed,
                'pressure': curr_res['main']['pressure'],
                'visibility': visibility_km,
                'feels_like': round(curr_res['main']['feels_like'])
            }

            for item in fore_res['list'][:8]:
                hour = datetime.fromtimestamp(item['dt']).strftime('%I %p')
                hourly_labels.append(hour)
                hourly_data.append(round(item['main']['temp']))

            seen_days = set()
            for item in fore_res['list']:
                day_name = datetime.fromtimestamp(item['dt']).strftime('%a')
                if day_name not in seen_days and day_name != datetime.now().strftime('%a'):
                    forecast_list.append({
                        'day': day_name,
                        'temp': round(item['main']['temp']),
                        'icon': item['weather'][0]['icon']
                    })
                    seen_days.add(day_name)
                if len(forecast_list) == 5: break

        except Exception as e:
            print(f"Error fetching data: {e}")
            error_msg = "City not found. Please check the spelling and try again."

    return render_template('index.html', 
                           weather=weather_data, 
                           forecast=forecast_list, 
                           hourly_labels=hourly_labels, 
                           hourly_data=hourly_data,
                           aqi=aqi_data,
                           alerts=alerts,
                           error=error_msg)


@app.route('/ask_ai', methods=['POST'])
def ask_ai():
    try:
        data = request.json
        user_question = data.get('question')
        weather_context = data.get('context')
        
        prompt = f"""
        You are 'WeatherBot', a smart AI assistant.
        Current Weather Data: {weather_context}
        User's Question: "{user_question}"
        
        Instructions:
        1. Answer based on the weather data.
        2. Keep it short and friendly with emojis.
        """
        
        response = model.generate_content(prompt)
        return jsonify({'answer': response.text})
        
    except Exception as e:
        print(f"AI Error: {e}")
        # ক্লায়েন্টকে ক্লিন এরর দেখানো
        return jsonify({'answer': "সার্ভার বিজি আছে (Rate Limit)। ১০ সেকেন্ড পর আবার চেষ্টা করুন। ⏳"}), 500


if __name__ == '__main__':
    app.run(debug=True)