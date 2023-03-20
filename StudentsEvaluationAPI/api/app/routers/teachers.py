from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from .. import schemas, database, models, utils, oauth2
from StudentsEvaluationAPI import __CLASSES__, __SUBJECT_LISTS__
from ..schemas import Subject, Term, Classes

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


@router.post("/register-subject/{student_class}/{studentID}", status_code=status.HTTP_201_CREATED)
async def register_subjects(
        studentID: str, student_class: str, subjects: schemas.SubjectCreate,
        user: models.Teacher = Depends(oauth2.get_teacher),
        db: Session = Depends(database.get_db)
):
    if user.class_taught != student_class:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized to perform this function")

    for subject in subjects.subjects:
        subject_found = db.query(models.Subjects).filter(models.Subjects.subject == subject).first()

        new_student_subject = models.StudentSubject(**{"student_id": studentID, "subject_id": subject_found.id})
        db.add(new_student_subject)
        db.commit()

@router.get("/get-classes", response_model=list[str])
async def get_all_classes(role: str = Depends(oauth2.get_teacher)):
    return __CLASSES__

@router.get("/get-subjects", response_model=list[str])
async def get_all_subjects(role: str = Depends(oauth2.get_teacher)):
    return __SUBJECT_LISTS__

@router.get("/{subject}/{student_class}/all-students", response_model=list[schemas.StudentSubject])
async def get_all_students_by_subject(
        subject: Subject, student_class: Classes,
        role: str = Depends(oauth2.get_teacher), db: Session = Depends(database.get_db)
):
    return db.query(models.Students).join(
        models.StudentSubject
    ).join(models.Subjects).filter(
        models.Subjects.subject == subject, models.Students.student_class == student_class
    ).all()

@router.post("/grades/{session:path}/{term}/{student_class}/{subject}")
async def post_grades(
        subject: Subject, student_class: str, term: Term, session: str,
        student_score: list[schemas.PostGrade],
        user: models.Teacher = Depends(oauth2.get_teacher),
        db: Session = Depends(database.get_db)
):
    teacherSubject = db.query(models.TeacherSubject).join(
        models.Subjects
    ).filter(
        models.TeacherSubject.teacher_id == user.id, models.Subjects.subject == subject
    ).first()
    if not teacherSubject:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update score for a subject you are teaching"
        )

    for studentEntry in student_score:
        studentSubject = db.query(models.StudentSubject).join(
            models.Subjects
        ).filter(
            models.StudentSubject.student_id == studentEntry.student_id, models.Subjects.subject == subject
        ).first()
        if not studentSubject:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only update score for a student taking your subject"
            )
        new_student_result = models.Result(
            **{
                "teacher_subject_id": teacherSubject.id,
                "student_subject_id": studentSubject.id,
                "c_a_score": studentEntry.c_a_score,
                "exam_score": studentEntry.exam_score,
                "term": term,
                "session": session
            }
        )
        db.add(new_student_result)
        db.commit()

    return {"message": "Scores updated successfully"}

@router.get("/grades/{session:path}/{term}/{student_class}/{studentID}", response_model=list[schemas.Results])
async def get_grades(
        studentID: str, student_class: str, term: Term, session: str,
        user: models.Teacher = Depends(oauth2.get_teacher),
        db: Session = Depends(database.get_db)
):
    student_found = db.query(models.Students).filter(models.Students.student_id == studentID).first()
    if not student_found:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Student not found")

    if student_found.student_class != user.class_taught:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view score for a student in your class"
        )

    query = db.query(models.Result, models.Subjects.subject).join(
        models.StudentSubject, models.Result.student_subject_id == models.StudentSubject.id
    ).join(
        models.Subjects, models.StudentSubject.subject_id == models.Subjects.id
    ).filter(
        models.StudentSubject.student_id == studentID, models.Result.term == term, models.Result.session == session
    ).all()

    retVal = []
    for result, subject in query:
        result.subject = subject
        retVal.append(result)

    return retVal
