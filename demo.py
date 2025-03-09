import logging
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

logging.basicConfig(level=logging.INFO)

all_mongo_nodes = ['mongo1:27017', 'mongo2:27018', 'mongo3:27019']
ok_nodes = []
failed_nodes = []

for node in all_mongo_nodes:
    mongo_uri = f"mongodb://{node}?directConnection=true&serverSelectionTimeoutMS=2000"
    client = MongoClient(mongo_uri)
    try:
        logging.info(f"Trying to connect to {node}")
        client.admin.command("ping")
        logging.info(f"Connected to {node}")
        ok_nodes.append(node)
    except ConnectionFailure as e:
        logging.info(f"Failed to connect to {node}: {e}")
        failed_nodes.append(node)
        continue

if len(ok_nodes) == 1:
    ok_node = ok_nodes[0]
    mongo_uri = f"mongodb://{ok_node}?directConnection=true&serverSelectionTimeoutMS=2000"
    client = MongoClient(mongo_uri)
    try:
        logging.info(f"Trying to connect to {ok_node}")
        client.admin.command("ping")
        logging.info(f"Connected to {ok_node}")
        cfg = client.admin.command("replSetGetConfig")
        members = cfg["config"]["members"]
        for member in members:
            if member["host"] != ok_node:
                member["priority"] = 0
                member["votes"] = 0
        logging.info(f"New config: {cfg}")
        result = client.admin.command("replSetReconfig", cfg["config"], force=True)
        logging.info(f"Reconfig result: {result}")
    except ConnectionFailure as e:
        logging.info(f"Failed to connect to {ok_node}: {e}")
        

