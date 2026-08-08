import io
import logging
import datetime

import azure.functions as func

from data_analysis import analyze_diets
from cosmos_client import get_container


def main(myblob: func.InputStream):

    logging.info(
        f"Blob trigger fired for {myblob.name}, "
        f"{myblob.length} bytes"
    )

    csv_bytes = myblob.read()

    result = analyze_diets(io.BytesIO(csv_bytes))

    result["id"] = "latest"
    result["updatedAt"] = datetime.datetime.utcnow().isoformat()

    container = get_container()
    container.upsert_item(result)

    logging.info("Analysis result cached to Cosmos DB as id='latest'")
