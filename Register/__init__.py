import azure.functions as func
import json
import uuid
from datetime import datetime, timezone

from cosmos_client import get_users_container
from auth import hash_password


def main(req: func.HttpRequest) -> func.HttpResponse:

    try:
        body = req.get_json()

        name = body.get("name", "").strip()
        email = body.get("email", "").strip().lower()
        password = body.get("password", "")

        # Validate required fields
        if not name or not email or not password:
            return func.HttpResponse(
                json.dumps({
                    "error": "Name, email, and password are required."
                }),
                mimetype="application/json",
                status_code=400
            )

        # Basic password requirement
        if len(password) < 8:
            return func.HttpResponse(
                json.dumps({
                    "error": "Password must be at least 8 characters."
                }),
                mimetype="application/json",
                status_code=400
            )

        # Connect to Users container
        container = get_users_container()

        # Check whether email already exists
        existing_users = list(
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

        if existing_users:
            return func.HttpResponse(
                json.dumps({
                    "error": "An account with that email already exists."
                }),
                mimetype="application/json",
                status_code=409
            )

        # Hash password before storing it
        password_hash = hash_password(password)

        # Create user document
        user = {
            "id": str(uuid.uuid4()),
            "name": name,
            "email": email,
            "passwordHash": password_hash,
            "provider": "local",
            "createdAt": datetime.now(timezone.utc).isoformat()
        }

        # Save user to Cosmos DB
        container.create_item(body=user)

        return func.HttpResponse(
            json.dumps({
                "message": "Registration successful."
            }),
            mimetype="application/json",
            status_code=201
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
        print(f"Registration error: {e}")

        return func.HttpResponse(
            json.dumps({
                "error": "An internal server error occurred."
            }),
            mimetype="application/json",
            status_code=500
        )