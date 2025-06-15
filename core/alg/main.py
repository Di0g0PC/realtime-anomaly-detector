import paho.mqtt.subscribe as subscribe
# import asyncio
from state_machine import tsAlg as state_machine
from subscribe_data_mqtt import subscrive_data_mqtt
from prometheus_client import start_http_server


topics = ["AD/containers"]

alg = state_machine("containers","/data/AD.db")

def on_message_print(topic, payload):
    alg.countMsg += 1
    print(f"MSG #{alg.countMsg} do {topic}")
    alg.execute(payload)
    print("Mensagem processada")
    # print(f"Dicionário: {alg.monitor}")

if __name__ == '__main__':
    # Start up the server to expose the metrics.
    start_http_server(7000)
    subscrive_data_mqtt("broker.hivemq.com", topics, on_message_print, "Anomaly_Detector",1883)