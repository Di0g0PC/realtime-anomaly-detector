from pydantic import BaseModel
from typing import Optional, Any, List

# class config_schema(BaseModel):
#     changeState: str = ""
#     config: Optional[dict[str, Any]] = {
#         "currentN" : 300 ,
#         "p" : 0.3,  
#         "durationcol": "ON", 
#         "id": "Container Plate",
#         "Algs": ['func1','func2'],
#         }

class config_schema(BaseModel):
    changeState: str = ""
    config: Optional[dict[str, Any]] = {}

# class config_dict(BaseModel):
#     currentN: int = 300,
#     p: float = 0.3, 
#     valuecol: str = "", 
#     durationcol: str = "ON", 
#     id: str = "Container Plate",
#     Algs: List =  ['func1','func2']

# class config_schema(BaseModel):
#     changeState: str = ""
#     config: Optional[config_dict] = None