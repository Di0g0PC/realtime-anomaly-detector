import paho.mqtt.client as mqtt
import json
import time


def subscrive_data_mqtt(
    mqtt_server: str,
    topics: list,
    on_message_callback,
    client_id:str,
    port: int = 1883,
):
    connected = False
    def on_connect(client, userdata, flags, rc):
        nonlocal connected 
        if rc == 0:
            print("Conectado com sucesso ao broker MQTT")
            connected = True
            for topic in topics:
                client.subscribe(topic)
                print(f"Subscrito ao tópico: {topic}")
        else:
            print(f"Falha na ligação ao broker MQTT: Código {rc}")

    def on_disconnect(client, userdata, rc):
        nonlocal connected
        connected = False
        print("Client desconectado ao broker MQTT ")
        if rc != 0:
            print("A reconectar....")

    def on_message(client, userdata, msg):
        try:
            data = msg.payload.decode('utf-8')
            payload = json.loads(data)
            print(f"MSG({msg.topic}): {payload}")
            on_message_callback(msg.topic, payload)
        except Exception as e:
            print(f"Erro ao processar a mensagem: {e}")

    client = mqtt.Client(client_id=client_id)
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_disconnect = on_disconnect

    try:
        client.reconnect_delay_set(min_delay=1,max_delay=15)
        client.connect(mqtt_server, port, 60)
        client.loop_start()
        max_delay = time.time() + 15

        while not connected and time.time() < max_delay:
            print("À espera de conexão...")
            time.sleep(0.5)
            
        if not connected:
            print("Não foi possivel efetuar a ligação ao Boker MQTT")
            return False
        
        while True:
            time.sleep(0.5)

    except KeyboardInterrupt:
        print("A encerrar...")

    except Exception as e:
        print(f"Erro geral: {e}")

    finally:
        client.loop_stop()
        client.disconnect()
