from fastapi import FastAPI, Depends
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from pydantic import BaseModel
from typing import Optional
import uvicorn

app = FastAPI()

engine = create_engine("postgresql://tunggal:laggnut@localhost:5432/gaguna")
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base(engine)

class tableUser(Base):
    __tablename__ = "testing"
    __table_args__ = {"autoload": True}

class User(BaseModel):
    username: str
    password: Optional[str]

    class Config:
        orm_mode = True

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get('/users')
def find_users (db: SessionLocal = Depends(get_db)):
    users = db.query(tableUser).all()
    return users

@app.get('/user/{username}')
def find_user (username: str, db: SessionLocal = Depends(get_db)):
    user = db.query(tableUser).where(tableUser.username == username).first()
    return user

@app.post('/createuser/')
def create_user (user: User, db: SessionLocal = Depends(get_db)):
    newUser = tableUser(**user.dict())
    db.add(newUser)
    db.commit()
    return {
                'status': 200,
                'message': 'Successfully insert data',
                'data': user.dict()
            }

@app.put('/updateuser/{username}')
def create_user (username: str, user: User, db: SessionLocal = Depends(get_db)):
    checkUser = db.query(tableUser).where(tableUser.username == username).first()
    print(checkUser, dir(checkUser))
    if checkUser :
        checkUser.username = user.dict()['username']
        checkUser.password = user.dict()['password']
        db.commit()
        return {
                    'status': 200,
                    'message': 'Successfully update data',
                    'data': user.dict()
                }
    else :
        return {
                    'status': 401,
                    'message': 'Bad request - User not Found',
                }

@app.put('/deleteuser/{username}')
def create_user (username: str, db: SessionLocal = Depends(get_db)):
    checkUser = db.query(tableUser).where(tableUser.username == username).first()
    print(checkUser, dir(checkUser))
    if checkUser :
        db.query(tableUser).where(tableUser.username == username).delete()
        db.commit()
        return {
                    'status': 200,
                    'message': 'Successfully delete data',
                    'data': username
                }
    else :
        return {
                    'status': 401,
                    'message': 'Bad request - User not Found',
                }

if __name__ == "__main__" :
    uvicorn.run("main:app", host="0.0.0.0", port=8080, log_level="info", reload=True, debug=True, workers=2)