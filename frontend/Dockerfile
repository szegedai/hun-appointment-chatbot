FROM ubuntu:18.04

RUN apt-get update
RUN apt-get -y install curl gnupg
RUN curl -fsSL https://deb.nodesource.com/setup_lts.x | bash -
RUN apt-get install -y nodejs


WORKDIR /app/frontend
COPY . /app/frontend

RUN npm install 

VOLUME /app/frontend

CMD npm start