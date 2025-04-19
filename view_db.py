from sqlalchemy.orm import Session
from database import SessionLocal
import models

def view_database():
    db = SessionLocal()
    try:
        # Kullanıcıları görüntüle
        print("\nKullanıcılar:")
        users = db.query(models.User).all()
        for user in users:
            print(f"ID: {user.id}, Kullanıcı Adı: {user.username}, Email: {user.email}")
            print("İzlenen Filmler:")
            for movie in user.watched_movies:
                print(f"  - {movie.title} (Rating: {movie.rating})")
            print()

        # Filmleri görüntüle
        print("\nFilmler:")
        movies = db.query(models.Movie).all()
        for movie in movies:
            print(f"ID: {movie.id}, Başlık: {movie.title}, Tür: {movie.genre}, Yıl: {movie.release_year}, Rating: {movie.rating}")
            print(f"İzleyen Kullanıcı Sayısı: {len(movie.watched_by)}")
            print()

    finally:
        db.close()

if __name__ == "__main__":
    view_database() 