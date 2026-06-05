from dotenv import load_dotenv
from typing import Literal, get_args
import os
from pathlib import Path
import json

load_dotenv()
LTA_DATAMALL_API_KEY = os.environ.get("LTA_DATAMALL_API_KEY")

DIRECTIONS = Literal["LEFT", "RIGHT"]
current_dir = Path(__file__).resolve().parent
config_path = current_dir.parent / 'config' / 'config.json'

with open(config_path, "r") as config_file:
    app_config = json.load(config_file)

class BusStop():
    def __init__(self, name, id):
        self.name = name
        self.id = id

class BusService():
    def __init__(self, service_no: str):
        self.id = service_no
        self.times = []
        
    def addTime(self, time_str: str):
        self.times.append(time_str)

ENDPOINT_TEMPLATE = app_config.get("endpoint")
STOPS = app_config.get("stops")
API_CALL_INTERVAL_SECONDS = app_config.get("API_CALL_INTERVAL_SECONDS")