#!/bin/bash

MSG="{\"_config\": {\"currentN\": 10, \"p\": 0.3}}"
mosquitto_pub -t "teste/topico" -h "broker.hivemq.com" -m "$MSG"
sleep 0.2

for i in $(seq 0 1 10); do
    
    if [ "$i" = "3" ]; then
        MSG="{\"_changeState\": \"Add\"}"
        mosquitto_pub -t "teste/topico" -h "broker.hivemq.com" -m "$MSG"
    fi

    MSG="{\"tsTimeStamp\": $i, \"tsValue\": $RANDOM}"
    mosquitto_pub -t "teste/topico" -h "broker.hivemq.com" -m "$MSG"
    sleep 0.2
done