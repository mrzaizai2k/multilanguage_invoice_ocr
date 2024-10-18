import sys
sys.path.append("") 

from fastapi import  HTTPException, Depends
from pydantic import BaseModel
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from fastapi.security import OAuth2PasswordBearer
from ldap3 import Server, Connection, ALL
from src.Utils.utils import timeit, read_config

config_path = "config/config.yaml"
config = read_config(path = config_path)


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# User model
class User(BaseModel):
    username: str
    is_admin: bool

# Token model
class Token(BaseModel):
    access_token: str
    token_type: str

#Real LDAP
# def ldap_authen(username: str, password: str, config:dict):
#     config = config['ldap']
#     ldap_server = config['ldap_server']
#     ldap_port = config['ldap_port']
#     base_dn = config['base_dn']

#     try:
#         server = Server(ldap_server, port=ldap_port, get_info=ALL)
#         user_dn = f"uid={username},{base_dn}"

#         with Connection(server, user=user_dn, password=password) as conn:
#             if conn.bind():
#                 print(f"Authentication successful for user {username}")
#                 is_admin = username.lower() == 'tesla'
#                 return True, is_admin, username
#             else:
#                 print(f"Authentication failed for user {username}")
#                 return False, False, None
#     except Exception as e:
#         print(f"LDAP authentication error: {str(e)}")
#         return False, False, None

def ldap_authen(username: str, password: str, config:dict):
    import os
    from dotenv import load_dotenv
    load_dotenv()
    USERNAME = os.getenv('USERNAME')
    PASSWORD = os.getenv('PASSWORD')

    if username == USERNAME and password==PASSWORD:
        print(f"Authentication successful for user {username}")
        # return is_valid, is_admin, username
        return True, False, username
    else:
        print(f"Authentication failed for user {username}")
        return False, False, None


def create_access_token(secret_key, algorithm, data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=algorithm)
    return encoded_jwt

def get_current_user(token: str, secret_key: str, algorithm: str) -> User:
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, secret_key, algorithms=[algorithm])
        username: str = payload.get("sub")
        is_admin: bool = payload.get("is_admin")
        if username is None:
            raise credentials_exception
        return User(username=username, is_admin=is_admin)
    except JWTError:
        raise credentials_exception



if __name__ == "__main__":  
    config_path = "config/config.yaml"
    ldap_authen(username='gauss', password='password', config=read_config(path=config_path))

    # username: tesla
    # password: password 
    # tesla is admin
    # username: gauss
    # password: password 