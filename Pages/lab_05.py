import requests

def get_current_weather(location):
    url = f'https://wttr.in{location}?format=j1'
    response = requests.get(url, timeout=10)
    if response.status_code != 200:
        raise Exception(f"wttr.in error:status {response.status_code}")
    try: 
        data = response.json()
    except ValueError:
        raise Exception(f"Could not find a location named{location}")
    current = data['current_condition'][0]


    return {
        'location':location,
        'temperature': float(current['temp_F']),
        'description': current['weatherDesc'][0]['value'],
        'FeelsLikeF': int(current['FeelsLikeF']),
        'visibility' : float(current['visibility']),
        'humidity' : int(current['humidity']),
        'uvIndex' : int(current['uvIndex']),
        'windspeedMiles': float(current['windspeedMiles'])
    }

    
    