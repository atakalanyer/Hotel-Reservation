INSERT INTO oteller (otel_adi, sehir, adres, aciklama, gorsel_yolu) VALUES
(N'Bogaz Manzara Otel', N'Istanbul', N'Besiktas Sahil Cad. No:12', N'Bogaz manzarali sehir oteli.', N'img/oteller/images.jpg'),
(N'Kapadokya Kaya Otel', N'Nevsehir', N'Goreme Turizm Sok. No:7', N'Vadilerde essiz konum ve balon turu deneyimi.', N'img/oteller/terrace.jpg'),
(N'Ege Mavi Otel', N'Izmir', N'Cesme Marina Yolu No:23', N'Denize sifir yaz tatili oteli.', N'img/oteller/mavi-ege-butik-otel.jpg'),
(N'Ankara Is Merkezi Otel', N'Ankara', N'Cankaya Is Kuleleri No:5', N'Merkezi konumlu is ve toplantı oteli.', N'img/oteller/jw-marriott-ankara-ankara-one-cikan-resim-76532480.jpg');
GO

INSERT INTO kullanicilar (kullanici_adi, sifre, rol, ad_soyad) VALUES
('kullanici', '123456', 'kullanici', 'Ornek Kullanici'),
('admin', 'admin123', 'admin', 'Sistem Yoneticisi');
GO

INSERT INTO oda_tipleri (tip_adi, kapasite, gecelik_fiyat) VALUES
('Standart Oda', 2, 1500.00),
('Deluxe Oda', 3, 2300.00),
('Aile Odasi', 4, 3200.00),
('Suit Oda', 2, 4500.00);
GO

INSERT INTO odalar (otel_id, tip_id, oda_no, durum) VALUES
(1, 1, '101', 'musait'),
(1, 2, '201', 'musait'),
(2, 1, '101', 'musait'),
(2, 3, '301', 'musait'),
(3, 2, '201', 'musait'),
(3, 4, '401', 'musait'),
(4, 1, '101', 'musait'),
(4, 2, '202', 'musait');
GO
