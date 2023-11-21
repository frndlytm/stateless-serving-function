import io
import json
import logging
import os
import traceback
import sys

import cachetools.func
import flask
import functions_framework
import mlflow.pyfunc
import pandas as pd

from pydantic import BaseModel

from src.models import JsonDataFrame
from src.decorators import timed

logging.basicConfig(level=logging.INFO)


class PredictRequest(BaseModel):
    model_uri: os.PathLike
    target: str
    data: JsonDataFrame


@timed
@cachetools.func.ttl_cache
def get_model(uri: str):
    model = mlflow.pyfunc.load_model(uri)
    return model


@functions_framework.http
def function(request: flask.Request):
    """
    Our stateless serving function entrypoint to our pre-trained
    model.
    """
    try:
        body = PredictRequest.model_validate(request.json)

        # Read the dataframe, relying on pandas.
        data = io.StringIO(body.data.model_dump_json())
        X = pd.read_json(data, orient="table")

        # Generate predictions
        model = get_model(body.model_uri)
        X[body.target] = model.predict(X)

        # Return a response telling where the processed data lives.
        return json.loads(X.to_json(orient="table", index=False))

    except:
        return {"traceback": "".join(traceback.format_exception(*sys.exc_info()))}
