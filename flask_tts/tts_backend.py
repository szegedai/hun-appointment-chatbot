from flask import Flask, request, Response, make_response
from flask_cors import CORS
import requests
import json

with open("credentials.json") as f:
    data = json.load(f)

app = Flask(__name__)
CORS(app)

@app.route('/')
def hw():
    return "routebol"

@app.route('/tts', methods=['GET'])
def tts():
    print(request.args.get('speaker'))
    speaker = request.args.get('speaker')
    print(f"TTS request a következő szövegre: {request.args.get('q')}")
    payload = {'speaker': speaker if speaker is not None and speaker in ['NG', 'MK'] else 'NG', 'q': request.args.get('q')}
    result = requests.get(f"http://{data.get('user')}:{data.get('pw')}@cyrus.tmit.bme.hu/hmmtts2/synth_hmm_wav.php", params=payload)
    response = make_response(result.content)
    response.headers.set('Content-Type', 'audio/wav')
    return response


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=3001)
