import os
from azure.cosmos import CosmosClient

COSMOS_ENDPOINT = os.environ["COSMOS_ENDPOINT"]
COSMOS_KEY = os.environ["COSMOS_KEY"]
COSMOS_DATABASE = os.environ["COSMOS_DATABASE"]
COSMOS_CONTAINER = os.environ["COSMOS_CONTAINER"]

client = CosmosClient(
    COSMOS_ENDPOINT,
    COSMOS_KEY
)

database = client.get_database_client(COSMOS_DATABASE)

users_container = database.get_container_client(COSMOS_CONTAINER)