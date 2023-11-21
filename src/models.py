"""
Follow the pandas.DataFrame.to_json(orient="table") specification.

>>> result = df.to_json(orient="table")
>>> parsed = loads(result)
>>> dumps(parsed, indent=4)  
{
    "schema": {
        "fields": [
            {
                "name": "index",
                "type": "string"
            },
            {
                "name": "col 1",
                "type": "string"
            },
            {
                "name": "col 2",
                "type": "string"
            }
        ],
        "primaryKey": [
            "index"
        ],
        "pandas_version": "1.4.0"
    },
    "data": [
        {
            "index": "row 1",
            "col 1": "a",
            "col 2": "b"
        },
        {
            "index": "row 2",
            "col 1": "c",
            "col 2": "d"
        }
    ]
}
"""
from typing import Any
from pydantic import BaseModel, Field

JsonRecord = dict[str, Any]


class JsonDataFrameFieldSchema(BaseModel):
    name: str
    type: str


class JsonDataFrameSchema(BaseModel):
    fields: list[JsonDataFrameFieldSchema]
    primary_key: list[str] = Field(default_factory=list, alias="primaryKey")
    pandas_version: str


class JsonDataFrame(BaseModel):
    schema: JsonDataFrameSchema
    data: list[JsonRecord]
