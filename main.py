from fastapi import FastAPI,Request
from authentication.routes import router as auth_routes
# from dashboard.routes import router as userexp
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from dotenv import load_dotenv
import os
load_dotenv()


app = FastAPI()
origins = ["*","http://127.0.0.1:8000"]
app.add_middleware(SessionMiddleware, secret_key=os.getenv('secret_key'))

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  
    allow_credentials=True,  
    allow_methods=["*"],     
    allow_headers=["*"],     
)


templates = Jinja2Templates(directory='Template')
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/Template", StaticFiles(directory="Template"), name="Template")


# Include routers from each app
app.include_router(auth_routes, prefix="/user", tags=["App1"])
# app.include_router(userexp, prefix="/userexp", tags=["App2"])

@app.get("/")
async def root(request:Request):
    state = request.session.get('state', None) 
    return templates.TemplateResponse("New_user.html",{"request": request, "state": state})

@app.get("/register")
async def register(request: Request):
    return templates.TemplateResponse("New_user.html", {"request": request})

# @app.get("/userlogin",name="userlogin")
# async def register(request: Request):
#     return templates.TemplateResponse("userlogin.html", {"request": request})

@app.get("/dashboard",name="dashboard")
async def dashboard(request: Request):
    return templates.TemplateResponse("Chat.html", {"request": request})