from dataclasses_avroschema.pydantic import AvroBaseModel
from pydantic import Field


class Cache(AvroBaseModel):
    key: str = Field(description='Key to retrieve the cache')
    data: bytes = Field(description='Data to be cached')


class InvalidateCache(AvroBaseModel):
   key: str = Field(description='This is cache key')

