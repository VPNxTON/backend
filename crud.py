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


def session_start(request):
    logging.info(request)
    user = User.get_or_none(vpn_token=request.vpn_token)
    if not user:
        raise HTTPException(
            status_code=403,
            detail=jsonable_encoder({"error": "Wallet unknown"})
        )
    else:
        Session.create(user_id=user.uuid, address=request.address)
    response = JSONResponse(content={'status': 'connected'})
    return response


def list_servers():
    return list(Server.select())


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


def end_vpnsession(request):
    user = User.get_or_none(vpn_token=request.vpn_token)

    if not user:
        return HTMLResponse(status_code=304)

    sessions = Session.select().where((Session.user_id==user.uuid) & (Session.state=='start'))
    for session in sessions:
        session.state='end'
        session.end_at=datetime.now()
        session.save()
    response = JSONResponse(content={'status': 'closed'})
    return response

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
    return list(subscriptions)
