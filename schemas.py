from typing import Any, List, Union
from uuid import UUID
# import uuid
from datetime import datetime
import peewee
from pydantic import BaseModel, Field
from pydantic.utils import GetterDict

def convert_datetime_to_iso_8601_with_z_suffix(dt: datetime) -> str:
    return dt.strftime('%Y-%m-%dT%H:%M:%SZ')

class PeeweeGetterDict(GetterDict):
    def get(self, key: Any, default: Any = None):
        res = getattr(self._obj, key, default)
        if isinstance(res, peewee.ModelSelect):
            return list(res)
        return res


class Auth(BaseModel):
    wallet: str


class Server(BaseModel):
    uuid: UUID
    name: str
    description: str
    countryISO: str
    type: str

    class Config:
        orm_mode = True
        getter_dict = PeeweeGetterDict

class Session(BaseModel):
    user_id: UUID
    uuid: UUID
    started_at: datetime
    state: str
    end_at: UUID

    class Config:
        orm_mode = True
        getter_dict = PeeweeGetterDict

class ServerRequest(BaseModel):
    email: str
    raw_config: str

    class Config:
        orm_mode = True
        getter_dict = PeeweeGetterDict

class User(BaseModel):
    uuid: UUID
    status : str
    created_at : datetime
    token : str
    token_time : datetime

    class Config:
        orm_mode = True
        getter_dict = PeeweeGetterDict

        json_encoders = {
            datetime: convert_datetime_to_iso_8601_with_z_suffix
        }

class Subscription(BaseModel):
    uuid: UUID
    productId: str
    expiresAt: datetime = None
    type: str
    status: str
    deviceLimit: int
    devicesLinked: int

    class Config:
        orm_mode = True
        getter_dict = PeeweeGetterDict

        json_encoders = {
            datetime: convert_datetime_to_iso_8601_with_z_suffix
        }

class Token(BaseModel):
    vpn_token: str
