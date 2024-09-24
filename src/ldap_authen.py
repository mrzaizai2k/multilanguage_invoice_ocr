import sys
sys.path.append("") 

import os
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from ldap3 import Server, Connection, ALL
from src.Utils.utils import timeit, read_config

from dotenv import load_dotenv
load_dotenv()


config_path = "config/config.yaml"
config = read_config(path = config_path)

SECRET_KEY = os.getenv('SECRET_KEY')
ALGORITHM = os.getenv('ALGORITHM')
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES'))


app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Replace with your React app's URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# User model
class User(BaseModel):
    username: str
    is_admin: bool

# Token model
class Token(BaseModel):
    access_token: str
    token_type: str

@timeit
def ldap_authen(username: str, password: str, config:dict):
    config = config['ldap']
    ldap_server = config['ldap_server']
    ldap_port = config['ldap_port']
    base_dn = config['base_dn']

    try:
        server = Server(ldap_server, port=ldap_port, get_info=ALL)
        user_dn = f"uid={username},{base_dn}"

        with Connection(server, user=user_dn, password=password) as conn:
            if conn.bind():
                print(f"Authentication successful for user {username}")
                is_admin = username.lower() == 'tesla'
                return True, is_admin, username
            else:
                print(f"Authentication failed for user {username}")
                return False, False, None
    except Exception as e:
        print(f"LDAP authentication error: {str(e)}")
        return False, False, None

@timeit
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        import time
        start =time.time()
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        is_admin: bool = payload.get("is_admin")
        if username is None:
            raise credentials_exception
        token_data = User(username=username, is_admin=is_admin)
        end =time.time()
        print("get current user", end-start)

    except JWTError:
        raise credentials_exception
    return token_data

@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    is_valid, is_admin, username = ldap_authen(username = form_data.username, 
                                             password=form_data.password, 
                                             config=config)
    if is_valid:
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": username, "is_admin": is_admin}, expires_delta=access_token_expires
        )
        return {"access_token": access_token, "token_type": "bearer"}
    else:
        raise HTTPException(status_code=401, detail="Incorrect username or password")

@app.get("/users/me")
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

if __name__ == "__main__":  
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8148)

    # username: tesla
    # password: password 
    # tesla is admin
    # username: gauss
    # password: password 