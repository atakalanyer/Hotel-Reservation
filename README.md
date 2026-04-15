# Otel Rezervasyon Sistemi

Python (Flask) ile gelistirilmis, Turkce arayuze sahip basit bir otel rezervasyon uygulamasi.
Veritabani SQL Server (SSMS 21 uyumlu) olarak calisir.

## Ozellikler

- Oda tipleri, odalar, misafirler ve rezervasyonlar tablolarini kullanir.
- Yeni rezervasyon olusturma ekrani vardir.
- Tarih cakisma kontrolu yapar.
- Toplam ucreti otomatik hesaplar.
- Mevcut odalar ve rezervasyonlar listelenir.

## Kurulum (SSMS 21 / SQL Server)

1. Python 3.10+ kurulu oldugundan emin olun.
2. SQL Server'da `OtelRezervasyonDB` adli bir veritabani olusturun.
3. ODBC surucusu kurulu olmali (onerilen: `ODBC Driver 18 for SQL Server`).
4. Proje klasorunde terminal acin:

```bash
pip install -r requirements.txt
python app.py
```

5. Tarayicida acin:

`http://127.0.0.1:5000`

6. Tablolari ve ornek veriyi yuklemek icin:

- SSMS'te `schema.sql` sonra `seed.sql` dosyalarini calistirabilirsiniz.
- Veya tek dosya ile `ssms_kurulum.sql` scriptini calistirabilirsiniz (database + tablolar + ornek veri).
- Ya da uygulama ayaktayken:

```bash
curl -X POST http://127.0.0.1:5000/init-db
```

## Baglanti ayarlari (opsiyonel)

Uygulama bu ortam degiskenlerini kullanir:

- `DB_SERVER` (varsayilan: `localhost\SQLEXPRESS`)
- `DB_NAME` (varsayilan: `OtelRezervasyonDB`)
- `DB_DRIVER` (varsayilan: `ODBC Driver 18 for SQL Server`)
- `DB_ENCRYPT` (varsayilan: `yes`)
- `DB_USER`, `DB_PASSWORD` (girildiginde SQL Authentication kullanilir)
- `DB_TRUST_CERT` (varsayilan: `yes`)

## Not

- `orijinal_schema.sql` dosyasi, kullanicinin ilk paylastigi tablo yapisinin birebir kopyasidir.
