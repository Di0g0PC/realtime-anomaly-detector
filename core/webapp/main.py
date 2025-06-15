import streamlit as st
import requests

st.set_page_config(page_title="API Interface", layout="wide")
#Atualizar de acordo com o host- se usar maquinas diferentes usar IP 
BASE_URL = "http://fmk_app:8000" 

st.title("INJECTOR INTERFACE")
tab1, tab2 = st.tabs(['Config','Run'])

# ---- POST /config ----
tab1.header("Configure System (POST /config)")
with tab1.form("config_form"):
    st.subheader("Configuration Parameters")

    st.caption("Alteração de estado - Máquina de estados")
    change_state = st.text_input("Change State", "")

    st.caption("Número de elementos usados para treinar o modelo - Por defeito - 100")
    currentN = st.text_input("currentN", value="300")

    st.caption("Percentagem de valores usados para teste")
    p = st.text_input("p", value="0.3")

    durationcol = st.text_input("durationcol", value="ON")

    alg_id = st.text_input("id", value="Container Plate")

    algs = st.multiselect("Algorithms", ["func1", "func2", "func3"], default=["func2"])

    submit_config = st.form_submit_button("Send Configuration")

    if submit_config:
        payload = {
            "changeState": change_state,
            "config": {
                "currentN": int(currentN) if currentN else "",
                "p": float(p) if currentN else "",
                "durationcol": durationcol,
                "id": alg_id,
                "Algs": algs
            }
        }
        for key in list(payload["config"].keys()):
            if payload["config"][key] == "" or payload["config"][key] == []:
                del payload["config"][key]

        response = requests.post(f"{BASE_URL}/config/", json=payload)
        st.write("Response Status Code:", response.status_code)
        st.json(response.json())

# ---- GET /run ----
tab2.header("Run Algorithm (GET /run)")
with tab2.form("run_form"):
    st.subheader("Run Parameters")
    factor = st.text_input("Factor", value="0.001")
    n_print = st.number_input("n_print", value=3)

    submit_run = st.form_submit_button("Execute Run")

    if submit_run:
        params = {
            "factor": factor,
            "n_print": int(n_print)
        }

        response = requests.get(f"{BASE_URL}/run/", params=params)
        st.write("Response Status Code:", response.status_code)
        st.json(response.json())
