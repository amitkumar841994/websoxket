from fastapi import APIRouter
from .views import SendMessage,Contact


router = APIRouter()

msg = SendMessage()
con = Contact()

router.include_router(msg.router)
router.include_router(con.router)

