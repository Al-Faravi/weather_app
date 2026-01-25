from flask import Flask, render_template, request
import requests
from datetime import datetime, timedelta

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def home():
    weather_data = None
    error_msg = None
    
    if request.method == 'POST':
        city = request.form.get('city')
        api_key = "b140d4764e7e30ec785c37515da8ea5d" 
        
        # OpenWeatherMap API URL
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
        
        try:
            response = requests.get(url).json()
            
            if response.get('cod') == 200:
                # সূর্যোদয় ও সূর্যাস্তের সময়কে স্থানীয় সময়ে রূপান্তর (ঐচ্ছিক ফিচার)
                sunrise_timestamp = response['sys']['sunrise'] + response['timezone']
                sunset_timestamp = response['sys']['sunset'] + response['timezone']
                
                sunrise_time = datetime.utcfromtimestamp(sunrise_timestamp).strftime('%I:%M %p')
                sunset_time = datetime.utcfromtimestamp(sunset_timestamp).strftime('%I:%M %p')

                weather_data = {
                    'city': response['name'],
                    'country': response['sys']['country'],
                    'temp': round(response['main']['temp']),
                    'desc': response['weather'][0]['description'],
                    'icon': response['weather'][0]['icon'],
                    'humidity': response['main']['humidity'],
                    'wind': response['wind']['speed'],
                    'pressure': response['main']['pressure'],
                    'visibility': round(response.get('visibility', 0) / 1000, 1), # মি থেকে কিমি
                    'sunrise': sunrise_time,
                    'sunset': sunset_time,
                    'feels_like': round(response['main']['feels_like'])
                }
            else:
                error_msg = "দুঃখিত, শহরের নামটি সঠিক নয়। আবার চেষ্টা করুন!"
                
        except Exception as e:
            error_msg = "সার্ভারে সংযোগ করতে সমস্যা হচ্ছে। আপনার ইন্টারনেট কানেকশন চেক করুন।"

    return render_template('index.html', weather=weather_data, error=error_msg)

if __name__ == '__main__':
    app.run(debug=True)