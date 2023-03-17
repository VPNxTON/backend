import peewee
import uuid
from secrets import token_urlsafe
import re
from database import db

import datetime
from user import User

from playhouse.postgres_ext import *
# from playhouse.postgres_ext import ArrayField
import logging
logger = logging.getLogger('peewee')
logger.setLevel(logging.ERROR)


class Server(peewee.Model):
    uuid = peewee.UUIDField(primary_key=True, default=uuid.uuid4)
    nft = peewee.CharField(unique=True)  #: ['openvpn', 'mess']
    updated_at = peewee.DateTimeField(default=datetime.datetime.now)
    created_at = peewee.DateTimeField(default=datetime.datetime.now)

    name = peewee.CharField(null=False, unique = True)
    description = peewee.TextField(null=True)
    address = peewee.CharField(null=False)
    type = peewee.CharField(null=True, default='OpenVPN')  #: ['openvpn', 'mess'] 
    port = peewee.IntegerField(default=1194)

    status = peewee.CharField(null=False, default='active')  #: ['active', 'inactive'] 
    icon = peewee.CharField(null=True) #: ['free', 'premium'] 
    countryISO = peewee.CharField(null=True)
    platform = peewee.CharField(null=True) #: ['android', 'free'] 
    raw_config = peewee.TextField(null=True)

    class Meta:
        database = db


class ServerRequest(peewee.Model):
    uuid = peewee.UUIDField(primary_key=True, default=uuid.uuid4)
    updated_at = peewee.DateTimeField(default=datetime.datetime.now)
    created_at = peewee.DateTimeField(default=datetime.datetime.now)
    email = peewee.CharField(null=True)
    user_id = peewee.ForeignKeyField(User, backref="user")
    type = peewee.CharField(null=False, default='OpenVPN') #: ['openvpn', 'mess'] 
    raw_config = peewee.TextField(null=True)

    class Meta:
        database = db


class Subscription(peewee.Model):
    user_id = peewee.ForeignKeyField(User, backref="user")
    uuid = peewee.UUIDField(primary_key=True, default=uuid.uuid4)
    txid = peewee.CharField(null=True)
    expires_at = peewee.DateTimeField(null=True)
    type = peewee.CharField(null=False, default="SUBSCRIPTION")
    status = peewee.CharField(null=False, default='') 
    deviceLimit = peewee.IntegerField(default=3)
    devicesLinked = peewee.IntegerField(default=0)
    updatedAt = peewee.DateTimeField(null=True)
    raw = JSONField(null=True)

    class Meta:
        database = db


class Session(peewee.Model):
    user_id = peewee.ForeignKeyField(User, backref="user")
    address = peewee.CharField(null=False)
    uuid = peewee.UUIDField(primary_key=True, default=uuid.uuid4)
    started_at = peewee.DateTimeField(null=False, default=datetime.datetime.now)
    state = peewee.CharField(null=False, default="start")
    end_at = peewee.DateTimeField(null=True)
    device_data = JSONField(null=True)

    class Meta:
        database = db