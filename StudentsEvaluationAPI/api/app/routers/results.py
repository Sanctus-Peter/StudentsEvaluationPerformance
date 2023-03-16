from fastapi import APIRouter, status, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from .. import schemas, database, models, utils, oauth2


router = APIRouter(tags=["Students Results"], prefix="/results")