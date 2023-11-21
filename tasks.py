import json
import io
import os

import pandas as pd
import requests
from invoke import Context, task

GCP_DEFAULT_REGION = os.getenv("GCP_DEFAULT_REGION", "us-east-1")
HERE = os.path.dirname(os.path.abspath(__file__))


@task
def demo(_: Context):
    with open(os.path.join(HERE, "data", "processed", "payload.json")) as fh:
        # Read the records that need predictions from a payload.json file
        request = {
            "model_uri": "data/models/SimpleImputer",
            "target": "compensation",
            "data": json.load(fh),
        }
        print(json.dumps(request, indent=2))

    # Construct a request to the service for the locally stored model URI
    # fmt:off

    response = requests.post(
        "http://localhost:8080/",
        headers={"Content-Type": "application/json"},
        json=request,
    )
    # fmt:on

    # Show that the compensation column has been imputed
    print(response.text)


@task
def deploy(
    c: Context,
    region: str = GCP_DEFAULT_REGION,
):
    print("Deploying to GCP...")
    c.run(
        f"""gcloud functions deploy python-http-function \
            --gen2 \
            --runtime=python312 \
            --region={region} \
            --source=. \
            --entry-point=hello_http \
            --trigger-http \
            --allow-unauthenticated
        """
    )
