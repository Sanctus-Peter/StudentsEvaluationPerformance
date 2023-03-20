from sqlalchemy.orm import relationship
from .database import Base
from sqlalchemy import Column, Integer, String, TIMESTAMP, text, ForeignKey, Float


class Students(Base):
    __tablename__ = 'students'
    id = Column(Integer, primary_key=True, nullable=False)
    firstname = Column(String, nullable=False)
    lastname = Column(String, nullable=False)
    middlename = Column(String)
    email = Column(String, nullable=False)
    address = Column(String, nullable=False)
    gender = Column(String, nullable=False)
    student_class = Column(String, nullable=False)
    student_id = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    department = Column(String, nullable=True)
    reg_date = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("NOW()"))
    parent_id = Column(Integer, ForeignKey("guardians.id", ondelete="CASCADE"))
    teacher_id = Column(Integer, ForeignKey("teachers.id", ondelete="CASCADE"))

    parent = relationship("Guardians", back_populates="children")
    teacher = relationship("Teacher", back_populates="student")
    student_subject = relationship(
        "StudentSubject", back_populates="student", cascade="all, delete", passive_deletes=True
    )


class Guardians(Base):
    __tablename__ = 'guardians'
    id = Column(Integer, primary_key=True, nullable=False)
    title = Column(String, nullable=False)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    gender = Column(String, nullable=False)
    address = Column(String, nullable=False)
    mobile_no = Column(String, nullable=False)
    password = Column(String, nullable=False)
    reg_date = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("NOW()"))

    children = relationship(
        "Students", back_populates="parent", cascade="all, delete", passive_deletes=True
    )


class Teacher(Base):
    __tablename__ = 'teachers'
    id = Column(Integer, primary_key=True, nullable=False)
    title = Column(String, nullable=False)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    gender = Column(String, nullable=False)
    address = Column(String, nullable=False)
    mobile_no = Column(String, nullable=False)
    password = Column(String, nullable=False)
    class_taught = Column(String)
    reg_date = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("NOW()"))

    student = relationship(
        "Students", back_populates="teacher", cascade="all, delete", passive_deletes=True
    )
    teacher_subject = relationship(
        "TeacherSubject", back_populates="teacher", cascade="all, delete", passive_deletes=True
    )


class Admins(Base):
    __tablename__ = 'admins'
    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    reg_date = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("NOW()"))

    news_article = relationship("News", back_populates="owner", cascade="all, delete", passive_deletes=True)


class News(Base):
    __tablename__ = 'news'
    id = Column(Integer, primary_key=True, nullable=False)
    title = Column(String, nullable=False)
    content = Column(String, nullable=False)
    category = Column(String, nullable=False)
    image = Column(String)
    author_id = Column(Integer, ForeignKey('admins.id', ondelete="CASCADE"), nullable=False)
    date = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("NOW()"))

    owner = relationship("Admins", back_populates="news_article")


class Result(Base):
    __tablename__ = 'results'
    id = Column(Integer, primary_key=True, nullable=False)
    student_subject_id = Column(Integer, ForeignKey('student_subjects.id', ondelete="CASCADE"), nullable=False)
    teacher_subject_id = Column(Integer, ForeignKey('teacher_subjects.id', ondelete="CASCADE"), nullable=False)
    c_a_score = Column(Float, nullable=False)
    exam_score = Column(Float, nullable=False)
    term = Column(String, nullable=False)
    session = Column(String, nullable=False)
    time_logged = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("NOW()"))

    student_subject = relationship("StudentSubject", back_populates="result")
    teacher_subject = relationship("TeacherSubject", back_populates="result")


class StudentSubject(Base):
    __tablename__ = 'student_subjects'
    id = Column(Integer, primary_key=True, nullable=False)
    student_id = Column(String, ForeignKey('students.student_id', ondelete="CASCADE"), nullable=False)
    subject_id = Column(Integer, ForeignKey('subjects.id', ondelete="CASCADE"), nullable=False)

    student = relationship("Students", back_populates="student_subject")
    subject = relationship("Subjects", back_populates="student_subject")
    result = relationship(
        "Result", back_populates="student_subject", cascade="all, delete", passive_deletes=True
    )

class TeacherSubject(Base):
    __tablename__ = 'teacher_subjects'
    id = Column(Integer, primary_key=True, nullable=False)
    teacher_id = Column(Integer, ForeignKey('teachers.id', ondelete="CASCADE"), nullable=False)
    subject_id = Column(Integer, ForeignKey('subjects.id', ondelete="CASCADE"), nullable=False)

    teacher = relationship("Teacher", back_populates="teacher_subject")
    subject = relationship("Subjects", back_populates="teacher_subject")
    result = relationship(
        "Result", back_populates="teacher_subject", cascade="all, delete", passive_deletes=True
    )


class Subjects(Base):
    __tablename__ = 'subjects'
    id = Column(Integer, primary_key=True, nullable=False)
    subject = Column(String, nullable=False, unique=True)

    student_subject = relationship(
        "StudentSubject", back_populates="subject", cascade="all, delete", passive_deletes=True
    )
    teacher_subject = relationship(
        "TeacherSubject", back_populates="subject", cascade="all, delete", passive_deletes=True
    )
