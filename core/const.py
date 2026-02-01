from pydantic import BaseModel

class Config(BaseModel):
    EnableDebugLog: bool = True


config = Config()