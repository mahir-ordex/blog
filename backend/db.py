from sqlalchemy import create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

engine_file = create_engine("sqlite:///example.db", echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine_file)

Base = declarative_base()


def get_db():
	db: Session = SessionLocal()
	try:
		yield db
	finally:
		db.close()
