# 🛒 Project Ecommerce KahtaCards

Project ini adalah aplikasi web e-commerce berbasis **Django** yang menyediakan fitur seperti autentikasi user (login & register) serta katalog produk.

---

## Cara Menjalankan Project (First Setup)

### 1. Clone Repository

```bash
git clone https://github.com/andri-oss/Project-Ecommerce-KahtaCards.git
cd Project-Ecommerce-KahtaCards
```

---

### 2. Buat Virtual Environment

```bash
python -m venv venv
```

Aktifkan virtual environment:

* Windows:

```bash
venv\Scripts\activate
```

* Linux / Mac:

```bash
source venv/bin/activate
```

---

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```



---

### 4. Migrasi Database

```bash
python manage.py migrate
```

---

### 5. Buat Superuser (Opsional)

```bash
python manage.py createsuperuser
```

---

### 6. Jalankan Server

```bash
python manage.py runserver
```

Buka di browser:

```
http://127.0.0.1:8000/
```
