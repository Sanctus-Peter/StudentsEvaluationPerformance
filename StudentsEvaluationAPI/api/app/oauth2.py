from jose import JWTError, jwt
from datetime import datetime, timedelta
from . import schemas, database, models
from fastapi import Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from .config import settings


admin_oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/administrator/sign-in")
parent_oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/guardian/sign-in")
teacher_oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/teacher/sign-in")
student_oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/student/sign-in")


SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_tok_expire_minutes

credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=f"Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )


def create_access_token(data: dict):
    encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    encode.update({"exp": expire})

    encoded = jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded


def verify_tok(token: str, credentialsException):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        _id = payload.get("user_id")

        if not _id:
            raise credentialsException
        tok_data = schemas.TokData(id=_id)
    except JWTError:
        raise credentialsException
    return tok_data


def get_current_user(
        token: str = Depends(student_oauth2_scheme),
        db: Session = Depends(database.get_db)
):
    token = verify_tok(token, credentials_exception)
    user = db.query(models.Students).filter(models.Students.id == token.id).first()
    return user


def get_admin_user(
        token: str = Depends(admin_oauth2_scheme),
        db: Session = Depends(database.get_db)
):
    token = verify_tok(token, credentials_exception)
    user = db.query(models.Admins).filter(models.Admins.id == token.id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You are not authorized to execute this action"
        )
    return user

def get_teacher(
        token: str = Depends(teacher_oauth2_scheme),
        db: Session = Depends(database.get_db)
):
    token = verify_tok(token, credentials_exception)
    user = db.query(models.Teacher).filter(models.Teacher.id == token.id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You are not authorized to execute this action"
        )
    return user


def get_guardian(
        token: str = Depends(parent_oauth2_scheme),
        db: Session = Depends(database.get_db)
):
    token = verify_tok(token, credentials_exception)
    user = db.query(models.Admins).filter(models.Guardians.id == token.id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You are not authorized to execute this action"
        )
    return user


