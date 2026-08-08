import azure.functions as func
import json

from azure.cosmos.exceptions import CosmosResourceNotFoundError

from cosmos_client import get_container


def main(req: func.HttpRequest) -> func.HttpResponse:

    try:

        container = get_container()

        try:
            result = container.read_item(
                item="latest",
                partition_key="latest"
            )
        except CosmosResourceNotFoundError:
            return func.HttpResponse(
                json.dumps({
                    "error": "No analysis result cached yet. "
                             "Upload All_Diets.csv to trigger processing."
                }),
                mimetype="application/json",
                status_code=404
            )

        return func.HttpResponse(
            json.dumps(result),
            mimetype="application/json",
            status_code=200
        )

    except Exception as e:

        return func.HttpResponse(
            json.dumps({
                "error": str(e)
            }),
            mimetype="application/json",
            status_code=500
        )