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

EN

## Hotel Reservation System

A simple hotel reservation application developed using Python (Flask) with a Turkish user interface. The database runs on SQL Server (compatible with SSMS 21).

## Features
Uses tables for room types, rooms, guests, and reservations
Includes a new reservation creation page
Performs date conflict checking
Automatically calculates total price
Lists available rooms and existing reservations

## Setup (SSMS 21 / SQL Server)
Make sure Python 3.10+ is installed
Create a database named OtelRezervasyonDB in SQL Server
Install ODBC driver (recommended: ODBC Driver 18 for SQL Server)

In the project folder, open terminal:

pip install -r requirements.txt
python app.py

Open in browser:

http://127.0.0.1:5000
## Database Setup

To load tables and sample data:

Run schema.sql and then seed.sql in SSMS
OR
Run ssms_kurulum.sql (includes database + tables + sample data)
OR
While the app is running:
curl -X POST http://127.0.0.1:5000/init-db
🔌 Connection Settings (Optional)

The application uses the following environment variables:

DB_SERVER (default: localhost\SQLEXPRESS)
DB_NAME (default: OtelRezervasyonDB)
DB_DRIVER (default: ODBC Driver 18 for SQL Server)
DB_ENCRYPT (default: yes)
DB_USER, DB_PASSWORD (if provided, SQL Authentication is used)
DB_TRUST_CERT (default: yes)
