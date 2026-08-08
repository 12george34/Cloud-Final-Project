import os
from azure.cosmos import CosmosClient, PartitionKey

# App settings you need to add in local.settings.json (local) and
# Function App > Configuration (deployed):
#   COSMOS_ENDPOINT   -> your Cosmos account URI
#   COSMOS_KEY        -> your Cosmos account primary key
#   COSMOS_DATABASE   -> e.g. "DietAnalysisDB"
#   COSMOS_CONTAINER  -> e.g. "AnalysisResults"

_client = None


def get_container():
    global _client

    if _client is None:
        _client = CosmosClient(
            url=os.environ["COSMOS_ENDPOINT"],
            credential=os.environ["COSMOS_KEY"]
        )

    # Shared throughput at the DATABASE level (not per-container) is what
    # keeps you inside the Cosmos free tier's 1000 RU/s when B's containers
    # live in this same database.
    database = _client.create_database_if_not_exists(
        id=os.environ["COSMOS_DATABASE"],
        offer_throughput=400
    )

    container = database.create_container_if_not_exists(
        id=os.environ["COSMOS_CONTAINER"],
        partition_key=PartitionKey(path="/id")
    )

    return container
