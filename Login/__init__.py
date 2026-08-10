import azure.functions as func
import json

from cosmos_client import get_users_container
from auth import verify_password


def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        body = req.get_json()

        email = body.get("email", "").strip().lower()
        password = body.get("password", "")

        if not email or not password:
            return func.HttpResponse(
                json.dumps({
                    "error": "Email and password are required."
                }),
                mimetype="application/json",
                status_code=400
            )

        container = get_users_container()

        users = list(
            container.query_items(
                query="""
                    SELECT * FROM c
                    WHERE c.email = @email
                """,
                parameters=[
                    {
                        "name": "@email",
                        "value": email
                    }
                ],
                enable_cross_partition_query=True
            )
        )

        if not users:
            return func.HttpResponse(
                json.dumps({
                    "error": "Invalid email or password."
                }),
                mimetype="application/json",
                status_code=401
            )

        user = users[0]

        if not verify_password(password, user["passwordHash"]):
            return func.HttpResponse(
                json.dumps({
                    "error": "Invalid email or password."
                }),
                mimetype="application/json",
                status_code=401
            )

        return func.HttpResponse(
            json.dumps({
                "message": "Login successful.",
                "user": {
                    "id": user["id"],
                    "name": user["name"],
                    "email": user["email"]
                }
            }),
            mimetype="application/json",
            status_code=200
        )

    except ValueError:
        return func.HttpResponse(
            json.dumps({
                "error": "Invalid JSON request."
            }),
            mimetype="application/json",
            status_code=400
        )

    except Exception as e:
        print(f"Login error: {e}")

        return func.HttpResponse(
            json.dumps({
                "error": "An internal server error occurred."
            }),
            mimetype="application/json",
            status_code=500
        )