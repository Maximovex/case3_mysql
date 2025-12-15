import secrets
from time import time
from typing import Annotated
import uuid
from fastapi import APIRouter, Cookie, Depends, HTTPException, status, Header,Response
from fastapi.security import HTTPBasic, HTTPBasicCredentials

router = APIRouter(tags=["demo-auth"])

security = HTTPBasic()


@router.get("/basic-auth/")
def demo_basic_auth_credentials(
    credentials: Annotated[HTTPBasicCredentials, Depends(security)],
):
    return {
        "message": "Hi",
        "username": credentials.username,
        "password": credentials.password,
    }


usernames_passwords = {
    "admin": "admin",
    "john": "password",
}

static_auth_token = {
    "7f58b9ba59062d977ed8c1e666579d1f7135062f60cdfc54989c8bc0862cbbd4": "admin",
    "7f53c9fd3e69af7fabf2a618e495fbc2089c4337b15944b62207e883119096bc": "password",
}


def get_auth_username(credentials: Annotated[HTTPBasicCredentials, Depends(security)]):
    unauthed_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid username or password",
        headers={"WWW-Authenticate": "Basic"},
    )

    if credentials.username not in usernames_passwords:
        raise unauthed_exc
    if not secrets.compare_digest(
        credentials.password.encode("utf-8"),
        usernames_passwords[credentials.username].encode("utf-8"),
    ):
        raise unauthed_exc
    return credentials.username


def get_username_by_token(token: str = Header(alias="static-auth-token")):
    if username := static_auth_token.get(token):
        return username
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="token unauthorized"
    )


@router.get("/http-header-auth/")
def demo_header_auth(auth_usename: str = Depends(get_username_by_token)):
    return {
        "message": f"Hi, {auth_usename}",
        "username": auth_usename,
    }

COOKIES={}
COOKIE_ID="web-app-session-id"

def generate_session_id():
    return uuid.uuid4().hex

def get_session_data(
        session_id:str=Cookie(alias=COOKIE_ID)
):
    if session_id not in COOKIES:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="not authenticated"
        )
    return COOKIES[session_id]

@router.post("/login-cookie/")
def auth_by_cookie(response:Response,
    auth_username: str = Depends(get_auth_username)):

    session_id=generate_session_id()
    COOKIES[session_id]={
        "username":auth_username,
        "login_at":int(time())
    }
    response.set_cookie(COOKIE_ID,session_id)
    return {
        "result": "OK",
        
    }

@router.get("/check-cookie/")
def demo_check(
    user_session=Depends(get_session_data)
):
    return {
        **user_session
    }