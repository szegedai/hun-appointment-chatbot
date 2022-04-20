FROM ubuntu:18.04

RUN apt-get update && apt-get install -y autossh && apt-get clean

COPY ./id_rsa /.ssh/id_rsa

COPY ./cmd.sh /cmd.sh

EXPOSE 8000

CMD ["/bin/bash", "/cmd.sh"]