import requests
import threading
import time
from azure.cognitiveservices.speech import SpeechConfig, SpeechRecognizer, SpeechSynthesizer

speech_api_key = 'Placeholder'
location = 'WestUS'
language = 'en-GB'

list_of_timer = []

recognizer_config = SpeechConfig(subscription=speech_api_key, region=location, speech_recognition_language=language)
recognizer = SpeechRecognizer(speech_config=recognizer_config)

def cancel_timer():
    global list_of_timer
    for i in list_of_timer:
        i.cancel()
    list_of_timer = []

def get_timer_time(text):
    url = 'Placeholder'
    body = {'text': text}
    response = requests.post(url, json=body)
    if response.status_code != 200:
        return 0
    payload = response.json()
    print(payload)
    if payload['seconds'] == 0:         
        return payload['message']                                       
    else:                                                             
        return payload['seconds']                                       

def say(text):
    print(text)
    ssml =  f'<speak version=\'1.0\' xml:lang=\'{language}\'>'
    ssml += f'<voice xml:lang=\'{language}\' name=\'{first_voice.short_name}\'>'
    ssml += text
    ssml += '</voice>'
    ssml += '</speak>'
    recognizer.stop_continuous_recognition()
    speech_synthesizer.speak_ssml(ssml)
    recognizer.start_continuous_recognition()

def announce_timer(minutes, seconds):
    announcement = 'Times up on your '
    if minutes > 0:
        announcement += f'{minutes} minute '
    if seconds > 0:
        announcement += f'{seconds} second '
    announcement += 'timer.'
    say(announcement)

def create_timer(total_seconds):
    global list_of_timer
    minutes, seconds = divmod(total_seconds, 60)
    for i in list_of_timer[:]:
        if (i.is_alive()) == False:
            list_of_timer.remove(i)
    a = threading.Timer(total_seconds, announce_timer, args=[minutes, seconds])
    a.start()
    list_of_timer.append(a)
    announcement = ''
    if minutes > 0:
        announcement += f'{minutes} minute '   
    if seconds > 0:
        announcement += f'{seconds} second '    
    announcement += 'timer started.'
    say(announcement)

def process_text(text):
    print(text)
    global list_of_timer
    a = get_timer_time(text)
    if a == "Timer cancelled successfully":
        if len(list_of_timer) == 0:
            say("No timer to cancel")
        else:
            cancel_timer()
            say("Cancel successfully")
    else:
        if a != 0:
            create_timer(get_timer_time(text))

def recognized(args):
    process_text(args.result.text)

recognizer.recognized.connect(recognized)

speech_config = SpeechConfig(subscription=speech_api_key, region=location)
speech_config.speech_synthesis_language = language
speech_synthesizer = SpeechSynthesizer(speech_config=speech_config)
voices = speech_synthesizer.get_voices_async().get().voices
first_voice = next(x for x in voices if x.locale.lower() == language.lower())
speech_config.speech_synthesis_voice_name = first_voice.short_name


recognizer.start_continuous_recognition()
print("Say something")
while True:
    time.sleep(1)
  
