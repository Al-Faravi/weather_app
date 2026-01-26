from flask import Flask, render_template, request
import requests
from datetime import datetime

app = Flask(__name__)

# OpenWeatherMap API Key
API_KEY = "b140d4764e7e30ec785c37515da8ea5d"

def get_aqi_status(aqi_value):
    """AQI ভ্যালু অনুযায়ী কালার এবং ডেসক্রিপশন রিটার্ন করবে"""
    if aqi_value == 1: return "Good", "#00e676"      # Green
    elif aqi_value == 2: return "Fair", "#f1c40f"      # Yellow
    elif aqi_value == 3: return "Moderate", "#e67e22"  # Orange
    elif aqi_value == 4: return "Poor", "#e74c3c"      # Red
    elif aqi_value == 5: return "Hazardous", "#8e44ad" # Purple
    return "Unknown", "#95a5a6"

def check_weather_alerts(weather_main, wind_speed, visibility, temp):
    """আবহাওয়ার কন্ডিশন চেক করে অ্যালার্ট জেনারেট করবে"""
    alerts = []
    
    # বৃষ্টির অ্যালার্ট
    if "Rain" in weather_main:
        alerts.append("Rainy conditions expected. Don't forget your umbrella! ☔")
    elif "Thunderstorm" in weather_main:
        alerts.append("Thunderstorm warning! Stay indoors if possible. ⚡")
    elif "Snow" in weather_main:
        alerts.append("Snowfall alert. Drive carefully. ❄️")
    
    # অন্যান্য অ্যালার্ট
    if wind_speed > 20: # ২০ কিমি/ঘ এর বেশি বাতাস
        alerts.append("High wind speeds detected. Be cautious. 💨")
    
    if visibility < 1.0: # ১ কিমি এর কম দৃশ্যমানতা
        alerts.append("Low visibility alert due to fog or haze. 🌫️")
        
    if temp > 38:
        alerts.append("Extreme heat warning. Stay hydrated. ☀️")
        
    return alerts

@app.route('/', methods=['GET', 'POST'])
def home():
    # ভেরিয়েবল ইনিশিয়ালাইজেশন
    weather_data = None
    forecast_list = []
    hourly_labels = []
    hourly_data = []
    aqi_data = None
    alerts = []
    error_msg = None
    
    # ইনপুট সিটি নেওয়া
    city = request.form.get('city')
    
    # যদি ইউজার কিছু না লেখে, ডিফল্ট হিসেবে 'Dhaka' দেখাবে
    if not city and request.method == 'GET':
        city = "Dhaka"

    if city:
        try:
            # ১. জিওকোডিং API (শহর থেকে অক্ষাংশ ও দ্রাঘিমাংশ বের করা)
            geo_url = f"http://api.openweathermap.org/geo/1.0/direct?q={city}&limit=1&appid={API_KEY}"
            geo_res = requests.get(geo_url).json()

            if not geo_res:
                raise Exception("City not found")

            lat = geo_res[0]['lat']
            lon = geo_res[0]['lon']

            # ২. আবহাওয়া, ফোরকাস্ট এবং AQI ডাটা ফেচ করা
            weather_url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"
            forecast_url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"
            aqi_url = f"http://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={API_KEY}"

            curr_res = requests.get(weather_url).json()
            fore_res = requests.get(forecast_url).json()
            aqi_res = requests.get(aqi_url).json()

            # --- ৩. ডাটা প্রসেসিং ---

            # AQI (Air Quality)
            if 'list' in aqi_res:
                aqi_val = aqi_res['list'][0]['main']['aqi']
                aqi_desc, aqi_color = get_aqi_status(aqi_val)
                aqi_data = {
                    'aqi': aqi_val,
                    'desc': aqi_desc,
                    'color': aqi_color
                }

            # বর্তমান আবহাওয়া
            weather_main = curr_res['weather'][0]['main']
            temp = round(curr_res['main']['temp'])
            wind_speed = curr_res['wind']['speed']
            visibility_km = round(curr_res.get('visibility', 0) / 1000, 1)

            # অ্যালার্ট চেক করা
            alerts = check_weather_alerts(weather_main, wind_speed, visibility_km, temp)

            weather_data = {
                'city': geo_res[0]['name'],
                'country': geo_res[0]['country'],
                'lat': lat,  # ম্যাপের জন্য অক্ষাংশ পাঠানো হলো
                'lon': lon,  # ম্যাপের জন্য দ্রাঘিমাংশ পাঠানো হলো
                'temp': temp,
                'desc': curr_res['weather'][0]['description'].title(),
                'main_condition': weather_main.lower(), # CSS ব্যাকগ্রাউন্ডের জন্য
                'icon': curr_res['weather'][0]['icon'],
                'humidity': curr_res['main']['humidity'],
                'wind': wind_speed,
                'pressure': curr_res['main']['pressure'],
                'visibility': visibility_km,
                'feels_like': round(curr_res['main']['feels_like'])
            }

            # গ্রাফের ডাটা (পরবর্তী ২৪ ঘণ্টা - ৮টি পয়েন্ট)
            for item in fore_res['list'][:8]:
                hour = datetime.fromtimestamp(item['dt']).strftime('%I %p') # যেমন: 02 PM
                hourly_labels.append(hour)
                hourly_data.append(round(item['main']['temp']))

            # ৫ দিনের ফোরকাস্ট (প্রতিদিন ১টি করে)
            seen_days = set()
            for item in fore_res['list']:
                day_name = datetime.fromtimestamp(item['dt']).strftime('%a') # যেমন: Mon
                # আজকের দিন বাদ দিয়ে পরবর্তী দিনগুলো নেব
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

    # টেমপ্লেটে ডাটা পাঠানো
    return render_template('index.html', 
                           weather=weather_data, 
                           forecast=forecast_list, 
                           hourly_labels=hourly_labels, 
                           hourly_data=hourly_data,
                           aqi=aqi_data,
                           alerts=alerts,
                           error=error_msg)

if __name__ == '__main__':
    app.run(debug=True)