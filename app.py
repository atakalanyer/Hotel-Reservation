import os
import smtplib
import ssl
from datetime import datetime
from email.message import EmailMessage
from pathlib import Path

import pyodbc
from dotenv import load_dotenv
from flask import Flask, flash, g, redirect, render_template, request, session, url_for


BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

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
# SMTP sunucu adresi (ornek: Gmail icin smtp.gmail.com); e-posta adresi degil.
MAIL_SERVER = os.getenv("MAIL_SERVER", "smtp.gmail.com")
MAIL_PORT = int(os.getenv("MAIL_PORT", "587"))
MAIL_USERNAME = (os.getenv("MAIL_USERNAME") or "").strip()
# Gmail uygulama sifreleri ekranda "xxxx xxxx ..." diye gorunur; SMTP bosluksuz ister.
MAIL_PASSWORD = "".join((os.getenv("MAIL_PASSWORD") or "").split())
MAIL_USE_TLS = os.getenv("MAIL_USE_TLS", "yes").lower() == "yes"


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


_OTEL_GORSEL_VARSAYILAN = {
    1: "img/oteller/bogaz.svg",
    2: "img/oteller/kapadokya.svg",
    3: "img/oteller/ege.svg",
    4: "img/oteller/ankara.svg",
}

# Yeni kurulum / bos DB satirlari: jw=Istanbul goruntu dosyasi, images=Ege goruntusu, mavi=Ankara goruntusu (yer degistirmis atama)
_OTEL_GORSEL_DOSYA_VARSAYILAN = {
    1: "img/oteller/images.jpg",
    2: "img/oteller/terrace.jpg",
    3: "img/oteller/mavi-ege-butik-otel.jpg",
    4: "img/oteller/jw-marriott-ankara-ankara-one-cikan-resim-76532480.jpg",
}


def diskten_otel_gorseli_eslesmeleri():
    """
    Dosya adlarina gore once "hangi sehrin goruntusu" oldugunu bulur, sonra otellere yer degistirerek atar:
    Istanbul goruntusu (jw*) -> Ankara oteli (4), Ege goruntusu (ege* / images.jpg) -> Istanbul/Bogaz (1),
    Ankara goruntusu (mavi*) -> Ege oteli (3), terrace* -> Kapadokya (2).
    """
    uzantilar = {".jpg", ".jpeg", ".png", ".webp"}
    dosyalar = []
    for klas, url_on in (
        (BASE_DIR / "static" / "images", "images"),
        (BASE_DIR / "static" / "img" / "oteller", "img/oteller"),
    ):
        if not klas.is_dir():
            continue
        for yol in sorted(klas.iterdir()):
            if yol.is_file() and yol.suffix.lower() in uzantilar:
                dosyalar.append((f"{url_on}/{yol.name}", yol.name.lower()))

    def ilk(kosul):
        for rel, low in dosyalar:
            if kosul(low):
                return rel
        return None

    gor_istanbul = ilk(lambda n: n.startswith("jw"))
    gor_terrace = ilk(lambda n: n.startswith("terrace"))
    gor_ankara = ilk(lambda n: n.startswith("mavi"))
    gor_ege = ilk(lambda n: n.startswith("ege")) or ilk(lambda n: n == "images.jpg")

    sonuc = {}
    if gor_terrace:
        sonuc[2] = gor_terrace
    if gor_ege:
        sonuc[1] = gor_ege
    if gor_ankara:
        sonuc[3] = gor_ankara
    if gor_istanbul:
        sonuc[4] = gor_istanbul
    return sonuc


def ensure_oteller_gorsel_sutunu():
    """Eski veritabanlarinda gorsel_yolu sutununu ve bos kayitlari doldurur."""
    db = get_db()
    cur = db.cursor()
    cur.execute(
        """
        IF COL_LENGTH('dbo.oteller', 'gorsel_yolu') IS NULL
            ALTER TABLE dbo.oteller ADD gorsel_yolu NVARCHAR(260) NULL;
        """
    )
    db.commit()
    cur.execute(
        """
        UPDATE o
        SET o.gorsel_yolu = CASE o.otel_id
            WHEN 1 THEN N'img/oteller/images.jpg'
            WHEN 2 THEN N'img/oteller/terrace.jpg'
            WHEN 3 THEN N'img/oteller/mavi-ege-butik-otel.jpg'
            WHEN 4 THEN N'img/oteller/jw-marriott-ankara-ankara-one-cikan-resim-76532480.jpg'
            ELSE N'img/oteller/default.svg'
        END
        FROM dbo.oteller o
        WHERE o.gorsel_yolu IS NULL OR RTRIM(CAST(o.gorsel_yolu AS NVARCHAR(260))) = N'';
        """
    )
    db.commit()


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


def aktif_kullanici():
    return {
        "kullanici_id": session.get("kullanici_id"),
        "kullanici_adi": session.get("kullanici_adi"),
        "rol": session.get("rol"),
        "ad_soyad": session.get("ad_soyad"),
    }


def giris_gerekli():
    if not session.get("kullanici_id"):
        flash("Bu islem icin once giris yapmalisiniz.", "hata")
        return False
    return True


def admin_gerekli():
    if not giris_gerekli():
        return False
    if session.get("rol") != "admin":
        flash("Bu sayfaya sadece admin erisebilir.", "hata")
        return False
    return True


def veritabani_hazir_mi():
    if "db_hazir" in g:
        return g.db_hazir

    db = get_db()
    gerekli_tablolar = {"oteller", "kullanicilar", "oda_tipleri", "odalar", "misafirler", "rezervasyonlar"}
    cursor = db.cursor().execute(
        """
        SELECT TABLE_NAME
        FROM INFORMATION_SCHEMA.TABLES
        WHERE TABLE_TYPE = 'BASE TABLE';
        """
    )
    mevcut = {str(row[0]).lower() for row in cursor.fetchall()}
    g.db_hazir = gerekli_tablolar.issubset(mevcut)
    return g.db_hazir


def kurulum_gerekli_sayfasi():
    return render_template("setup_required.html"), 503


def rezervasyon_maili_gonder(alici_email, misafir_adi_soyadi, otel_adi, oda_no, giris_tarihi, cikis_tarihi, toplam_ucret):
    if not alici_email:
        return False, "E-posta adresi verilmedi."
    if not MAIL_USERNAME or not MAIL_PASSWORD:
        return False, (
            "Mail ayarlari eksik. Proje klasorundeki .env dosyasina MAIL_USERNAME ve "
            "MAIL_PASSWORD yazin (ornek icin .env.example dosyasina bakin) veya bu "
            "degiskenleri ortamda tanimlayin."
        )

    message = EmailMessage()
    message["Subject"] = "Rezervasyon Onayi"
    message["From"] = MAIL_USERNAME
    message["To"] = alici_email
    message.set_content(
        (
            f"Merhaba {misafir_adi_soyadi},\n\n"
            "Rezervasyonunuz basariyla olusturuldu.\n\n"
            f"Otel: {otel_adi}\n"
            f"Oda No: {oda_no}\n"
            f"Giris Tarihi: {giris_tarihi}\n"
            f"Cikis Tarihi: {cikis_tarihi}\n"
            f"Toplam Ucret: {toplam_ucret:.2f} TL\n\n"
            "Bizi tercih ettiginiz icin tesekkur ederiz."
        )
    )

    try:
        context = ssl.create_default_context()
        with smtplib.SMTP(MAIL_SERVER, MAIL_PORT, timeout=20) as server:
            if MAIL_USE_TLS:
                server.starttls(context=context)
            server.login(MAIL_USERNAME, MAIL_PASSWORD)
            server.send_message(message)
        return True, ""
    except smtplib.SMTPAuthenticationError as exc:
        return False, (
            "SMTP girisi basarisiz. Gmail kullaniyorsaniz Google Hesabi > Guvenlik "
            "bolumunden 2FA acikken 'Uygulama sifresi' olusturup MAIL_PASSWORD olarak "
            "verin (normal Gmail sifresi genelde calismaz). Teknik detay: "
            + str(exc)
        )
    except OSError as exc:
        return False, (
            f"SMTP sunucusuna baglanilamadi ({MAIL_SERVER}:{MAIL_PORT}). "
            "MAIL_SERVER ve MAIL_PORT degerlerini kontrol edin. Detay: "
            + str(exc)
        )
    except Exception as exc:
        return False, str(exc)


@app.route("/")
def anasayfa():
    if not veritabani_hazir_mi():
        return kurulum_gerekli_sayfasi()

    ensure_oteller_gorsel_sutunu()
    oda_durumlarini_senkronize_et()
    db = get_db()
    cursor = db.cursor().execute(
        """
        SELECT o.oda_id, o.oda_no, o.durum, t.tip_adi, t.kapasite, t.gecelik_fiyat,
               h.otel_id, h.otel_adi, h.sehir, h.gorsel_yolu
        FROM odalar o
        JOIN oteller h ON h.otel_id = o.otel_id
        JOIN oda_tipleri t ON t.tip_id = o.tip_id
        ORDER BY h.otel_id, o.oda_no;
        """
    )
    odalar = fetchall_dict(cursor)
    disk_gorsel = diskten_otel_gorseli_eslesmeleri()
    oteller = {}
    for oda in odalar:
        otel_id = oda["otel_id"]
        if otel_id not in oteller:
            gy = disk_gorsel.get(otel_id) or (oda.get("gorsel_yolu") or "").strip()
            if not gy:
                gy = _OTEL_GORSEL_DOSYA_VARSAYILAN.get(otel_id) or _OTEL_GORSEL_VARSAYILAN.get(
                    otel_id, "img/oteller/default.svg"
                )
            oteller[otel_id] = {
                "otel_id": otel_id,
                "otel_adi": oda["otel_adi"],
                "sehir": oda["sehir"],
                "gorsel_yolu": gy,
                "odalar": [],
            }
        oteller[otel_id]["odalar"].append(oda)

    return render_template("index.html", oteller=list(oteller.values()))


@app.route("/hakkimizda")
def hakkimizda():
    return render_template("about.html")


@app.route("/iletisim")
def iletisim():
    return render_template("contact.html")


@app.route("/giris", methods=["GET", "POST"])
def giris():
    if not veritabani_hazir_mi():
        return kurulum_gerekli_sayfasi()

    if request.method == "POST":
        kullanici_adi = request.form.get("kullanici_adi", "").strip()
        sifre = request.form.get("sifre", "").strip()
        if not kullanici_adi or not sifre:
            flash("Kullanici adi ve sifre zorunludur.", "hata")
            return render_template("login.html")

        db = get_db()
        cursor = db.cursor().execute(
            """
            SELECT kullanici_id, kullanici_adi, rol, ad_soyad
            FROM kullanicilar
            WHERE kullanici_adi = ? AND sifre = ?;
            """,
            (kullanici_adi, sifre),
        )
        kullanici = fetchone_dict(cursor)
        if kullanici is None:
            flash("Kullanici adi veya sifre hatali.", "hata")
            return render_template("login.html")

        session["kullanici_id"] = kullanici["kullanici_id"]
        session["kullanici_adi"] = kullanici["kullanici_adi"]
        session["rol"] = kullanici["rol"]
        session["ad_soyad"] = kullanici["ad_soyad"]

        flash("Giris basarili.", "basari")
        return redirect(url_for("anasayfa"))
    return render_template("login.html")


@app.route("/cikis")
def cikis():
    session.clear()
    flash("Cikis yapildi.", "basari")
    return redirect(url_for("anasayfa"))


@app.route("/rezervasyon/yeni")
def rezervasyon_yeni_yonlendir():
    if not giris_gerekli():
        return redirect(url_for("giris"))
    return redirect(url_for("anasayfa"))


@app.route("/otel/<int:otel_id>/rezervasyon/yeni", methods=["GET", "POST"])
def rezervasyon_yeni(otel_id):
    if not veritabani_hazir_mi():
        return kurulum_gerekli_sayfasi()

    if not giris_gerekli():
        return redirect(url_for("giris"))

    oda_durumlarini_senkronize_et()
    db = get_db()
    otel_cursor = db.cursor().execute(
        "SELECT otel_id, otel_adi, sehir FROM oteller WHERE otel_id = ?;",
        (otel_id,),
    )
    otel = fetchone_dict(otel_cursor)
    if otel is None:
        flash("Otel bulunamadi.", "hata")
        return redirect(url_for("anasayfa"))

    cursor = db.cursor().execute(
        """
        SELECT o.oda_id, o.oda_no, t.tip_adi, t.kapasite, t.gecelik_fiyat
        FROM odalar o
        JOIN oda_tipleri t ON t.tip_id = o.tip_id
        WHERE o.otel_id = ?
          AND o.durum IN ('musait', 'dolu')
        ORDER BY o.oda_no;
        """,
        (otel_id,),
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
            return render_template("reservation_form.html", odalar=odalar, otel=otel)

        try:
            oda_id_int = int(oda_id)
            giris = datetime.strptime(giris_tarihi, "%Y-%m-%d").date()
            cikis = datetime.strptime(cikis_tarihi, "%Y-%m-%d").date()
        except ValueError:
            flash("Tarih veya oda bilgisi hatali.", "hata")
            return render_template("reservation_form.html", odalar=odalar, otel=otel)

        if giris >= cikis:
            flash("Cikis tarihi giris tarihinden sonra olmalidir.", "hata")
            return render_template("reservation_form.html", odalar=odalar, otel=otel)

        if rezervasyon_cakisma_var_mi(oda_id_int, giris_tarihi, cikis_tarihi):
            flash("Secilen oda bu tarih araliginda musait degil.", "hata")
            return render_template("reservation_form.html", odalar=odalar, otel=otel)

        oda_cursor = db.cursor().execute(
            """
            SELECT o.oda_no, t.tip_adi, t.gecelik_fiyat
            FROM odalar o
            JOIN oda_tipleri t ON t.tip_id = o.tip_id
            WHERE o.oda_id = ? AND o.otel_id = ?;
            """,
            (oda_id_int, otel_id),
        )
        oda = fetchone_dict(oda_cursor)

        if oda is None:
            flash("Oda bulunamadi.", "hata")
            return render_template("reservation_form.html", odalar=odalar, otel=otel)

        gece_sayisi = (cikis - giris).days
        toplam_ucret = float(oda["gecelik_fiyat"]) * gece_sayisi

        cursor = db.cursor()
        misafir_id = None
        if email:
            varolan = cursor.execute(
                "SELECT misafir_id FROM misafirler WHERE email = ?;",
                (email,),
            ).fetchone()
            if varolan:
                misafir_id = varolan[0]
                cursor.execute(
                    """
                    UPDATE misafirler
                    SET ad = ?, soyad = ?, telefon = ?
                    WHERE misafir_id = ?;
                    """,
                    (ad, soyad, telefon, misafir_id),
                )
        if misafir_id is None:
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
            return render_template("reservation_form.html", odalar=odalar, otel=otel)

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
        mail_ok, mail_hata = rezervasyon_maili_gonder(
            alici_email=email,
            misafir_adi_soyadi=f"{ad} {soyad}",
            otel_adi=otel["otel_adi"],
            oda_no=oda["oda_no"],
            giris_tarihi=giris_tarihi,
            cikis_tarihi=cikis_tarihi,
            toplam_ucret=toplam_ucret,
        )
        if email and mail_ok:
            flash("Bilgilendirme e-postasi gonderildi.", "basari")
        elif email:
            flash(f"E-posta gonderilemedi: {mail_hata}", "hata")

        return redirect(url_for("rezervasyonlar_listesi"))

    return render_template("reservation_form.html", odalar=odalar, otel=otel)


@app.route("/rezervasyonlar")
def rezervasyonlar_listesi():
    if not veritabani_hazir_mi():
        return kurulum_gerekli_sayfasi()

    if not admin_gerekli():
        return redirect(url_for("anasayfa"))

    db = get_db()
    cursor = db.cursor().execute(
        """
        SELECT r.rezervasyon_id, r.giris_tarihi, r.cikis_tarihi, r.durum, r.toplam_ucret,
               m.ad, m.soyad, m.telefon, m.email,
               h.otel_adi, o.oda_no, t.tip_adi
        FROM rezervasyonlar r
        JOIN misafirler m ON m.misafir_id = r.misafir_id
        JOIN odalar o ON o.oda_id = r.oda_id
        JOIN oteller h ON h.otel_id = o.otel_id
        JOIN oda_tipleri t ON t.tip_id = o.tip_id
        ORDER BY r.rezervasyon_id DESC;
        """
    )
    rezervasyonlar = fetchall_dict(cursor)
    return render_template("reservations.html", rezervasyonlar=rezervasyonlar)


@app.route("/admin/rezervasyon/<int:rezervasyon_id>/sil", methods=["POST"])
def rezervasyon_sil(rezervasyon_id):
    if not veritabani_hazir_mi():
        return kurulum_gerekli_sayfasi()
    if not admin_gerekli():
        return redirect(url_for("anasayfa"))

    db = get_db()
    cursor = db.cursor()
    kayit = fetchone_dict(
        cursor.execute(
            """
            SELECT rezervasyon_id
            FROM rezervasyonlar
            WHERE rezervasyon_id = ?;
            """,
            (rezervasyon_id,),
        )
    )
    if kayit is None:
        flash("Silinecek rezervasyon bulunamadi.", "hata")
        return redirect(url_for("rezervasyonlar_listesi"))

    cursor.execute(
        "DELETE FROM rezervasyonlar WHERE rezervasyon_id = ?;",
        (rezervasyon_id,),
    )
    db.commit()
    oda_durumlarini_senkronize_et()
    flash("Rezervasyon kaydi silindi.", "basari")
    return redirect(url_for("rezervasyonlar_listesi"))


@app.route("/init-db", methods=["POST"])
def init_db_route():
    init_db()
    flash("Veritabani tablolari olusturuldu ve ornek veriler eklendi.", "basari")
    return redirect(url_for("anasayfa"))


@app.context_processor
def ortak_sablon_degeleri():
    return {"aktif_kullanici": aktif_kullanici()}


if __name__ == "__main__":
    app.run(debug=True)
