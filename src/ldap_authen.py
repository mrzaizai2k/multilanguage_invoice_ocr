import sys
sys.path.append("") 

from fastapi import FastAPI, Request, HTTPException, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from uuid import uuid4
from sqlalchemy import create_engine, Column, String, Integer, DateTime
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from ldap3 import Server, Connection, ALL, SUBTREE
from datetime import datetime, timedelta
import os

def LDAP_AUTH(username, password):
    # LDAP server details
    ldap_server = "ldap.forumsys.com"
    ldap_port = 389
    base_dn = "dc=example,dc=com"

    try:
        # Connect to the LDAP server
        server = Server(ldap_server, port=ldap_port, get_info=ALL)
        
        # Attempt to bind directly with the user's credentials
        user_dn = f"uid={username},{base_dn}"
        with Connection(server, user=user_dn, password=password) as conn:
            if conn.bind():
                print(f"Authentication successful for user {username}")
                return True
            else:
                print(f"Authentication failed for user {username}")
                return False

    except Exception as e:
        print(f"LDAP authentication error: {str(e)}")
        return False

app = FastAPI()

# Adjust the template directory path
templates = Jinja2Templates(directory=os.path.join("src", "static"))

# Adjust the static files directory path
static_dir = os.path.join("src", "static")
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Create an in-memory SQLite database
engine = create_engine('sqlite:///:memory:', echo=True)

# Create a session factory
SessionLocal = sessionmaker(bind=engine)

# Create a base class for declarative models
Base = declarative_base()

# Define a Session model
class Session(Base):
    __tablename__ = 'session'
    id = Column(String(36), primary_key=True)
    username = Column(String, nullable=True)
    session_timeout = Column(DateTime, nullable=True)

# Create all tables in the database
Base.metadata.create_all(engine)

@app.route('/auth-web', methods=['GET', 'POST'])
async def auth_web(request: Request):
    error_message = None

    if request.method == 'POST':
        form = await request.form()
        username = form.get('username')
        password = form.get('password')

        if LDAP_AUTH(username, password):
            # Update the expiration time (e.g., 30 minutes from now)
            expiration_time = datetime.now() + timedelta(minutes=30)

            # Generate a unique session ID
            session_id = str(uuid4())

            # Store the session information in the database with the correct username
            db = SessionLocal()
            session = Session(id=session_id, username=username, session_timeout=expiration_time)
            db.add(session)
            db.commit()
            db.close()
            print('added:', session_id, username, expiration_time)
            # Set cookies with session information
            response = RedirectResponse(url='/protected-web')
            response.set_cookie(key='session_id', value=session_id)
            response.set_cookie(key='message', value="Authentication successful")
            response.set_cookie(key='username', value=username)

            return response
        else:
            error_message = 'Invalid credentials'

    return templates.TemplateResponse("login.html", {"request": request, "error_message": error_message})

@app.get('/protected-web', response_class=HTMLResponse)
@app.post('/protected-web', response_class=HTMLResponse)
async def protected_web(request: Request):
    session_id = request.cookies.get('session_id')
    username = request.cookies.get('username')
    message = request.cookies.get('message')

    # Check if both session_id and username are present in cookies
    if session_id and username:
        db = SessionLocal()
        # Query the database to find the user with the given username and session ID
        session = db.query(Session).filter(
            Session.id == session_id,
            Session.username == username,
            Session.session_timeout > datetime.now(),  # Check if the session has not expired
        ).order_by(Session.session_timeout.desc()).first()
        db.close()

        if session:
            return HTMLResponse(content=f"<h1>Hello user {username}!</h1> , {message}")
        else:
            print("Authentication failed for session_id:", session_id)
            raise HTTPException(status_code=401, detail='Unauthorized')
    else:
        print("Session ID or username not present in cookies.")
        raise HTTPException(status_code=401, detail='Unauthorized')

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8148)

    # username: tesla
    # password