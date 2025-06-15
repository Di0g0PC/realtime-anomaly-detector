import paho.mqtt.client as mqtt
import json
import time

def publish_data_mqtt(telemetry: dict, mqtt_server:str ,token:str, topic:str, port:int = 1883) -> bool:
    connected = False
    success = False

    def on_connect(client, userdata, flags, rc):
        nonlocal connected #Permite alterar a variavel connected
        if rc == 0:
            connected = True
        else:
            print(f"Falha na ligação ao broker MQTT: Código {rc}")
    
    def on_disconnect(client, userdata, rc):
        nonlocal connected
        connected = False
        print("Client desconectado ao broker MQTT ")
        if rc != 0:
            print("A reconectar....")

    client = mqtt.Client()
    client.username_pw_set(token)  # Token do dispositivo
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect

    try:
        client.reconnect_delay_set(min_delay=1,max_delay=15)
        client.connect(mqtt_server, port, 60)
        client.loop_start() # Para ter processamento em background (async)
        
        max_delay = time.time() + 15
        while not connected and time.time() < max_delay:
            time.sleep(0.5)
            print("À espera de conexão")

        if not connected:
            print("Não foi possivel efetuar a conexão ao broker")
            return False

        # Converte dicionário para JSON string
        telemetry_json = json.dumps(telemetry)

        # Publica a telemetria
        result = client.publish(topic, telemetry_json)
        result.wait_for_publish()  # bloqueia até a publicação ser confirmada

        if result.is_published():
            success = True
        else:
            client.loop_stop()
            client.disconnect()
            print("Erro ao publicar data via MQTT")
            return False
        
        return success

    except Exception as e:
        print(f"Erro ao publicar data via MQTT: {e}")
        return False
    
    finally:
        client.loop_stop()
        client.disconnect()
