import time
from typing import List
import logging
from typing import Optional
from fastapi import Depends, FastAPI, HTTPException, UploadFile, File, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, Response

import io
import os
import shutil
import urllib.parse
from datetime import datetime

import crud, database, models, schemas
from user import User
from database import db_state_default
from security import check_session

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.ERROR)

logger = logging.getLogger("api")
origins = [
    "http://localhost:3000",
    "https://vpnxton.def.team",
    "*"
]

app = FastAPI(openapi_url="/api/openapi.json")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def reset_db_state():
    # database.db._state._state.set(db_state_default.copy())
    # database.db._state.reset()
    pass

def get_db(db_state=Depends(reset_db_state)):
    try:
        database.db.connect()
        yield
    finally:
        if not database.db.is_closed():
            database.db.close()

@app.get("/api/hello", include_in_schema=False)
def read_root():
    return {"Hello": "World"}

########USER###############
@app.post("/api/auth/",  dependencies=[Depends(get_db)])
def auth(wallet: schemas.Auth):
    user = crud.auth(wallet.wallet)
    response = JSONResponse(content={'wallet': user.wallet, 'token':user.token, 'vpn_token':user.vpn_token})
    return response

########SERVER###############
@app.get(
    "/api/servers/{address}/connect", include_in_schema=True,
    dependencies=[Depends(get_db), Depends(check_session)]
)
def connect(address: str, user:  schemas.User = Depends(check_session)):
    server = crud.get_server(address)
    token = user.generate_vpn_token()
    data = server.raw_config + f"\n<auth-user-pass>\n{user.wallet}\n{token}\n</auth-user-pass>"
    return Response(content=data, media_type="text/*")


@app.post("/api/servers/request", include_in_schema=True,
    response_model=schemas.ServerRequest,
    dependencies=[Depends(get_db), Depends(check_session)])

def add_request(request: schemas.ServerRequest, user:  schemas.User = Depends(check_session)):
    return crud.get_or_create_request(request, user)

@app.get(
    "/api/servers", include_in_schema=True, response_model=List[schemas.Server], dependencies=[Depends(get_db)]
)
def get_servers():
    request = crud.list_servers()
    return request

########SESSION###############
@app.get(
    "/api/session/list", include_in_schema=True,
    response_model=List[schemas.Session],
    dependencies=[Depends(get_db), Depends(check_session)]
)
def session_list(user:  schemas.User = Depends(check_session)):
    sessions = crud.list_session(user)
    return sessions

# TODO: добавить проверку подписки, добавить проверку заголовковков
@app.post(
    "/api/session/start", include_in_schema=False,
    dependencies=[Depends(get_db)]
)
def session_start(request: schemas.SessionStart):
    return crud.session_start(request)

# TODO: добавить проверку подписки, добавить проверку заголовковков
@app.post(
    "/api/session/end", include_in_schema=False,
    dependencies=[Depends(get_db)]
)
def session_end(request: schemas.SessionEnd):
    response = crud.end_vpnsession(request)
    return response

########SUBSCRIPTIONS###############
# @app.get(
#     "/api/subscriptions/me", include_in_schema=True,
#     response_model=schemas.Subscription,
#     dependencies=[Depends(get_db), Depends(check_session)]
# )
# def get_subscription(user:  schemas.User = Depends(check_session)):
#     return crud.get_subscription(user = user)


@app.get(
    "/api/user/{wallet}/subscriptions", include_in_schema=True,
    response_model=List[schemas.Subscription],
    dependencies=[Depends(get_db), Depends(check_session)]
)
def list_subscription(user:  schemas.User=Depends(check_session)):
    return crud.list_subscriptions(user = user)

# @app.post(
#     "/api/subscriptions/onboarding-trial", include_in_schema=True, response_model=schemas.Subscription, dependencies=[Depends(get_db), Depends(check_session)]
# )
# def post_subscription_trial(user:  schemas.User = Depends(check_session)):
#     return crud.create_free_subscription(user = user)
