from fastapi import Depends, HTTPException, status, UploadFile
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from StudentsEvaluationAPI.api.app import database, models
import uuid
from datetime import datetime

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hashed(password: str):
    return pwd_context.hash(password)


def verify(attempted_password, usr_password):
    return pwd_context.verify(attempted_password, usr_password)


# print(hashed("12345pass"))
def get_student_with_id(user_id, db: Session = Depends(database.get_db)):
    found_user = db.query(models.Students).filter(models.Students.id == user_id)
    is_found = found_user.first()
    if not is_found:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with id {user_id} not found")
    return is_found


async def validate_file(file: UploadFile, max_size: int = None, mime_types: list = None):
    """
    Validate a file by checking the size and mime types a.k.a file types
    """
    if mime_types and file.content_type not in mime_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You can only upload image for party logo"
        )

    if max_size:
        size = await file.read()
        if len(size) > max_size:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="File size is too big. Limit is 10mb"
            )
        await file.seek(0)
    return file


def generate_suffix():
    # Generate a random 4 digit suffix
    suffix = uuid.uuid4().int % 1000
    # Pad the suffix with zeros to ensure it is at least 4 digits long
    suffix = str(suffix).zfill(3)
    return suffix

# Generate the complete matriculation number
def generate_registration_number():
    suffix = generate_suffix()
    year = datetime.now().year % 100
    return f"STU/{year}/{suffix}"
