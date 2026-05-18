from db import Base
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True,autoincrement=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    bio = Column(String)
    role = Column(String)
    blogs = relationship("Blog", back_populates="author", cascade="all, delete-orphan")



class Blog(Base):
    __tablename__ = "blogs"

    id = Column(Integer, primary_key=True,autoincrement=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    author = relationship("User", back_populates="blogs")

class Comments(Base):
    __tablename__ = "comments"

    id = Column(Integer,primary_key=True, autoincrement=True)
    text = Column(String)
    blog_id = Column(Integer, ForeignKey("blogs.id"),nullable=False)




