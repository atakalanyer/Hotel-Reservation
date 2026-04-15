import os
from datetime import datetime
from pathlib import Path

import pyodbc
from flask import Flask, flash, g, redirect, render_template, request, url_for


BASE_DIR = Path(__file__).resolve().parent
SCHEMA_PATH = BASE_DIR / "schema.sql"
SEED_PATH = BASE_DIR / "seed.sql"

app = Flask(__name__)
app.secret_key = "otel_rezervasyon_gizli_anahtar"

DB_SERVER = os.getenv("DB_SERVER", r"localhost\SQLEXPRESS")
DB_NAME = os.getenv("DB_NAME", "OtelRezervasyonDB")
DB_USER = os.getenv("DB_USER", "")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_DRIVER = os.getenv("DB_DRIVER", "ODBC Driver 18 for SQL Server")
DB_TRUST_CERT = os.getenv("DB_TRUST_CERT", "yes")
DB_ENCRYPT = os.getenv("DB_ENCRYPT", "yes")


def build_connection_string():
    if DB_USER and DB_PASSWORD:
        return (
            f"DRIVER={{{DB_DRIVER}}};"
            f"SERVER={DB_SERVER};"
            f"DATABASE={DB_NAME};"
            f"UID={DB_USER};"
            f"PWD={DB_PASSWORD};"
            f"Encrypt={DB_ENCRYPT};"
            f"TrustServerCertificate={DB_TRUST_CERT};"
        )
    return (
        f"DRIVER={{{DB_DRIVER}}};"
        f"SERVER={DB_SERVER};"
        f"DATABASE={DB_NAME};"
        "Trusted_Connection=yes;"
        f"Encrypt={DB_ENCRYPT};"
        f"TrustServerCertificate={DB_TRUST_CERT};"
    )


def get_db():
    if "db" not in g:
        g.db = pyodbc.connect(build_connection_string())
    return g.db


@app.teardown_appcontext
def close_db(_error):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def fetchall_dict(cursor):
    columns = [col[0] for col in cursor.description]
    rows = cursor.fetchall()
    return [dict(zip(columns, row)) for row in rows]


def fetchone_dict(cursor):
    row = cursor.fetchone()
    if row is None:
        return None
    columns = [col[0] for col in cursor.description]
    return dict(zip(columns, row))


def run_sql_script(connection, script_text):
    statements = [s.strip() for s in script_text.split("GO") if s.strip()]
    cursor = connection.cursor()
    for statement in statements:
        cursor.execute(statement)
    connection.commit()


def oda_durumlarini_senkronize_et():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("UPDATE odalar SET durum = 'musait';")
    cursor.execute(
        """
        UPDATE o
        SET o.durum = 'dolu'
        FROM odalar o
        WHERE EXISTS (
            SELECT 1
            FROM rezervasyonlar r
            WHERE r.oda_id = o.oda_id
              AND r.durum IN ('beklemede', 'onaylandi')
        );
        """
    )
    db.commit()


def init_db():
    db = pyodbc.connect(build_connection_string(), autocommit=False)
    schema_sql = SCHEMA_PATH.read_text(encoding="utf-8")
    seed_sql = SEED_PATH.read_text(encoding="utf-8")
    run_sql_script(db, schema_sql)
    run_sql_script(db, seed_sql)
    db.close()


def rezervasyon_cakisma_var_mi(oda_id, giris_tarihi, cikis_tarihi):
    db = get_db()
    query = """
        SELECT TOP 1 1 AS var_mi
        FROM rezervasyonlar
        WHERE oda_id = ?
          AND durum IN ('beklemede', 'onaylandi')
          AND (giris_tarihi < ? AND cikis_tarihi > ?)
    """
    row = db.cursor().execute(query, (oda_id, cikis_tarihi, giris_tarihi)).fetchone()
    return row is not None


@app.route("/")
def anasayfa():
    oda_durumlarini_senkronize_et()
    db = get_db()
    cursor = db.cursor().execute(
        """
        SELECT o.oda_id, o.oda_no, o.durum, t.tip_adi, t.kapasite, t.gecelik_fiyat
        FROM odalar o
        JOIN oda_tipleri t ON t.tip_id = o.tip_id
        ORDER BY o.oda_no;
        """
    )
    odalar = fetchall_dict(cursor)
    return render_template("index.html", odalar=odalar)


@app.route("/rezervasyon/yeni", methods=["GET", "POST"])
def rezervasyon_yeni():
    oda_durumlarini_senkronize_et()
    db = get_db()
    cursor = db.cursor().execute(
        """
        SELECT o.oda_id, o.oda_no, t.tip_adi, t.kapasite, t.gecelik_fiyat
        FROM odalar o
        JOIN oda_tipleri t ON t.tip_id = o.tip_id
        WHERE o.durum IN ('musait', 'dolu')
        ORDER BY o.oda_no;
        """
    )
    odalar = fetchall_dict(cursor)

    if request.method == "POST":
        ad = request.form.get("ad", "").strip()
        soyad = request.form.get("soyad", "").strip()
        telefon = request.form.get("telefon", "").strip()
        email = request.form.get("email", "").strip() or None
        oda_id = request.form.get("oda_id", "").strip()
        giris_tarihi = request.form.get("giris_tarihi", "").strip()
        cikis_tarihi = request.form.get("cikis_tarihi", "").strip()

        if not all([ad, soyad, telefon, oda_id, giris_tarihi, cikis_tarihi]):
            flash("Lutfen zorunlu tum alanlari doldurun.", "hata")
            return render_template("reservation_form.html", odalar=odalar)

        try:
            oda_id_int = int(oda_id)
            giris = datetime.strptime(giris_tarihi, "%Y-%m-%d").date()
            cikis = datetime.strptime(cikis_tarihi, "%Y-%m-%d").date()
        except ValueError:
            flash("Tarih veya oda bilgisi hatali.", "hata")
            return render_template("reservation_form.html", odalar=odalar)

        if giris >= cikis:
            flash("Cikis tarihi giris tarihinden sonra olmalidir.", "hata")
            return render_template("reservation_form.html", odalar=odalar)

        if rezervasyon_cakisma_var_mi(oda_id_int, giris_tarihi, cikis_tarihi):
            flash("Secilen oda bu tarih araliginda musait degil.", "hata")
            return render_template("reservation_form.html", odalar=odalar)

        oda_cursor = db.cursor().execute(
            """
            SELECT t.gecelik_fiyat
            FROM odalar o
            JOIN oda_tipleri t ON t.tip_id = o.tip_id
            WHERE o.oda_id = ?;
            """,
            (oda_id_int,),
        )
        oda = fetchone_dict(oda_cursor)

        if oda is None:
            flash("Oda bulunamadi.", "hata")
            return render_template("reservation_form.html", odalar=odalar)

        gece_sayisi = (cikis - giris).days
        toplam_ucret = float(oda["gecelik_fiyat"]) * gece_sayisi

        cursor = db.cursor()
        misafir_row = cursor.execute(
            """
            INSERT INTO misafirler (ad, soyad, telefon, email)
            OUTPUT INSERTED.misafir_id
            VALUES (?, ?, ?, ?);
            """,
            (ad, soyad, telefon, email),
        ).fetchone()
        misafir_id = misafir_row[0] if misafir_row else None
        if misafir_id is None:
            db.rollback()
            flash("Misafir kaydi olusturulamadi. Lutfen tekrar deneyin.", "hata")
            return render_template("reservation_form.html", odalar=odalar)

        cursor.execute(
            """
            INSERT INTO rezervasyonlar
            (misafir_id, oda_id, giris_tarihi, cikis_tarihi, durum, toplam_ucret)
            VALUES (?, ?, ?, ?, 'onaylandi', ?);
            """,
            (misafir_id, oda_id_int, giris_tarihi, cikis_tarihi, toplam_ucret),
        )

        cursor.execute("UPDATE odalar SET durum = 'dolu' WHERE oda_id = ?;", (oda_id_int,))
        db.commit()

        flash("Rezervasyon basariyla olusturuldu.", "basari")
        return redirect(url_for("rezervasyonlar_listesi"))

    return render_template("reservation_form.html", odalar=odalar)


@app.route("/rezervasyonlar")
def rezervasyonlar_listesi():
    db = get_db()
    cursor = db.cursor().execute(
        """
        SELECT r.rezervasyon_id, r.giris_tarihi, r.cikis_tarihi, r.durum, r.toplam_ucret,
               m.ad, m.soyad, m.telefon, m.email,
               o.oda_no, t.tip_adi
        FROM rezervasyonlar r
        JOIN misafirler m ON m.misafir_id = r.misafir_id
        JOIN odalar o ON o.oda_id = r.oda_id
        JOIN oda_tipleri t ON t.tip_id = o.tip_id
        ORDER BY r.rezervasyon_id DESC;
        """
    )
    rezervasyonlar = fetchall_dict(cursor)
    return render_template("reservations.html", rezervasyonlar=rezervasyonlar)


@app.route("/init-db", methods=["POST"])
def init_db_route():
    init_db()
    flash("Veritabani tablolari olusturuldu ve ornek veriler eklendi.", "basari")
    return redirect(url_for("anasayfa"))


if __name__ == "__main__":
    app.run(debug=True)
