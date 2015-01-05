#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sqlalchemy import Column, String, create_engine, ForeignKey, Integer, Sequence
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, Sequence('user_id_seq'), primary_key=True)
    name = Column(String(20))
    books = relationship('Book', uselist= False)

class Book(Base):
    __tablename__ = 'book'
    id = Column(Integer, Sequence('user_id_seq'), primary_key=True)
    name = Column(String(20))
    # “多”的一方的book表是通过外键关联到user表的:
    user_id = Column(Integer, ForeignKey('user.id'))

engine = create_engine('mysql+mysqlconnector://root:123@localhost:3306/one2one')
#创建数据表
Base.metadata.create_all(engine)

session = sessionmaker(bind=engine)()

user = User(name='haibin2')
user.books = Book(name='book1')
session.add(user)
session.commit()
session.close()
