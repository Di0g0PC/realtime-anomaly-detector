import pandas as pd
from datetime import datetime

def convert_utc (df, col, dropRows=True, format="%Y-%m-%d %H:%M:%S.%f"):

    def create_time_stamp(value):
        try:
            utc = datetime.strptime(value, format)
            return utc.timestamp()
        except:
            return None
    
    df['ts'] = df[col].apply(create_time_stamp)
    # Para dropar todas as linhas com valores nulos
    if dropRows:
        df.dropna(subset = ['ts'],inplace= True)

    return df