import hashlib
import uuid
import datetime
from peewee import Model, UUIDField, CharField, BooleanField, DateTimeField, IntegerField
from datetime import timedelta
from random import choice
from database import db as psql_db
import secrets
import logging

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

logger = logging.getLogger('checker')

_hash = hashlib.sha256()

class BaseModel(Model):
    class Meta:
        database = psql_db
'''
— id
— логин
— хэш пароля
— дата, время создания пользователя
— дата, время последней оплаты пользователя
— дата и время до которой активна подписка
— тип устройства (андроид, ios)
— страна, откуда пользователь
— состояние пользователя (активен, заблокирован, доступны только бесплатные сервера)
— id пользователя, по рефералке которого пришел пользователь.
— реферальный код пользователя
— количество пользователей, которые пришли по рефералке пользователя
'''
class User(BaseModel):
    uuid  = UUIDField(primary_key=True, default=uuid.uuid4)
    deviceId = CharField(null=True)

    email = CharField(max_length=256, null=True)
    wallet = CharField(max_length=256, null=True)

    password = CharField(max_length=256, null=True)
    otp = CharField(max_length=256, null=True)

    active = BooleanField(default=True)
    status = CharField(max_length=256, null=True)

    confirmed_at = DateTimeField(null=True)
    created_at = DateTimeField(default=datetime.datetime.now)
    subscribed_till = DateTimeField(null=True)

    regionCode = CharField(max_length=256, null=True)
    language = CharField(max_length=256, null=True)

    referalUserId = CharField(max_length=256, null=True)
    referalCode = CharField(max_length=256, null=True, default=secrets.token_urlsafe(32))
    referalCount = IntegerField(default=0)

    role = CharField(default='user')
    token = CharField(null=True)
    token_time = DateTimeField(null=True)

    vpn_token = CharField(null=True, unique=True)
    vpn_token_time = DateTimeField(null=True)
    # balance = DecimalField(max_digits=11, decimal_places=2, default=0.00)

    @staticmethod
    def auth(wallet):
        if wallet:
            user, created = User.get_or_create(wallet=wallet, email=wallet)
            if created:
                pass
            user.generate_token()
            return user, True
        else:
            return None, False

    @staticmethod
    def auth_by_otp(wallet, password):
        try:
            user = User.select().where(
                (User.wallet == wallet) |
                (User.email == wallet) |
                (User.uuid == wallet)
                ).get()
        except Exception as e:
            logger.error(e)
            return None, False
        if user.verify_otp(password):
            user.generate_token()
            return user, True
        return None, False

    def is_auth(token):
        if token == None:#Thats critical for model, because token can be None
            raise Exception('No Token')
        try:
            user = User.get(token = token)
        except Exception as e:
            raise Exception('Not Authenticated')
        if User.verify_token(token):
            return user
        else:
            raise Exception('Not Authenticated')

    def set_password(self, password):
        self.password = hashlib.sha256(password.encode('utf-8')).hexdigest()
        self.save()
        return True

    def gen_otp(self):
        password = generate_password() 
        self.otp = hashlib.sha256(password.encode('utf-8')).hexdigest()
        self.save()
        return password

    def verify_password(self, password):
        return self.password == hashlib.sha256(password.encode('utf-8')).hexdigest()

    def verify_otp(self, otp):
        return self.otp == hashlib.sha256(otp.encode('utf-8')).hexdigest()

    def generate_token(self):
        self.token = str(uuid.uuid4())
        self.token_time = datetime.datetime.now()
        self.save()
        return self.token

    def remove_token(self):
        self.token = None
        self.token_time = None
        self.save()
        return True

    @staticmethod
    def verify_token(token):
        if token is None:
            return False
        try:
            user = User.get(token=token)
        except Exception as e:
            logger.error(e)
            return False
        delta = timedelta(minutes=60)
        if datetime.datetime.now()-user.token_time > delta:
            user.token = None
            user.token_time = None
            user.save()
            return False
        return True

    def generate_vpn_token(self):
        self.vpn_token = secrets.token_urlsafe()
        self.vpn_token_time = datetime.datetime.now()
        self.save()
        return self.vpn_token

    def remove_vpn_token(self):
        self.vpn_token = None
        self.vpn_token_time = None
        self.save()
        return True

    @staticmethod
    def verify_vpn_token(vpn_token):
        if vpn_token is None:
            return False
        try:
            user = User.get(vpn_token=vpn_token)
        except Exception as e:
            logger.error(e)
            return False
        delta = timedelta(minutes=3600)
        if datetime.datetime.now()-user.vpn_token_time > delta:
            user.vpn_token = None
            user.vpn_token_time = None
            user.save()
            return False
        return True

    @property
    def as_dict(self):
        d = model_to_dict(self)
        if 'balance' in d:
            d['balance'] = str(self.balance)
        d.pop('password', None)
        return d

charsets = [
    'abcdefghijklmnopqrstuvwxyz',
    'ABCDEFGHIJKLMNOPQRSTUVWXYZ',
    '0123456789',
    '^!%&()=?#<>',
    ]


def generate_password(length=12):
    pwd = []
    charset = choice(charsets)
    while len(pwd) < length:
        pwd.append(choice(charset))
        charset = choice(list(set(charsets) - set([charset])))
    return "".join(pwd)


def init():
    psql_db.drop_tables([User], cascade=True)
    psql_db.create_tables([User])
