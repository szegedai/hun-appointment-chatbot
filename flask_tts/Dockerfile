FROM python:3.8-slim

WORKDIR /app/flask

COPY . .

RUN pip install -r requirements.txt

CMD ["python3", "tts_backend.py"]
