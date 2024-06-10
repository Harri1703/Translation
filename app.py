from flask import Flask, request, jsonify
import re
from gtts import gTTS
import os

app = Flask(__name__)

# Mapping for Tamil words for days and months
tamil_words = {
    '0': 'poojium', '1': 'ondru', '2': 'irandu', '3': 'moondru', '4': 'naangu', '5': 'ainthu',
    '6': 'aaru', '7': 'yelu', '8': 'ettu', '9': 'onbadhu', '10': 'pathu', 
    '11': 'pathinondru', '12': 'panirandu', '13': 'pathinmoondru', '14': 'pathinaangu',
    '15': 'pathinainthu', '16': 'pathinaaru', '17': 'pathinayelu', '18': 'pathinettu', '19': 'pathonbadhu',
    '20': 'irupathu', '21': 'irupathu ondru', '22': 'irupathu irandu', '23': 'irupathu moondru', '24': 'irupathu naangu',
    '25': 'irupathu ainthu', '26': 'irupathu aaru', '27': 'irupathu yelu', '28': 'irupathu ettu', '29': 'irupathu onbadhu',
    '30': 'muppathu', '31': 'muppathu ondru', '32': 'muppathu irandu', '33': 'muppathu moondru', '34': 'muppathu naangu',
    '35': 'muppathu ainthu', '36': 'muppathu aaru', '37': 'muppathu yelu', '38': 'muppathu ettu', '39': 'muppathu onbadhu',
    '40': 'narpathu', '41': 'narpathu ondru', '42': 'narpathu irandu', '43': 'narpathu moondru', '44': 'narpathu naangu',
    '45': 'narpathu ainthu', '46': 'narpathu aaru', '47': 'narpathu yelu', '48': 'narpathu ettu', '49': 'narpathu onbadhu',
    '50': 'aimbathu', '51': 'aimbathu ondru', '52': 'aimbathu irandu', '53': 'aimbathu moondru', '54': 'aimbathu naangu',
    '55': 'aimbathu ainthu', '56': 'aimbathu aaru', '57': 'aimbathu yelu', '58': 'aimbathu ettu', '59': 'aimbathu onbadhu'
}

# Mapping for English months
months = [
    ",January,", ",February,", ",March,", ",April,", ",May,", ",June,",
    ",July,", ",August,", ",September,", ",October,", ",November,", ",December,"
]

# Mapping for Tamil words for specific years
year_words = {
    '2024': 'irandayirathu, irupathu naangu',
    '2025': 'irandayirathu, irupathu ainthu',
    '2026': 'irandayirathu, irupathu aaru',
    '2027': 'irandayirathu, irupathu yelu',
    '2028': 'irandayirathu, irupathu ettu',
    '2029': 'irandayirathu, irupathu onbadhu',
    '2030': 'irandayirathu, muppathu',
    '2031': 'irandayirathu, muppathu ondru',
    '2032': 'irandayirathu, muppathu irandu'
}

# Mapping for Tamil leave types
leave_types = {
    'study holiday': 'padipu',
    'semester holiday': 'semester',
    'weekly off': 'vaara',
    'sick leave': 'noiivaaiipatta'
}

# Function to convert a year number to Tamil words based on the mapping
def year_to_tamil(year):
    return year_words.get(year, 'Unknown year')

# Function to translate a date in the format dd-mm-yyyy to Tamil words
def translate_date(date_str):
    day, month, year = date_str.split('-')
    tamil_day = tamil_words[str(int(day))]  
    english_month = months[int(month) - 1]
    tamil_year = year_to_tamil(year)
    return f"{tamil_day} {english_month} {tamil_year}"

# Function to translate time in hh:mm AM/PM to Tamil words
def translate_time(time_str):
    time, period = time_str.rsplit(' ', 1)
    hours, minutes = map(int, time.split(':'))

    tamil_hours = tamil_words[str(hours)] 
    tamil_minutes = f"{tamil_words[str(minutes)]} nimidangal" if minutes != 0 else ""

    period_tamil = "kaalai," if period == "AM" else "maalai,"
    tamil_time = f"{tamil_hours} mani {tamil_minutes}".strip()

    return f"{period_tamil} {tamil_time}"

@app.route('/translate', methods=['POST'])
def translate_text():
    english_text = request.json['text']
    
    # Extract name, type of leave, and dates from the text
    match = re.match(r'your (son|daughter) ([A-Za-z ]+) applied (.+) from (\d{2}-\d{2}-\d{4}) (\d{2}:\d{2} (AM|PM)) to (\d{2}-\d{2}-\d{4}) (\d{2}:\d{2} (AM|PM))', english_text)
    if not match:
        return {'error': 'Invalid input format'}, 400
    
    gender = match.group(1)
    name = match.group(2)
    leave_type = match.group(3).lower()
    start_date = match.group(4)
    start_time = match.group(5)
    end_date = match.group(7)
    end_time = match.group(8)
    
    # Check if leave type is in the presets
    if leave_type not in leave_types:
        return {'error': 'Invalid leave type'}, 400
    
    # Translate dates and times
    tamil_start_date = translate_date(start_date)
    tamil_end_date = translate_date(end_date)
    tamil_start_time = translate_time(start_time)
    tamil_end_time = translate_time(end_time)
    
    # Fixed Tamil phrases
    tamil_gender = "ungal magan" if gender == "son" else "ungal magal"
    tamil_leave_type = leave_types[leave_type]  # Use the preset leave type
    
    # Construct the final message
    tamil_message = f"{tamil_gender}, {name}, {tamil_leave_type}, vidumuraikaga, {tamil_start_date}, {tamil_start_time} muthal, {tamil_end_date}, {tamil_end_time} varai, vinnappithullar."
    
    # Convert Tamil text to speech and save as MP3
    tts = gTTS(tamil_message, lang='ta')
    audio_path = f"audio/{name.replace(' ', '_')}.mp3"
    os.makedirs(os.path.dirname(audio_path), exist_ok=True)
    tts.save(audio_path)
    
    return jsonify({'tamil_text': tamil_message, 'audio_file': audio_path})

if __name__ == '__main__':
    app.run()
