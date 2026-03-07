from flask import Flask, render_template, request
import requests

app = Flask(__name__)

# Yahan apni API Key dalein
API_KEY = 'jcw3qyLcljadB1gdLnQEv5Md3pQMLavtKnff8xcp'

@app.route('/', methods=['GET', 'POST'])
def index():
    weather_data = None
    city = None
    
    if request.method == 'POST':
        city = request.form.get('city')
        if city:
            # OpenWeatherMap API URL
            url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&units=metric&appid={API_KEY}"
            response = requests.get(url).json()
            
            if response.get('cod') == 200:
                weather_data = {
                    'city': response['name'],
                    'temp': response['main']['temp'],
                    'description': response['weather'][0]['description'],
                    'icon': response['weather'][0]['icon']
                }
            else:
                weather_data = {'error': 'City not found!'}

    return render_template('index.html', weather=weather_data)

if __name__ == '__main__':
    app.run(debug=True)