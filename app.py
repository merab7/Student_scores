from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import Column, Integer, String, ForeignKey, create_engine, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, Session

# creating slq lite database
DATABASE_URL = "sqlite:///./students.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# creating table for student-subject relationship
student_subject = Table(
    "student_subject",
    Base.metadata,
    Column("student_id", Integer, ForeignKey("students.id")),
    Column("subject_id", Integer, ForeignKey("subjects.id")),
)


# creating student, subject, score models
class Student(Base):
    __tablename__ = "students"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    surname = Column(String, index=True)
    subjects = relationship(
        "Subject",
        secondary=student_subject,
        back_populates="students",
    )
    scores = relationship("Score", back_populates="student")


class Subject(Base):
    __tablename__ = "subjects"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    students = relationship(
        "Student",
        secondary=student_subject,
        back_populates="subjects",
    )
    scores = relationship("Score", back_populates="subject")


class Score(Base):
    __tablename__ = "scores"
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"))
    subject_id = Column(Integer, ForeignKey("subjects.id"))
    score = Column(Integer)
    student = relationship("Student", back_populates="scores")
    subject = relationship("Subject", back_populates="scores")


# creating tables
Base.metadata.create_all(bind=engine)

# starting fastapi
app = FastAPI()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# making endpoints for updating, geting and deleting data


# create sdudent
@app.post("/students/")
def create_student(name: str, surname: str, db: Session = Depends(get_db)):
    student = Student(name=name, surname=surname)
    db.add(student)
    db.commit()
    db.refresh(student)
    return student


# getting all student
@app.get("/students/")
def get_students(db: Session = Depends(get_db)):
    return db.query(Student).all()


# getting specific student using id
@app.get("/students/{student_id}")
def get_student(student_id: int, db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student


# updating specific student using student id
@app.put("/students/{student_id}")
def update_student(
    student_id: int,
    name: str = None,
    surname: str = None,
    db: Session = Depends(get_db),
):
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    if name:
        student.name = name
    if surname:
        student.surname = surname
    db.commit()
    db.refresh(student)
    return student


# delete student with student id
@app.delete("/students/{student_id}")
def delete_student(student_id: int, db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    db.delete(student)
    db.commit()
    return {"message": "Student deleted"}


# create subject
@app.post("/subjects/")
def create_subject(name: str, db: Session = Depends(get_db)):
    subject = Subject(name=name)
    db.add(subject)
    db.commit()
    db.refresh(subject)
    return subject


# getting all subjects
@app.get("/subjects/")
def get_subjects(db: Session = Depends(get_db)):
    return db.query(Subject).all()


# deleting subject using subject id
@app.delete("/subjects/{subject_id}")
def delete_subject(subject_id: int, db: Session = Depends(get_db)):
    subject = db.query(Subject).filter(Subject.id == subject_id).first()
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")
    db.delete(subject)
    db.commit()
    return {"message": "Subject deleted"}


# create score table
@app.post("/scores/")
def add_score(
    student_id: int, subject_id: int, score: int, db: Session = Depends(get_db)
):
    new_score = Score(student_id=student_id, subject_id=subject_id, score=score)
    db.add(new_score)
    db.commit()
    db.refresh(new_score)
    return new_score


# gett all the scores with subject id and student id
@app.get("/scores/")
def get_scores(db: Session = Depends(get_db)):
    return db.query(Score).all()


# get score with score_id
@app.get("/scores/{score_id}")
def get_score(score_id: int, db: Session = Depends(get_db)):
    score = db.query(Score).filter(Score.id == score_id).first()
    if not score:
        raise HTTPException(status_code=404, detail="Score not found")
    return score


# getting specific score data with score id
@app.delete("/scores/{score_id}")
def delete_score(score_id: int, db: Session = Depends(get_db)):
    score = db.query(Score).filter(Score.id == score_id).first()
    if not score:
        raise HTTPException(status_code=404, detail="Score not found")
    db.delete(score)
    db.commit()
    return {"message": "Score deleted"}
