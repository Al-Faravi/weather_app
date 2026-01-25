from flask import Flask, render_template, request
import requests
from datetime import datetime

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def home():
    weather_data = None
    forecast_list = []
    error_msg = None
    api_key = "b140d4764e7e30ec785c37515da8ea5d" 
    
    if request.method == 'POST':
        city = request.form.get('city')
        
        # ১. বর্তমান আবহাওয়ার জন্য API কল
        current_url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
        
        # ২. ৫ দিনের পূর্বাভাসের জন্য API কল
        forecast_url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={api_key}&units=metric"
        
        try:
            curr_res = requests.get(current_url).json()
            fore_res = requests.get(forecast_url).json()
            
            if curr_res.get('cod') == 200:
                # সময় রূপান্তর (Timezone অনুযায়ী)
                sunrise = datetime.utcfromtimestamp(curr_res['sys']['sunrise'] + curr_res['timezone']).strftime('%I:%M %p')
                sunset = datetime.utcfromtimestamp(curr_res['sys']['sunset'] + curr_res['timezone']).strftime('%I:%M %p')

                weather_data = {
                    'city': curr_res['name'],
                    'country': curr_res['sys']['country'],
                    'temp': round(curr_res['main']['temp']),
                    'desc': curr_res['weather'][0]['description'],
                    'main_condition': curr_res['weather'][0]['main'].lower(), # সিএসএস থিমের জন্য
                    'icon': curr_res['weather'][0]['icon'],
                    'humidity': curr_res['main']['humidity'],
                    'wind': curr_res['wind']['speed'],
                    'pressure': curr_res['main']['pressure'],
                    'visibility': round(curr_res.get('visibility', 0) / 1000, 1),
                    'sunrise': sunrise,
                    'sunset': sunset,
                    'feels_like': round(curr_res['main']['feels_like'])
                }

                # ৫ দিনের পূর্বাভাসের ডাটা প্রসেসিং (প্রতিদিনের নির্দিষ্ট সময়ের ডাটা ফিল্টার)
                # এই API প্রতি ৩ ঘণ্টা পরপর ডাটা দেয়, আমরা প্রতিদিনের একটি করে ডাটা নেব
                for item in fore_res['list'][::8]: 
                    forecast_list.append({
                        'day': datetime.fromtimestamp(item['dt']).strftime('%a'),
                        'temp': round(item['main']['temp']),
                        'icon': item['weather'][0]['icon'],
                        'condition': item['weather'][0]['main']
                    })
            else:
                error_msg = "দুঃখিত, এই শহরটি খুঁজে পাওয়া যায়নি!"
                
        except Exception as e:
            error_msg = "ডেটা লোড করতে সমস্যা হচ্ছে। আপনার ইন্টারনেট কানেকশন চেক করুন।"

    return render_template('index.html', weather=weather_data, forecast=forecast_list, error=error_msg)

if __name__ == '__main__':
    app.run(debug=True)