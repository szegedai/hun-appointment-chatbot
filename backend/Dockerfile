FROM rasa/rasa:2.2.7-full

WORKDIR /app
COPY . /app
COPY ./data /app/data
COPY ./models /app/models
COPY ./services /app/services

USER root

RUN pip install -r requirements.txt &&\
    # installing from web
	#pip install https://github.com/oroszgy/spacy-hungarian-models/releases/download/hu_core_ud_lg-0.3.1/hu_core_ud_lg-0.3.1-py3-none-any.whl &&\
	# installing from wheel file
RUN pip install hu_core_ud_lg-0.3.1-py3-none-any.whl &&\
	python -m spacy link hu_core_ud_lg hu

USER 1001

CMD [ "run","-m","/app/models","--enable-api","--cors","*","--debug" ]