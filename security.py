from fastapi import Depends, HTTPException
from fastapi.security import APIKeyHeader
from starlette import status
import crud


Authorization = APIKeyHeader(name='Authorization')

def check_session(authorization: str = Depends(Authorization)):
    check = crud.check_session(authorization)
    if check:
        return check
    # else raise 401
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid Session",
    )
