# -*- coding: utf-8 -*-
import json
import requests
import urllib
import subprocess
import argparse
import pycurl
import StringIO
import os.path
import azure_translate_api
from gtts import gTTS

 
def speak_text(language, phrase):
    tts = gTTS(text=phrase, lang=language)
    tts.save("output.mp3")
    subprocess.call(['mplayer output.mp3'], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    

def transcribe(lang):
    key = 'AIzaSyAcalCzUvPmmJ7CZBFOEWx2Z1ZSn4Vs1gg'
    stt_url = 'https://www.google.com/speech-api/v2/recognize?client=chromium&lang='+ lang + '&key=' + key
    filename = 'test.flac'
    print "listening .."
#    os.system(
#        'arecord -D plughw:1,0 -f cd -c 1 -t wav -d 0 -q -r 16000 -d 3 | flac - -s -f --best --sample-rate 16000 -o ' + filename)
    os.system('rec -r 16000 ' + filename + ' silence 1 0.1 5% 1 2.0 5%')

    print "interpreting .."
    # send the file to google speech api
    c = pycurl.Curl()
    c.setopt(pycurl.VERBOSE, 0)
    c.setopt(pycurl.URL, stt_url)
    fout = StringIO.StringIO()
    c.setopt(pycurl.WRITEFUNCTION, fout.write)
 
    c.setopt(pycurl.POST, 1)
    c.setopt(pycurl.HTTPHEADER, ['Content-Type: audio/x-flac; rate=16000'])
 
    file_size = os.path.getsize(filename)
    c.setopt(pycurl.POSTFIELDSIZE, file_size)
    fin = open(filename, 'rb')
    c.setopt(pycurl.READFUNCTION, fin.read)
    c.perform()
 
    response_data = fout.getvalue()
 
    start_loc = response_data.find("transcript")
    temp_str = response_data[start_loc + 13:]
    end_loc = temp_str.find("\"")
    final_result = temp_str[:end_loc]
    c.close()
    return final_result
 
 
class Translator(object):
    oauth_url = 'https://datamarket.accesscontrol.windows.net/v2/OAuth2-13'
    translation_url = 'http://api.microsofttranslator.com/V2/Ajax.svc/Translate?'
 
    def __init__(self):
        oauth_args = {
            'client_id': 'TranslationPi',
            'client_secret': 'l8Hhx/ejsWLIaTAcu/f7TV04epEqQM3WwmB5Da1iPp0=',
            'scope': 'http://api.microsofttranslator.com',
            'grant_type': 'client_credentials'
        }
        oauth_junk = json.loads(requests.post(Translator.oauth_url, data=urllib.urlencode(oauth_args)).content)
        self.headers = {'Authorization': 'Bearer ' + oauth_junk['access_token']}
 
    def translate(self, origin_language, destination_language, text):
 
        translation_args = {
            'text': text,
            'to': destination_language,
            'from': origin_language
        }
	client = azure_translate_api.MicrosoftTranslatorClient('TranslationPi',  # make sure to replace client_id with your client id
                                                       'l8Hhx/ejsWLIaTAcu/f7TV04epEqQM3WwmB5Da1iPp0=') # replace the client secret with$
	translation =  client.TranslateText(text, origin_language, destination_language)


#        if destination_language == 'DE':
#            translation = translation.translate(german_umlauts)
        print "Translation: ", translation
        speak_text(origin_language, 'Translating ' + text)
        speak_text(destination_language, translation)
 
 
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Raspberry Pi - Translator.')
    parser.add_argument('-o', '--origin_language', help='Origin Language', required=True)
    parser.add_argument('-d', '--destination_language', help='Destination Language', required=True)
    args = parser.parse_args()
    while True:
        Translator().translate(args.origin_language, args.destination_language, transcribe(args.origin_language))
