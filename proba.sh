#!/bin/bash

cd /home/gszabo/hun-appointment-chatbot/

docker-compose logs >> log.txt

echo $(date +%Y/%m/%d) >> log.txt

docker-compose down

docker rmi hun-appointment-chatbot-action_server

docker-compose up
