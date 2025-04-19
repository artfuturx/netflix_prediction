from sqlalchemy.orm import Session
from database import SessionLocal, engine
import models

# Örnek filmler
sample_movies = [
    {
        "title": "Inception",
        "genre": "Action,Sci-Fi",
        "release_year": 2010,
        "rating": 8.8
    },
    {
        "title": "The Dark Knight",
        "genre": "Action,Drama",
        "release_year": 2008,
        "rating": 9.0
    },
    {
        "title": "Pulp Fiction",
        "genre": "Drama,Crime",
        "release_year": 1994,
        "rating": 8.9
    },
    {
        "title": "The Shawshank Redemption",
        "genre": "Drama",
        "release_year": 1994,
        "rating": 9.3
    },
    {
        "title": "Forrest Gump",
        "genre": "Drama,Romance",
        "release_year": 1994,
        "rating": 8.8
    },
    {
        "title": "The Matrix",
        "genre": "Action,Sci-Fi",
        "release_year": 1999,
        "rating": 8.7
    },
    {
        "title": "Goodfellas",
        "genre": "Drama,Crime",
        "release_year": 1990,
        "rating": 8.7
    },
    {
        "title": "The Godfather",
        "genre": "Drama,Crime",
        "release_year": 1972,
        "rating": 9.2
    },
    {
        "title": "Fight Club",
        "genre": "Drama",
        "release_year": 1999,
        "rating": 8.8
    },
    {
        "title": "The Silence of the Lambs",
        "genre": "Drama,Thriller",
        "release_year": 1991,
        "rating": 8.6
    }
]

def seed_database():
    db = SessionLocal()
    try:
        # Veritabanını temizle
        db.query(models.Movie).delete()
        db.query(models.User).delete()
        db.commit()
        
        # Filmleri ekle
        for movie_data in sample_movies:
            movie = models.Movie(**movie_data)
            db.add(movie)
        
        db.commit()
        print("Veritabanı başarıyla dolduruldu!")
    except Exception as e:
        print(f"Hata oluştu: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_database() 