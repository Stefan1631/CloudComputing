import os
from datetime import datetime

from flask import Flask, render_template, request
from google.cloud import storage, translate_v2 as translate, datastore

app = Flask(__name__)

# APIuri
storage_client = storage.Client()
translate_client = translate.Client()
db = datastore.Client()

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

        # Cloud Storage (stateful)
        bucket = storage_client.bucket(BUCKET_NAME)
        blob = bucket.blob('ultima_traducere.txt')
        blob.upload_from_string(f"Original: {text}\nTraducere: {translated_text}")

        # DataStorage (stateful)
        key = db.key('Traducere')
        entity = datastore.Entity(key=key)

        entity.update({
            'original': text,
            'tradus': translated_text,
            'timestamp': timestamp
        })

        db.put(entity)

        # Serviciu de logging
        print(f"INFO: Traducere salvata in {BUCKET_NAME}")

        return render_template('index.html', original=text, translated=translated_text)

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
