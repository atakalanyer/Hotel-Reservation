INSERT INTO oda_tipleri (tip_adi, kapasite, gecelik_fiyat) VALUES
('Standart Oda', 2, 1500.00),
('Deluxe Oda', 3, 2300.00),
('Aile Odasi', 4, 3200.00),
('Suit Oda', 2, 4500.00);
GO

INSERT INTO odalar (tip_id, oda_no, durum) VALUES
(1, '101', 'musait'),
(1, '102', 'musait'),
(2, '201', 'musait'),
(2, '202', 'musait'),
(3, '301', 'musait'),
(4, '401', 'musait');
GO
