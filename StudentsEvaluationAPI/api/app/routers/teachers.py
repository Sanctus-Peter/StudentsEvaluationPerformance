from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import schemas, database, models, utils, oauth2


router = APIRouter(tags=["Teachers"], prefix="/teacher")


@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=schemas.Teacher)
async def create_teacher(
        user: schemas.TeacherCreate, db: Session = Depends(database.get_db),
        role: models.Admins = Depends(oauth2.get_admin_user)
):
    hashed_pwd = utils.hashed(user.password)
    user.password = hashed_pwd
    sub_taught = user.subject_taught
    del user.subject_taught
    new_user = models.Teacher(**user.dict())
    db.add(new_user)
    db.commit()

    if user.class_taught:
        db.query(models.Students).filter(
            models.Students.student_class == user.class_taught
        ).update({"teacher_id": new_user.id}, synchronize_session=False)
        db.commit()

    if sub_taught:
        for subject in sub_taught:
            subject_found = db.query(models.Subjects).filter(models.Subjects.subject == subject).first()
            if not subject_found:
                new_subject = models.Subjects(**{"subject": subject})
                db.add(new_subject)
                db.commit()

                new_teacher_subject = models.TeacherSubject(**{"teacher_id": new_user.id, "subject_id": new_subject.id})
                db.add(new_teacher_subject)
                db.commit()
            else:
                new_teacher_subject = models.TeacherSubject(**{"teacher_id": new_user.id, "subject_id": subject_found.id})
                db.add(new_teacher_subject)
                db.commit()

    db.refresh(new_user)

    return new_user

@router.delete("/{userID}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_teacher(
        userID: int, db: Session = Depends(database.get_db),
        role: str = Depends(oauth2.get_admin_user)
):
    db.query(models.Teacher).where(models.Teacher.id == userID).delete()
    db.commit()
    return

@router.put("/password", status_code=status.HTTP_200_OK)
async def change_password(
        form_data: schemas.UpdatePassword,
        user: models.Teacher = Depends(oauth2.get_teacher),
        db: Session = Depends(database.get_db)
):
    if not utils.verify(form_data.old_password, user.password):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Incorrect password")
    if form_data.new_password != form_data.password:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Passwords do not match")
    user.update({"password": utils.hashed(form_data.new_password)}, synchronize_session=False)
    db.commit()
    db.refresh(user)
    return {"message": "Password updated successfully"}


@router.get("/all-students", response_model=list[schemas.Students])
async def get_all_students(db: Session = Depends(database.get_db), user: models.Teacher = Depends(oauth2.get_teacher)):
    return db.query(models.Students).filter(models.Students.teacher_id == user.id).all()
