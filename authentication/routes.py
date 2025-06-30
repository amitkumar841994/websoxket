from fastapi import APIRouter
from .views import NewUserRegistration

# Instantiate the class-based view
newuser = NewUserRegistration()

# Use the router from the view
router = newuser.router