import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sqlalchemy.orm import Session
from models import Movie, User
import pandas as pd
import logging

# Logging ayarları
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MovieRecommender:
    def __init__(self, n_clusters=5):
        self.n_clusters = n_clusters
        self.kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        self.scaler = StandardScaler()
        self.movie_features = None
        self.movie_clusters = None
        
    def prepare_features(self, db: Session):
        # Filmlerin özelliklerini hazırla
        movies = db.query(Movie).all()
        logger.info(f"Toplam {len(movies)} film bulundu")
        
        if not movies:
            return []
            
        # Her film için özellik vektörü oluştur
        features = []
        for movie in movies:
            # Daha fazla özellik ekle
            feature = np.array([
                movie.release_year,
                movie.rating,
                len(movie.watched_by),  # İzlenme sayısı
                # Tür özelliklerini sayısal değerlere dönüştür
                1 if 'Action' in movie.genre else 0,
                1 if 'Comedy' in movie.genre else 0,
                1 if 'Drama' in movie.genre else 0,
                1 if 'Sci-Fi' in movie.genre else 0,
                1 if 'Romance' in movie.genre else 0
            ])
            features.append(feature)
            
        self.movie_features = np.array(features)
        # Özellikleri ölçeklendir
        self.movie_features = self.scaler.fit_transform(self.movie_features)
        logger.info(f"Özellik vektörü boyutu: {self.movie_features.shape}")
        return self.movie_features
        
    def fit(self, db: Session):
        features = self.prepare_features(db)
        if len(features) > 0:
            self.kmeans.fit(features)
            self.movie_clusters = self.kmeans.labels_
            logger.info(f"K-means eğitimi tamamlandı. Küme sayısı: {self.n_clusters}")
        
    def get_user_cluster(self, db: Session, user_id: int):
        # Kullanıcının izlediği filmlerin ortalamasını al
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            logger.warning(f"Kullanıcı {user_id} bulunamadı")
            return np.random.randint(0, self.n_clusters)
            
        if not user.watched_movies:
            logger.info(f"Kullanıcı {user_id} henüz film izlememiş")
            return np.random.randint(0, self.n_clusters)
            
        logger.info(f"Kullanıcı {user_id} için {len(user.watched_movies)} film bulundu")
            
        user_features = []
        for movie in user.watched_movies:
            feature = np.array([
                movie.release_year,
                movie.rating,
                len(movie.watched_by),
                1 if 'Action' in movie.genre else 0,
                1 if 'Comedy' in movie.genre else 0,
                1 if 'Drama' in movie.genre else 0,
                1 if 'Sci-Fi' in movie.genre else 0,
                1 if 'Romance' in movie.genre else 0
            ])
            user_features.append(feature)
            
        user_avg_features = np.mean(user_features, axis=0)
        # Kullanıcı özelliklerini ölçeklendir
        user_avg_features = self.scaler.transform([user_avg_features])[0]
        
        # Kullanıcının hangi kümeye ait olduğunu bul
        user_cluster = self.kmeans.predict([user_avg_features])[0]
        logger.info(f"Kullanıcı {user_id} küme {user_cluster}'e atandı")
        return user_cluster
        
    def recommend_movies(self, db: Session, user_id: int, n_recommendations=5):
        if self.movie_clusters is None:
            logger.info("Model henüz eğitilmemiş, en yüksek puanlı filmler öneriliyor")
            movies = db.query(Movie).order_by(Movie.rating.desc()).limit(n_recommendations).all()
            return movies
            
        user_cluster = self.get_user_cluster(db, user_id)
        
        # Kullanıcının izlediği filmleri al
        user = db.query(User).filter(User.id == user_id).first()
        watched_movie_ids = [movie.id for movie in user.watched_movies] if user else []
        logger.info(f"Kullanıcı {user_id} için {len(watched_movie_ids)} izlenmiş film bulundu")
        
        # Aynı kümedeki ve izlenmemiş filmleri öner
        recommendations = []
        for movie, cluster in zip(db.query(Movie).all(), self.movie_clusters):
            if cluster == user_cluster and movie.id not in watched_movie_ids:
                recommendations.append(movie)
                
        logger.info(f"Küme {user_cluster} için {len(recommendations)} öneri bulundu")
        
        # Rating ve izlenme sayısına göre sırala
        recommendations.sort(key=lambda x: (x.rating, len(x.watched_by)), reverse=True)
        
        # Eğer yeterli öneri yoksa, en yüksek puanlı filmleri ekle
        if len(recommendations) < n_recommendations:
            logger.info("Yeterli öneri bulunamadı, en yüksek puanlı filmler ekleniyor")
            additional_movies = db.query(Movie).filter(Movie.id.notin_(watched_movie_ids + [m.id for m in recommendations]))\
                .order_by(Movie.rating.desc())\
                .limit(n_recommendations - len(recommendations))\
                .all()
            recommendations.extend(additional_movies)
        
        return recommendations[:n_recommendations]
        
    def get_cluster_statistics(self, db: Session):
        """Küme istatistiklerini hesapla"""
        if self.movie_clusters is None:
            return []
            
        stats = []
        for cluster_id in range(self.n_clusters):
            cluster_movies = [movie for movie, cluster in zip(db.query(Movie).all(), self.movie_clusters) 
                            if cluster == cluster_id]
            
            if cluster_movies:
                avg_rating = np.mean([movie.rating for movie in cluster_movies])
                avg_year = np.mean([movie.release_year for movie in cluster_movies])
                genres = [genre for movie in cluster_movies for genre in movie.genre.split(',')]
                top_genres = pd.Series(genres).value_counts().head(3).to_dict()
                
                stats.append({
                    'cluster_id': cluster_id,
                    'movie_count': len(cluster_movies),
                    'avg_rating': avg_rating,
                    'avg_year': avg_year,
                    'top_genres': top_genres
                })
        
        return stats 