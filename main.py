from fastapi import FastAPI, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from typing import List
import models
from recommender import MovieRecommender
from pydantic import BaseModel
from database import SessionLocal, engine
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Netflix Benzeri Öneri Sistemi")

# CORS ayarları
origins = [
    "http://localhost:8001",
    "http://127.0.0.1:8001",
    "https://localhost:8001",
    "https://127.0.0.1:8001"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Veritabanı bağlantısı
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Pydantic modelleri
class MovieBase(BaseModel):
    title: str
    genre: str
    release_year: int
    rating: float

class MovieCreate(MovieBase):
    pass

class Movie(MovieBase):
    id: int

    class Config:
        from_attributes = True

class UserBase(BaseModel):
    username: str
    email: str

class UserCreate(UserBase):
    pass

class User(UserBase):
    id: int
    watched_movies: List[Movie] = []

    class Config:
        from_attributes = True

class WatchMovieRequest(BaseModel):
    rating: float

# Öneri sistemi örneği
recommender = MovieRecommender(n_clusters=5)

@app.on_event("startup")
async def startup_event():
    db = SessionLocal()
    try:
        # Öneri sistemini eğit
        recommender.fit(db)
    finally:
        db.close()

# Film ekleme endpoint'i
@app.post("/movies/", response_model=Movie)
def create_movie(movie: MovieCreate, db: Session = Depends(get_db)):
    db_movie = models.Movie(**movie.dict())
    db.add(db_movie)
    db.commit()
    db.refresh(db_movie)
    return db_movie

# Kullanıcı ekleme endpoint'i
@app.post("/users/", response_model=User)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = models.User(**user.dict())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# Film izleme endpoint'i
@app.post("/users/{user_id}/watch/{movie_id}")
def watch_movie(
    user_id: int, 
    movie_id: int, 
    request: WatchMovieRequest = Body(...),
    db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    movie = db.query(models.Movie).filter(models.Movie.id == movie_id).first()
    
    if not user or not movie:
        raise HTTPException(status_code=404, detail="Kullanıcı veya film bulunamadı")
        
    # Kullanıcı-film ilişkisini ekle
    user.watched_movies.append(movie)
    db.commit()
    
    # Öneri sistemini güncelle
    recommender.fit(db)
    
    return {"message": "Film izlendi ve öneri sistemi güncellendi"}

# Öneri alma endpoint'i
@app.get("/users/{user_id}/recommendations", response_model=List[Movie])
def get_recommendations(user_id: int, n_recommendations: int = 5, db: Session = Depends(get_db)):
    recommendations = recommender.recommend_movies(db, user_id, n_recommendations)
    return recommendations

# Küme istatistikleri endpoint'i
@app.get("/clusters/stats")
def get_cluster_stats(db: Session = Depends(get_db)):
    return recommender.get_cluster_statistics(db)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 