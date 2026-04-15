-- =============================================
-- OTEL REZERVASYON SİSTEMİ — ORİJİNAL ŞEMA
-- Kullanıcının ilk gönderdiği sürüm (birebir)
-- =============================================

CREATE TABLE oda_tipleri (
    tip_id        INT           PRIMARY KEY AUTO_INCREMENT,
    tip_adi       VARCHAR(50)   NOT NULL,
    kapasite      INT           NOT NULL,
    gecelik_fiyat DECIMAL(8,2)  NOT NULL
);

CREATE TABLE odalar (
    oda_id  INT          PRIMARY KEY AUTO_INCREMENT,
    tip_id  INT          NOT NULL,
    oda_no  VARCHAR(10)  NOT NULL UNIQUE,
    durum   VARCHAR(20)  NOT NULL DEFAULT 'musait',

    FOREIGN KEY (tip_id) REFERENCES oda_tipleri(tip_id)
);

CREATE TABLE misafirler (
    misafir_id  INT           PRIMARY KEY AUTO_INCREMENT,
    ad          VARCHAR(50)   NOT NULL,
    soyad       VARCHAR(50)   NOT NULL,
    telefon     VARCHAR(15)   NOT NULL,
    email       VARCHAR(100)  UNIQUE
);

CREATE TABLE rezervasyonlar (
    rezervasyon_id  INT           PRIMARY KEY AUTO_INCREMENT,
    misafir_id      INT           NOT NULL,
    oda_id          INT           NOT NULL,
    giris_tarihi    DATE          NOT NULL,
    cikis_tarihi    DATE          NOT NULL,
    durum           VARCHAR(20)   NOT NULL DEFAULT 'beklemede',
    toplam_ucret    DECIMAL(8,2),

    FOREIGN KEY (misafir_id) REFERENCES misafirler(misafir_id),
    FOREIGN KEY (oda_id)     REFERENCES odalar(oda_id)
);
