import os
import base64
from datetime import datetime

from flask import Flask, render_template, request
from google.cloud import storage, translate_v2 as translate, datastore
from google.cloud import language_v1
from google.cloud import texttospeech

app = Flask(__name__)

# APIuri
storage_client = storage.Client()
translate_client = translate.Client()
db = datastore.Client()
language_client = language_v1.LanguageServiceClient()
tts_client = texttospeech.TextToSpeechClient()

BUCKET_NAME = os.environ.get('BUCKET_NAME')


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/process', methods=['POST'])
def process():
    text = request.form.get('text_to_translate')

    if text:
        # Translation API
        result = translate_client.translate(text, target_language='ro')
        translated_text = result['translatedText']

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Natural Language API - sentiment analysis on original text
        nl_document = language_v1.Document(content=text, type_=language_v1.Document.Type.PLAIN_TEXT)
        sentiment = language_client.analyze_sentiment(request={'document': nl_document}).document_sentiment
        sentiment_score = round(sentiment.score, 2)
        sentiment_magnitude = round(sentiment.magnitude, 2)

        # Cloud Storage (stateful)
        bucket = storage_client.bucket(BUCKET_NAME)
        blob = bucket.blob('ultima_traducere.txt')
        blob.upload_from_string(
            f"Original: {text}\nTraducere: {translated_text}\n"
            f"Sentiment: {sentiment_score} (magnitudine: {sentiment_magnitude})"
        )

        # DataStorage (stateful)
        key = db.key('Traducere')
        entity = datastore.Entity(key=key)

        entity.update({
            'original': text,
            'tradus': translated_text,
            'timestamp': timestamp,
            'sentiment_score': sentiment_score,
            'sentiment_magnitude': sentiment_magnitude,
        })

        db.put(entity)

        # Serviciu de logging
        print(f"INFO: Traducere salvata in {BUCKET_NAME}")

        # Text-to-Speech API - pronunta traducerea in romana
        tts_input = texttospeech.SynthesisInput(text=translated_text)
        tts_voice = texttospeech.VoiceSelectionParams(language_code='ro-RO', ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL)
        tts_audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.MP3)
        tts_response = tts_client.synthesize_speech(input=tts_input, voice=tts_voice, audio_config=tts_audio_config)
        audio_b64 = base64.b64encode(tts_response.audio_content).decode('utf-8')

        return render_template('index.html', original=text, translated=translated_text,
                               sentiment_score=sentiment_score, sentiment_magnitude=sentiment_magnitude,
                               audio_b64=audio_b64)

    return render_template('index.html')


@app.route('/ultima_traducere', methods=['GET'])
def getTraducere():
    # Cloud Storage (stateful)
    bucket = storage_client.bucket(BUCKET_NAME)
    blob = bucket.blob('ultima_traducere.txt')
    if blob.exists():
        continut = blob.download_as_text()
    else:
        continut = "Nu s-a tradus nimic inca"

    # Serviciu de logging
    print(f"INFO:Am incarcat continutul din {BUCKET_NAME}")

    return render_template('ultima_traducere.html', continut=continut)


@app.route('/istoric', methods=['GET'])
def get_istoric():
    query = db.query(kind='Traducere')
    query.order = ['-timestamp']
    lista_traduceri = list(query.fetch())

    return render_template('istoric.html', continut=lista_traduceri)


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
