import sqlite3

def connect(db_path:str):
    return sqlite3.connect(db_path)

def create_table(db_path:str,table_name:str):
    with connect(db_path) as con:
        cur = con.cursor()
        cur.execute(f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                container_id TEXT,
                ts INTEGER,
                tsValue REAL
            )
        """)
        con.commit()

# def create_table_Without_id(db_path:str,table_name:str):
#     with connect(db_path) as con:
#         cur = con.cursor()
#         cur.execute(f"""
#             CREATE TABLE IF NOT EXISTS {table_name} (
#                 container_id TEXT,
#                 ts INTEGER,
#                 tsValue REAL
#             )
#         """)
#         con.commit()

def insert_db_data(db_path:str,table_name:str,container_id:str,ts:float,tsValue:float):
    with connect(db_path) as con:
        cur = con.cursor()
        # Verificar se o container_id já existe
        cur.execute(f"""
                    Select 1 from {table_name} WHERE container_id = ?""",(container_id,))
        exists = cur.fetchone()
        if not exists:
            cur.execute(
                        f"""INSERT INTO {table_name} (container_id, ts, tsvalue) VALUES (?, ?, ?)""",
                        (container_id, ts, tsValue)
                    )
            con.commit()
            print("Dados inseridos nas tabelas com sucesso")
        else:
            cur.execute(
                f""" UPDATE {table_name} 
                SET ts = ?, 
                    tsvalue = ? 
                WHERE container_id = ?""",
                (ts, tsValue, container_id)
                )
            con.commit()
            print(f"Dados do container {container_id} atualizados com sucesso")
        

def select_last_n_db(db_path:str,table_name:str,n:int):
    with connect(db_path) as con:
        cur = con.cursor()
        cur.execute(f"""SELECT * FROM {table_name} ORDER BY ts DESC LIMIT ? 
            """,(n,))
        resultados = cur.fetchall()
        return resultados
    
def keep_last_n_db(db_path: str, table_name: str, n: int):
    with connect(db_path) as con:
        cur = con.cursor()
        cur.execute(f"""
            DELETE FROM {table_name}
            WHERE id NOT IN (
                SELECT id FROM {table_name}
                ORDER BY ts DESC
                LIMIT ?
            )
        """, (n,))
        con.commit()
        print(f"Dimensão da Tabela {table_name} atualizada")

    
def delete_db_data(db_path:str,table_name:str):
    with connect(db_path) as con:
        cur = con.cursor()
        cur.execute(f"""
            DELETE FROM {table_name}
        """)
        con.commit()

def table_rows(db_path:str,table_name:str)-> int:
    with connect(db_path) as con:
        cur = con.cursor()
        cur.execute(
            f"""SELECT COUNT(*) FROM {table_name};"""
            )
        con.commit()
        return cur.fetchone()[0] 
    
def select_data(db_path:str,table_name:str,cols:str):
    with connect(db_path) as con:
        cur = con.cursor()
        
        cur.execute(f"""SELECT {cols} FROM {table_name}
            """)
        
        con.commit()
        resultados = cur.fetchall()
        return resultados