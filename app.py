from flask import Flask, render_template, request
import requests
from datetime import datetime

app = Flask(__name__)

# আপনার API Key
API_KEY = "b140d4764e7e30ec785c37515da8ea5d"

@app.route('/', methods=['GET', 'POST'])
def home():
    weather_data = None
    forecast_list = []
    error_msg = None
    
    # ইনপুট ডাটা গ্রহণ (POST থেকে শহর অথবা GET থেকে ল্যাট/লন)
    city = request.form.get('city')
    lat = request.args.get('lat')
    lon = request.args.get('lon')

    current_url = None
    forecast_url = None

    # ১. ইউআরএল কনস্ট্রাকশন (শহর বনাম কোঅর্ডিনেট)
    if city:
        current_url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
        forecast_url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={API_KEY}&units=metric"
    elif lat and lon:
        current_url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"
        forecast_url = f"http://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"

    # ২. যদি কোনো রিকোয়েস্ট থাকে তবে ডাটা ফেচ করা
    if current_url and forecast_url:
        try:
            curr_res = requests.get(current_url).json()
            fore_res = requests.get(forecast_url).json()

            if curr_res.get('cod') == 200:
                # স্থানীয় সময় অনুযায়ী সূর্যোদয় ও সূর্যাস্ত গণনা
                # OpenWeatherMap-এর 'timezone' সেকেন্ডে থাকে
                sunrise = datetime.utcfromtimestamp(curr_res['sys']['sunrise'] + curr_res['timezone']).strftime('%I:%M %p')
                sunset = datetime.utcfromtimestamp(curr_res['sys']['sunset'] + curr_res['timezone']).strftime('%I:%M %p')

                weather_data = {
                    'city': curr_res['name'],
                    'country': curr_res['sys']['country'],
                    'temp': round(curr_res['main']['temp']),
                    'desc': curr_res['weather'][0]['description'],
                    'main_condition': curr_res['weather'][0]['main'].lower(),
                    'icon': curr_res['weather'][0]['icon'],
                    'humidity': curr_res['main']['humidity'],
                    'wind': curr_res['wind']['speed'],
                    'pressure': curr_res['main']['pressure'],
                    'visibility': round(curr_res.get('visibility', 0) / 1000, 1),
                    'sunrise': sunrise,
                    'sunset': sunset,
                    'feels_like': round(curr_res['main']['feels_like'])
                }

                # ৫ দিনের পূর্বাভাসের ডাটা প্রসেসিং (প্রতিদিনের জন্য একটি করে স্লট)
                for item in fore_res['list'][::8]:
                    forecast_list.append({
                        'day': datetime.fromtimestamp(item['dt']).strftime('%a'),
                        'temp': round(item['main']['temp']),
                        'icon': item['weather'][0]['icon'],
                        'condition': item['weather'][0]['main']
                    })
            else:
                error_msg = "দুঃখিত, এই স্থানটি খুঁজে পাওয়া যায়নি!"
                
        except Exception as e:
            error_msg = "সার্ভার থেকে ডেটা আনতে সমস্যা হচ্ছে। অনুগ্রহ করে পরে চেষ্টা করুন।"

    return render_template('index.html', weather=weather_data, forecast=forecast_list, error=error_msg)

if __name__ == '__main__':
    app.run(debug=True)