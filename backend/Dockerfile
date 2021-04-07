FROM rasa/rasa:latest-full 

WORKDIR /app
COPY . /app
COPY ./data /app/data
COPY ./services /app/services

USER root

RUN pip install -r requirements.txt &&\
	pip install https://github.com/oroszgy/spacy-hungarian-models/releases/download/hu_core_ud_lg-0.3.1/hu_core_ud_lg-0.3.1-py3-none-any.whl &&\
	python -m spacy link hu_core_ud_lg hu &&\
	rasa train

USER 1001

VOLUME /app
VOLUME /app/data

CMD [ "run","-m","/app/models","--enable-api","--cors","*","--debug" ]