from pydantic import BaseModel, HttpUrl, Field

class Media(BaseModel):
    url: HttpUrl = Field(description='A valid url of the media img')