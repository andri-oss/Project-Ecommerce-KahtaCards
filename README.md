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

### 4. Setup Environment

Buat file `.env` di root project:

```env
SECRET_KEY=django-insecure-your-secret-key
DEBUG=True
```

---

### 5. Migrasi Database

```bash
python manage.py migrate
```

---

### 6. Buat Superuser (Opsional)

```bash
python manage.py createsuperuser
```

---

### 7. Jalankan Server

```bash
python manage.py runserver
```

Buka di browser:

```
http://127.0.0.1:8000/
```
