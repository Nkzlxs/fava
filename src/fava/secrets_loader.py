import json
import pathlib

with open(pathlib.Path(pathlib.Path.cwd(),"data/secrets.json"),"r") as f:
    tmp = json.loads(f.read())

    SECRET_KEY = tmp["secret"]
    USER_LIST = tmp["users"]