# Netflix Benzeri Film Öneri Sistemi

# Proje Ekibi

- İpek Iraz Esin
- Yağmur Polat
- Mine Emektar
- Sevgi Berk

Bu proje, K-means kümeleme algoritması kullanarak film önerileri yapan bir FastAPI uygulamasıdır.

## Özellikler

- Kullanıcı ve film yönetimi
- Film izleme ve puanlama sistemi
- K-means algoritması ile kişiselleştirilmiş film önerileri
- Küme istatistikleri görüntüleme

## Kurulum

1. Gerekli paketleri yükleyin:
```bash
pip install -r requirements.txt
```

2. Veritabanını oluşturun:
```bash
python3 init_db.py
```

3. Örnek verileri yükleyin:
```bash
python3 seed_db.py
```

4. Uygulamayı başlatın:
```bash
uvicorn main:app --reload --port 8001
```

## API Endpoint'leri

### Kullanıcı İşlemleri
- `POST /users/` - Yeni kullanıcı ekle
- `POST /users/{user_id}/watch/{movie_id}` - Film izleme kaydı oluştur

### Film İşlemleri
- `POST /movies/` - Yeni film ekle
- `GET /users/{user_id}/recommendations` - Kullanıcıya özel film önerileri al

### İstatistikler
- `GET /clusters/stats` - Küme istatistiklerini görüntüle

## Veritabanı Yapısı

- `users` tablosu: Kullanıcı bilgileri
- `movies` tablosu: Film bilgileri
- `user_movie_association`: Kullanıcı-film ilişkileri

## Öneri Sistemi

Sistem, filmlerin özelliklerini (tür, yıl, puan, izlenme sayısı) kullanarak K-means algoritması ile kümeler oluşturur. Kullanıcının izlediği filmlerin özelliklerine göre bir küme seçilir ve aynı kümedeki izlenmemiş filmler önerilir.

## Geliştirici Notları

- Python 3.8+
- FastAPI
- SQLAlchemy
- scikit-learn
- pandas 
