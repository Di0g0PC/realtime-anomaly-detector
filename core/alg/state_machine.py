import pandas as pd
import time
from pyod.models.knn import KNN
import numpy as np  
from prometheus_client import Gauge
from database import (
                      create_table,
                      insert_db_data, 
                      keep_last_n_db,
                      table_rows,
                      select_data,
                      )
import joblib
from pathlib import Path



class tsAlg:
    countMsg = 0
    def __init__(self,name,db_name):
        self.tmName = name
        self.db_name = db_name
        self.status = "Add"
        self.config = {
            "currentN" : 100 ,
            "p" : 0.3, 
            "durationcol": "ON", 
            "id": "Container Plate", 
            "Algs": ['func1','func2']}
        self.monitor = {}
        self.test = pd.DataFrame(columns=[self.config["id"],'ts','tsValue'])
        create_table(self.db_name,"historico")
        create_table(self.db_name,"train_alg")
        self.algConfig = {}
        self.Add_Data = True
        self.outlier_pred = Gauge('Outlier_pred', 'Classification')
        self.outlier_score = Gauge('Outlier_score', 'Outlier Score')
        
        #durationcol - "on"- Quando estamos a trabalhar com "durações"

    def func1(self,msg:str):

        if 'func1' in self.algConfig.keys():
            lst = self.algConfig['func1']
            
        elif 'func1' not in self.algConfig.keys():
            self.algConfig['func1'] = []
            lst = self.algConfig['func1']
        
        ts = time.time()
        ts_old = ts - 60 
        lst.append([msg,ts])
        list_copy = lst.copy()

        for i in range(len(list_copy)):
            if list_copy[i][1] < ts_old:
                del lst[i]
            else:
                break

        result = len(lst)
        containers = [item[0] for item in lst]
        self.algConfig['func1'] = lst

        print(f"No ultimo minuto saíram {result} {self.config["id"]}(s) - ({containers})")

    def func2(self,msg:float):
        
        if 'func2' in self.algConfig.keys():
            lst = self.algConfig['func2']
            
        elif 'func2' not in self.algConfig.keys():
            self.algConfig['func2'] = {
                'db_name':self.db_name,
                'table_name': "train_alg", 
                'cols': "tsValue"}
            
            lst = self.algConfig['func2']
        
        model_path = Path("data/modelo_knn.pkl")

        if model_path.exists():
            clf = joblib.load(model_path)
            print("Modelo carregado com sucesso.")

        else:
            x_train = np.array(select_data(lst["db_name"],lst["table_name"],lst["cols"]))
            x_train = x_train.reshape(-1,1)
            
            clf = KNN(n_neighbors=5, contamination=0.1, method='mean')
            clf.fit(x_train)

            joblib.dump(clf, model_path)
            print("Modelo salvo.")

        x_pred = np.array([[msg]])

        # É necessário testar a necessidade do x_pred ser um array com p.e 3 valores 
        pred = clf.predict(x_pred)  # outlier labels (0 or 1)
        scores = clf.decision_function(x_pred)  # outlier scores
                
        self.outlier_pred.set(pred)
        self.outlier_score.set(scores)

    # Função change state
    def changeStatus(self,status:str):
        self.status = status
        print(f"O estado atual é: {self.status}")
 
    # Função utilizada para verificar se o novo N é maior que o N atual
    def checkN(self,newN):
        if newN > self.config["currentN"]:
            self.status = "Add"
        elif newN < self.config["currentN"]:
            self.status = "Select"
 
    # Função configure
    def configChange(self,configFile:dict):
        for key, value in configFile.items():
            self.config[key] = value
        print(f"A config mudou para: {self.config}")
        
    # Função Insert
    def Insert_Data(self,container_id,ts,tsvalue):
        if self.Add_Data:
            insert_db_data(self.db_name,"historico",container_id,ts,tsvalue)
            insert_db_data(self.db_name,"train_alg",container_id,ts,tsvalue)
            print(f"O delay do container {container_id} é: {tsvalue}")

        elif not self.Add_Data:
            insert_db_data(self.db_name,"historico",container_id,ts,tsvalue)
            new_row = pd.DataFrame([{
                self.config["id"]: container_id,
                "ts":ts,
                "tsValue": tsvalue,
            }])
            self.test = pd.concat([self.test,new_row],ignore_index=True)

    # Função select
    def selectFromDf(self,n_values):
        keep_last_n_db(self.db_name,"train_alg",n_values)
        self.test.sort_values("ts", ascending=False) # Ordenar os valores
        updatedDf = self.test.head(round(n_values * self.config["p"])) # Selecionar os n mais recentes
        self.test = updatedDf # Atualizar o DF
   
    def updateDf(self,container_id,ts,tsvalue, n_values):
        # keep_last_n_db(self.db_name,"train_alg",n_values-1)
        # insert_db_data(self.db_name,"train_alg",container_id,ts,tsvalue)
        self.df.sort_values("ts", ascending=False)
        df = df.iloc[:-1] #Select N-1 values
        self.Insert_Data(container_id,ts,tsvalue)
 
    def execute(self, message):
    
        if ("_changeState" in message.keys()): # Se a mensagem contiver ordem de mudar de estado
            self.changeStatus(message["_changeState"]) # Função change state
            return 

        elif ("_config" in message.keys()): # Se a mensagem contiver dicionário de configuração (shuts off)
            if "currentN" in message["_config"]: 
                self.checkN(message["_config"]["currentN"])
                # Verifica se o N enviado na configuração é maior ou menor que o N atual
            self.configChange(message["_config"]) # Função config
            return

        # Se não recebeu um _config ou _changeState -> Normal funcionamento
        else:
            if 'ts' not in message.keys() or self.config["id"] not in message.keys():
                print("drop message")
                return
            else:
                if self.config['durationcol'] != "":
                    if (
                        message[self.config["id"]] in self.monitor.keys() and 
                        len(self.monitor[message[self.config["id"]]]) == 1
                        ):

                        print(f"{message[self.config["id"]]} encontrado no dicionário")

                        self.monitor[message[self.config["id"]]].append(message["ts"])

                        if len(self.monitor[message[self.config["id"]]]) == 2:

                            print("2 Valor ts injetado")

                            tsValue = (
                                self.monitor[message[self.config["id"]]][1] - 
                                self.monitor[message[self.config["id"]]][0]
                                )
                            
                            if tsValue>=0:
                                message["tsValue"] = tsValue
                            else:
                                print("Dados do container incorretos - Data Drop")
                            
                            del self.monitor[message[self.config["id"]]]

                    elif not(
                        message[self.config["id"]] in self.monitor.keys()
                        ):
                        self.monitor[message[self.config["id"]]] = [message["ts"]]

                        print(f"{message[self.config["id"]]} adicionado ao dicionário")
                    

            if self.status == "Add" and 'tsValue' in message.keys():
                if table_rows(self.db_name,"train_alg") < self.config["currentN"]:
                    self.Add_Data = True
                    self.Insert_Data(message[self.config["id"]],message["ts"], message["tsValue"]) 

                elif table_rows(self.db_name,"train_alg") >= self.config["currentN"]:
                    self.Add_Data = False
                    if len(self.test)<=round(self.config["p"] * self.config["currentN"]):
                        self.Insert_Data(message[self.config["id"]],message["ts"], message["tsValue"])
                else:
                    self.changeStatus("On")
                    # Passar para off em produção
                    print("Limite de dados de teste e treino atingido!")


            elif self.status == "Select":
                self.selectFromDf(self.config["currentN"])
                self.changeStatus("Off")

            elif self.status == "On":
                # RUN AS FIFO
                self.updateDf(
                    message[self.config["id"]],
                    message["ts"],
                    message["tsValue"],
                    )
                if ('func1' in self.config['Algs'] 
                    and 'tsValue' in message.keys()): 
                    self.func1(message[self.config["id"]])

                if ('func2' in self.config['Algs'] 
                    and 'tsValue' in message.keys()):
                        self.func2(message["tsValue"])
