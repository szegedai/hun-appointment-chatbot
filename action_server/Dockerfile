FROM rasa/rasa-sdk:latest

WORKDIR /app

COPY . ./

USER root

RUN pip install -r requirements.txt

USER 1001