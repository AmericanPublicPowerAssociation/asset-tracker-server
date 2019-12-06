from sqlalchemy import Column, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.types import (
    Integer,
    PickleType,
    String)


Base = declarative_base()


class Busbar(Base):
    __tablename__ = 'busbar'
    id = Column(String, primary_key=True)


class Generator(Base):
    __tablename__ = 'generator'
    id = Column(String, primary_key=True)


class Transformer(Base):
    __tablename__ = 'transformer'
    id = Column(String, primary_key=True)


class Regulator(Base):
    __tablename__ = 'regulator'
    id = Column(String, primary_key=True)


class Line(Base):
    __tablename__ = 'line'
    id = Column(String, primary_key=True)


class LineType(Base):
    __tablename__ = 'line_type'
    id = Column(String, primary_key=True)


class Meter(Base):
    __tablename__ = 'meter'
    id = Column(String, primary_key=True)


class Capacitor(Base):
    __tablename__ = 'capacitor'
    id = Column(String, primary_key=True)


class Switch(Base):
    __tablename__ = 'switch'
    id = Column(String, primary_key=True)


class Substation(Base):
    __tablename__ = 'substation'
    id = Column(String, primary_key=True)


class Pole(Base):
    __tablename__ = 'pole'
    id = Column(String, primary_key=True)


class Task(Base):
    __tablename__ = 'task'
    id = Column(String, primary_key=True)
