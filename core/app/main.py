from fastapi import FastAPI
import pandas as pd
import time
from convert_utc import convert_utc
from http import HTTPStatus
from publish_data_mqtt import publish_data_mqtt
from schemas import config_schema

init_read_items = True
df_events = None

app = FastAPI()

@app.get("/run/", status_code=HTTPStatus.OK)
def send_data(factor:float=0.1, n_print:int=3):
    global init_read_items
    global df_events
    
    if (init_read_items):
        print("Preparing data")
        df = pd.read_csv('/data/nexus_client_clearance_.csv')

        df_filter = df[df["Status"] == "Aceite"]
        df_filter = df_filter[["Authorization start date","Authorization expiration","Container Plate"]]

        df1 = df_filter
        df2 = df_filter.copy(deep=True)

        df_in = convert_utc(df1, 'Authorization start date')
        df_out = convert_utc(df2, 'Authorization expiration')
        df_events = pd.concat([df_in,df_out]).sort_values(by="ts")
        df_events = df_events[["Container Plate", "ts"]]

        # Volta a colocar os indices por ordem
        df_events.reset_index(drop=True, inplace=True)
        df_events['delay'] = df_events['ts'].diff().fillna(0)
        
        init_read_items = False

    count = 0
    
    for ii in range(n_print):

        start = time.time()
        telemetry = df_events[["Container Plate", "ts"]].iloc[ii].to_dict()

        print(telemetry)
        if publish_data_mqtt(
            telemetry, 
            "demo.thingsboard.io",
            "e8rbmdzleyprfte06ggr",
            "v1/devices/me/telemetry"
            ):
            print("Data publish correctly")
        else:
            print("Error publish data")

        end = time.time()
        count+= 1 
        delay = df_events.loc[ii,'delay']

        print(f"sleeping for {delay:.5f}s")
        print(f"Injection number: {count}")
        print()

        tempo = max(0,(factor * delay - (end-start)))
        if tempo>0:
            time.sleep(tempo)

    return {"status": f"Injected {count} container(s)"}

@app.post("/config/", status_code=HTTPStatus.OK)
def config_data(payload: config_schema):
    telemetry = {}
    
    if payload.changeState:
        telemetry['_changeState']= payload.changeState

    if payload.config:
        telemetry['_config'] = payload.config 
    
    if publish_data_mqtt(
        telemetry, 
        "demo.thingsboard.io",
        "e8rbmdzleyprfte06ggr",
        "v1/devices/me/telemetry"
        ):
        print("Data publish correctly")
    else:
        print("Error publish data")

    print(telemetry)

    return {
        "status": HTTPStatus.OK,
        "_changeState": payload.changeState,
        "config": payload.config
        }

