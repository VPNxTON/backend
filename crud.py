import schemas
from models import Subscription, Server, ServerRequest, Session
from datetime import datetime
from datetime import timedelta
from fastapi import HTTPException
from starlette import status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse, HTMLResponse
from user import User
import logging

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.ERROR)

logger = logging.getLogger("crud")

def auth(wallet):
    # TODO Добавить проверку по тонапи
    user, _auth = User.auth(wallet)
    if _auth:
        return user
    raise HTTPException(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        detail=jsonable_encoder({"Need wallet or wallet doesn't exists"})
    )

def get_server(address):
    server = Server.get_or_none(nft=address)
    print(address)
    if not server:
        raise HTTPException(
            status_code=404,
            detail=jsonable_encoder({"error": "Server not found"})
        )
    return server


def get_or_create_request(request: schemas.ServerRequest, user_id: str):
    req, created = ServerRequest.get_or_create(user_id=user_id)
    if not created:
        return req

    req.raw_config = request.raw_config
    req.email = request.email
    req.save()
    return req

def check_session(token):
    try:
        user = User.is_auth(token)
    except Exception as e:
        logger.error(e)
        return False
    if user:
        return user
    return False


def list_session(user):
    sessions = Session.select().where(Session.user_id==user.uuid)
    return list(sessions)


def end_vpnsession(user):
    sessions = Session.select().where((Session.user_id==user.uuid) & (Session.state=='start'))
    for session in sessions:
        session.state='end'
        session.end_at=datetime.now()
        session.save()
    return sessions

#TODO поставить заглушку
def get_subscription(user: schemas.User):
    subscriptions = Subscription.select().where((Subscription.user_id==user.uuid) & \
        ((Subscription.expires_at>datetime.now()) | (Subscription.expires_at==None)) & \
        (Subscription.status=='active') 
        ).order_by(-Subscription.expires_at)
    
    if len(subscriptions) > 0:
        subscription = subscriptions[0]
    else:
        return HTMLResponse(status_code=304)
    return subscription


def list_subscriptions(user: schemas.User):
    subscriptions = Subscription.select().where(Subscription.user_id == user.uuid).order_by(-Subscription.expires_at)
    if len(subscriptions) == 0:
        return HTMLResponse(status_code=304)
    return subscriptions
