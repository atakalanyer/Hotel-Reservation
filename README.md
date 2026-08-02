# TR Otel Rezervasyon Sistemi

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

# EN Hotel Reservation System

A simple hotel reservation application developed with **Python (Flask)** featuring a **Turkish user interface**.
The application uses **Microsoft SQL Server (SSMS 21 compatible)** as its database.

## Features

- Uses tables for room types, rooms, guests, and reservations.
- Create new hotel reservations.
- Prevents date conflicts for room bookings.
- Automatically calculates the total reservation cost.
- Displays available rooms and existing reservations.

## Installation (SSMS 21 / SQL Server)

1. Make sure **Python 3.10+** is installed.
2. Create a database named `OtelRezervasyonDB` in SQL Server.
3. Install an ODBC driver (recommended: `ODBC Driver 18 for SQL Server`).
4. Open a terminal in the project directory and run:

```bash
pip install -r requirements.txt
python app.py
```

5. Open your browser and navigate to:

`http://127.0.0.1:5000`

6. To initialize the database:

- Run `schema.sql` followed by `seed.sql` in SSMS.
- Or execute `ssms_kurulum.sql` to create the database, tables, and sample data in a single script.
- Alternatively, while the application is running, execute:

```bash
curl -X POST http://127.0.0.1:5000/init-db
```

## Database Configuration (Optional)

The application supports the following environment variables:

- `DB_SERVER` (default: `localhost\SQLEXPRESS`)
- `DB_NAME` (default: `OtelRezervasyonDB`)
- `DB_DRIVER` (default: `ODBC Driver 18 for SQL Server`)
- `DB_ENCRYPT` (default: `yes`)
- `DB_USER`, `DB_PASSWORD` (used when SQL Server Authentication is enabled)
- `DB_TRUST_CERT` (default: `yes`)
