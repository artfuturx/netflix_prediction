from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

# Kullanıcı-Film ilişki tablosu
user_movie_association = Table(
    'user_movie_association',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('movie_id', Integer, ForeignKey('movies.id')),
    Column('rating', Float)
)

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    email = Column(String, unique=True)
    watched_movies = relationship("Movie", secondary=user_movie_association, back_populates="watched_by")

class Movie(Base):
    __tablename__ = 'movies'
    
    id = Column(Integer, primary_key=True)
    title = Column(String)
    genre = Column(String)
    release_year = Column(Integer)
    rating = Column(Float)
    watched_by = relationship("User", secondary=user_movie_association, back_populates="watched_movies")

# Veritabanı bağlantısı
DATABASE_URL = "sqlite:///./netflix_recommender.db"
engine = create_engine(DATABASE_URL)
Base.metadata.create_all(engine) 