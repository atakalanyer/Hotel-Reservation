IF OBJECT_ID('dbo.rezervasyonlar', 'U') IS NOT NULL DROP TABLE dbo.rezervasyonlar;
IF OBJECT_ID('dbo.misafirler', 'U') IS NOT NULL DROP TABLE dbo.misafirler;
IF OBJECT_ID('dbo.odalar', 'U') IS NOT NULL DROP TABLE dbo.odalar;
IF OBJECT_ID('dbo.oda_tipleri', 'U') IS NOT NULL DROP TABLE dbo.oda_tipleri;
GO

CREATE TABLE dbo.oda_tipleri (
    tip_id        INT            IDENTITY(1,1) PRIMARY KEY,
    tip_adi       NVARCHAR(50)   NOT NULL,
    kapasite      INT            NOT NULL,
    gecelik_fiyat DECIMAL(8,2)   NOT NULL
);
GO

CREATE TABLE dbo.odalar (
    oda_id  INT            IDENTITY(1,1) PRIMARY KEY,
    tip_id  INT            NOT NULL,
    oda_no  NVARCHAR(10)   NOT NULL UNIQUE,
    durum   NVARCHAR(20)   NOT NULL DEFAULT 'musait',

    CONSTRAINT FK_odalar_oda_tipleri FOREIGN KEY (tip_id) REFERENCES dbo.oda_tipleri(tip_id)
);
GO

CREATE TABLE dbo.misafirler (
    misafir_id  INT             IDENTITY(1,1) PRIMARY KEY,
    ad          NVARCHAR(50)    NOT NULL,
    soyad       NVARCHAR(50)    NOT NULL,
    telefon     NVARCHAR(15)    NOT NULL,
    email       NVARCHAR(100)   UNIQUE
);
GO

CREATE TABLE dbo.rezervasyonlar (
    rezervasyon_id  INT             IDENTITY(1,1) PRIMARY KEY,
    misafir_id      INT             NOT NULL,
    oda_id          INT             NOT NULL,
    giris_tarihi    DATE            NOT NULL,
    cikis_tarihi    DATE            NOT NULL,
    durum           NVARCHAR(20)    NOT NULL DEFAULT 'beklemede',
    toplam_ucret    DECIMAL(8,2)    NULL,

    CONSTRAINT FK_rezervasyonlar_misafirler FOREIGN KEY (misafir_id) REFERENCES dbo.misafirler(misafir_id),
    CONSTRAINT FK_rezervasyonlar_odalar FOREIGN KEY (oda_id) REFERENCES dbo.odalar(oda_id)
);
GO
