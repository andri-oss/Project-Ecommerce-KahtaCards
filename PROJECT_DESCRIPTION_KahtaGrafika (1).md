# PROJECT DESCRIPTION
# E-Commerce Custom Packaging — Kahta Grafika
> Dokumen ini adalah referensi utama tim developer dan konteks untuk AI-assisted coding.  
> Versi: 1.0 | Tahun: 2026 | Metodologi: Scrum

---

## 1. GAMBARAN UMUM PROJECT

**Kahta Grafika** adalah platform e-commerce berbasis web untuk usaha percetakan kemasan custom. Pelanggan dapat memesan produk percetakan (box, amplop, kertas, dan sejenisnya) dengan desain custom yang mereka upload sendiri, lalu memilih metode pengiriman dan membayar secara online.

| Atribut | Detail |
|---|---|
| **Nama Sistem** | E-Commerce Percetakan Packaging – Kahta Grafika |
| **Tipe Aplikasi** | Web-based (Server-Side Rendering) |
| **Framework Backend** | Django (Python) |
| **Database** | SQLite (development) → PostgreSQL (production) |
| **Frontend Approach** | Django Templates (SSR) + Tailwind CSS / Bootstrap |
| **Payment Gateway** | Midtrans |
| **Metodologi** | Scrum |
| **Ukuran Tim** | 3–4 developer |

---

## 2. AKTOR & PERAN SISTEM

### 👤 User (Pelanggan)
Pengguna publik yang mendaftar dan melakukan transaksi pembelian produk percetakan custom.

### 🛠️ Admin (Pengelola Toko)
Staf internal Kahta Grafika yang mengelola produk, memproses pesanan, dan memantau transaksi via dashboard admin.

### ⚙️ System (Auto Process)
Proses otomatis yang berjalan di background, khususnya untuk pembatalan pesanan yang belum dibayar setelah 1 jam (menggunakan Celery + Redis, atau Django management command + cron job).

---

## 3. FITUR & REQUIREMENTS

### 3.1 Functional Requirements (Final — Revisi)

| Req ID | Deskripsi | Aktor | Priority | Risk |
|---|---|---|---|---|
| Req 001 | Pengguna memiliki akun untuk mengakses sistem | User/Admin | Critical (Rank 1) | Low |
| Req 002 | User dapat melakukan registrasi dan login ke sistem | User | Critical (Rank 1) | Low |
| Req 003 | User dapat melihat katalog daftar produk percetakan | User | Critical (Rank 1) | Low |
| Req 004 | User dapat melihat detail produk beserta spesifikasi dan harga | User | Critical (Rank 1) | Low |
| Req 005 | User dapat menambahkan produk ke keranjang belanja | User | Critical (Rank 1) | Low |
| Req 006 | User dapat mengupload desain custom dan memberikan catatan pada produk | User | Critical (Rank 2) | Medium |
| Req 007 | User dapat melakukan checkout dari keranjang belanja | User | Critical (Rank 1) | Low |
| Req 008 | User dapat memilih metode pengiriman (delivery ke alamat / pickup di toko) | User | Critical (Rank 1) | Low |
| Req 009 | User wajib mengisi alamat pengiriman jika memilih metode delivery | User | Critical (Rank 1) | Low |
| Req 010 | User dapat melakukan pembayaran online melalui Payment Gateway | User | Critical (Rank 2) | Medium |
| Req 011 | Sistem otomatis membatalkan pesanan yang belum dibayar dalam 1 jam | System | Critical (Rank 2) | Medium |
| Req 012 | User dapat melihat status dan tracking pesanan secara real-time | User | Important (Rank 1) | Low |
| Req 013 | User dapat melihat riwayat transaksi pesanan | User | Important (Rank 3) | Low |
| Req 014 | User dapat mengelola dan memperbarui data profil akun | User | Useful (Rank 3) | Low |
| Req 015 | Admin dapat mengelola katalog produk (tambah, edit, hapus) | Admin | Critical (Rank 1) | Low |
| Req 016 | Admin dapat memproses pesanan dan mengupdate status pengerjaan | Admin | Critical (Rank 1) | Low |
| Req 017 | Admin dapat mengakses laporan transaksi dan data pelanggan | Admin | Important (Rank 3) | Low |

> **Catatan Rank:**  
> **Rank 1** = Mandatory, All Feasible, Low Risk → dikerjakan Sprint pertama  
> **Rank 2** = Mandatory, Feasible, Medium/High Risk → dikerjakan Sprint kedua  
> **Rank 3** = Desirable, All Feasible → dikerjakan Sprint ketiga atau backlog

---

### 3.2 Non-Functional Requirements

**Usability**
- Dapat digunakan oleh pelanggan umum dan admin toko tanpa pelatihan teknis
- Antarmuka responsif dan intuitif (desktop & mobile browser)

**Reliability**
- Ketersediaan layanan tinggi (target ≥ 95% uptime)
- Data transaksi dan pesanan tersimpan akurat dan konsisten

**Performance**
- Response time < 3 detik untuk halaman utama
- Mampu menangani concurrent users (optimasi query, pagination)

**Supportability**
- Kode modular sehingga mudah dikembangkan oleh tim bergantian
- Mudah di-debug dan diperbaiki saat ada bug

---

### 3.3 Batasan Sistem (Inverse Requirements — OUT OF SCOPE)

Fitur berikut **TIDAK** akan dikembangkan dalam project ini:

- ❌ Editor/tool desain grafis online (Canva-like)
- ❌ Layanan pengiriman ekspres milik sendiri
- ❌ Live chat real-time antara pelanggan dan desainer

---

## 4. ARSITEKTUR MODULAR (Django Apps)

Proyek dibagi menjadi Django apps yang independen agar dapat dikerjakan paralel oleh tim:

```
kahta_grafika/              ← Django Project Root
│
├── config/                 ← Settings, URLs utama, WSGI/ASGI
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── apps/
│   ├── accounts/           ← [MODULE 1] Autentikasi & Profil User
│   ├── catalog/            ← [MODULE 2] Katalog & Detail Produk
│   ├── cart/               ← [MODULE 3] Keranjang Belanja
│   ├── orders/             ← [MODULE 4] Checkout, Pesanan & Tracking
│   ├── payments/           ← [MODULE 5] Integrasi Payment Gateway (Midtrans)
│   └── dashboard/          ← [MODULE 6] Admin Dashboard
│
├── templates/              ← HTML templates (per app)
├── static/                 ← CSS, JS, images
├── media/                  ← File upload desain pelanggan
└── manage.py
```

---

## 5. DETAIL SETIAP MODUL

### MODULE 1 — `accounts` (Autentikasi & Profil)
**Tanggung jawab:** Registrasi, login, logout, dan manajemen profil pengguna.

**Models:**
- `UserProfile` — extends Django `AbstractUser` atau one-to-one dengan `User`
  - `phone_number`, `address`, `created_at`

**Views & URLs:**
- `GET/POST /auth/register/` — halaman & proses registrasi
- `GET/POST /auth/login/` — halaman & proses login
- `POST /auth/logout/` — proses logout
- `GET/POST /profile/` — lihat & edit profil (login required)

**Templates:**
- `accounts/register.html`
- `accounts/login.html`
- `accounts/profile.html`

**Catatan:** Gunakan `django.contrib.auth` sebagai base. Tambahkan middleware `login_required` untuk halaman yang butuh autentikasi.

---

### MODULE 2 — `catalog` (Katalog & Produk)
**Tanggung jawab:** Menampilkan daftar produk dan detail produk percetakan.

**Models:**
- `Category` — kategori produk (box, amplop, kertas, dll.)
  - `name`, `slug`, `description`, `image`
- `Product` — produk percetakan
  - `name`, `slug`, `category (FK)`, `description`, `material_spec`, `price`, `min_order`, `image`, `is_active`

**Views & URLs:**
- `GET /catalog/` — daftar semua produk + filter kategori
- `GET /catalog/<slug>/` — detail produk

**Templates:**
- `catalog/product_list.html`
- `catalog/product_detail.html`

**Catatan:** Implementasikan pagination dan filter kategori. Produk harus bisa dikelola dari admin panel Django default maupun custom dashboard.

---

### MODULE 3 — `cart` (Keranjang Belanja)
**Tanggung jawab:** Mengelola keranjang belanja, upload desain custom, dan catatan produk.

**Models:**
- `Cart` — keranjang milik satu user (atau session untuk guest)
  - `user (FK, nullable)`, `session_key`, `created_at`
- `CartItem` — item dalam keranjang
  - `cart (FK)`, `product (FK)`, `quantity`, `custom_design (FileField)`, `notes`, `added_at`

**Views & URLs:**
- `GET /cart/` — lihat isi keranjang
- `POST /cart/add/<product_id>/` — tambah produk
- `POST /cart/update/<item_id>/` — update quantity/catatan
- `POST /cart/remove/<item_id>/` — hapus item
- `POST /cart/upload-design/<item_id>/` — upload file desain

**Templates:**
- `cart/cart_detail.html`

**Catatan:**  
- File desain custom disimpan di `media/designs/` dengan format: `designs/<user_id>/<filename>`
- Validasi tipe file: PDF, PNG, JPG, AI, CDR (sesuaikan dengan kebutuhan percetakan)
- Batasi ukuran file upload (setting `MAX_UPLOAD_SIZE` di settings.py)

---

### MODULE 4 — `orders` (Pesanan, Checkout & Tracking)
**Tanggung jawab:** Proses checkout, manajemen pesanan, status tracking, riwayat transaksi.

**Models:**
- `Order` — pesanan
  - `order_number (unique)`, `user (FK)`, `status`, `shipping_method`, `shipping_address`, `total_price`, `created_at`, `updated_at`
  - **Status choices:** `PENDING_PAYMENT`, `PAID`, `PROCESSING`, `SHIPPED`, `COMPLETED`, `CANCELLED`
  - **Shipping method:** `DELIVERY`, `PICKUP`
- `OrderItem` — item dalam pesanan
  - `order (FK)`, `product (FK)`, `quantity`, `price_at_purchase`, `custom_design`, `notes`
- `ShippingAddress` — alamat pengiriman
  - `order (FK)`, `recipient_name`, `phone`, `address_line`, `city`, `province`, `postal_code`

**Views & URLs:**
- `GET/POST /checkout/` — halaman checkout (pilih shipping, isi alamat)
- `GET /orders/` — riwayat pesanan user
- `GET /orders/<order_number>/` — detail & tracking pesanan
- `POST /orders/<order_number>/cancel/` — batalkan pesanan (jika masih PENDING)

**Templates:**
- `orders/checkout.html`
- `orders/order_list.html`
- `orders/order_detail.html`

**Auto-Cancel Logic:**
```python
# Jalankan sebagai management command atau Celery beat task
# Cek setiap N menit: pesanan PENDING_PAYMENT > 1 jam → ubah status ke CANCELLED
Order.objects.filter(
    status='PENDING_PAYMENT',
    created_at__lt=timezone.now() - timedelta(hours=1)
).update(status='CANCELLED')
```
Untuk MVP, bisa pakai `django-apscheduler` atau `management command` + cron. Untuk skala lebih besar, gunakan Celery + Redis.

---

### MODULE 5 — `payments` (Payment Gateway)
**Tanggung jawab:** Integrasi dengan Midtrans untuk pembayaran online.

**Models:**
- `Payment` — record transaksi pembayaran
  - `order (OneToOne FK)`, `midtrans_order_id`, `payment_method`, `amount`, `status`, `snap_token`, `created_at`, `paid_at`
  - **Status:** `PENDING`, `SUCCESS`, `FAILED`, `EXPIRED`

**Views & URLs:**
- `POST /payments/create/<order_number>/` — buat Snap token Midtrans
- `GET /payments/success/` — halaman sukses pembayaran
- `GET /payments/failed/` — halaman gagal pembayaran
- `POST /payments/notification/` — webhook/callback dari Midtrans (CSRF exempt)

**Catatan:**
- Gunakan library `midtransclient` (pip install midtransclient)
- `SERVER_KEY` dan `CLIENT_KEY` Midtrans disimpan di `.env` (jangan hardcode)
- Webhook endpoint harus `@csrf_exempt` dan validasi signature key dari Midtrans
- Setelah pembayaran sukses → update `Order.status` ke `PAID`

---

### MODULE 6 — `dashboard` (Admin Panel Custom)
**Tanggung jawab:** Dashboard khusus admin untuk mengelola produk, pesanan, dan melihat laporan.

**Views & URLs (semua `staff_required`):**
- `GET /dashboard/` — ringkasan: pesanan baru, revenue hari ini
- `GET/POST /dashboard/products/` — daftar & tambah produk
- `GET/POST /dashboard/products/<id>/edit/` — edit produk
- `POST /dashboard/products/<id>/delete/` — hapus produk
- `GET /dashboard/orders/` — daftar semua pesanan masuk
- `GET /dashboard/orders/<order_number>/` — detail pesanan + file desain
- `POST /dashboard/orders/<order_number>/update-status/` — update status pesanan
- `GET /dashboard/customers/` — daftar pelanggan terdaftar
- `GET /dashboard/reports/` — laporan transaksi (filter by tanggal)

**Templates:**
- `dashboard/index.html`
- `dashboard/product_list.html`, `dashboard/product_form.html`
- `dashboard/order_list.html`, `dashboard/order_detail.html`
- `dashboard/customer_list.html`
- `dashboard/reports.html`

**Catatan:** Gunakan decorator `@user_passes_test(lambda u: u.is_staff)` untuk semua view dashboard.

---

## 6. DATABASE SCHEMA OVERVIEW

```
User (Django built-in)
 └─ UserProfile (1:1)

Category
 └─ Product (N:1 → Category)

Cart (1:1 → User/session)
 └─ CartItem (N:1 → Cart, N:1 → Product)
      └─ custom_design (file)

Order (N:1 → User)
 ├─ OrderItem (N:1 → Order, N:1 → Product)
 ├─ ShippingAddress (1:1 → Order)
 └─ Payment (1:1 → Order)
```

---

## 7. PEMBAGIAN TUGAS TIM (3–4 Developer)

### Rekomendasi Pembagian Berdasarkan Modul

| Developer | Modul Utama | Modul Pendukung |
|---|---|---|
| **Dev A** | Module 1 (accounts) + Module 6 (dashboard) | Setup project, config, deployment |
| **Dev B** | Module 2 (catalog) + Module 3 (cart) | Static files, base template |
| **Dev C** | Module 4 (orders) + auto-cancel logic | Order flow integration |
| **Dev D** | Module 5 (payments / Midtrans) | Testing, bug fixing |

> Jika tim hanya 3 orang, Dev C dan Dev D digabung, atau Module 6 (dashboard) dikerjakan bersama di Sprint akhir.

---

## 8. SPRINT PLANNING (SCRUM)

### Sprint 1 — Foundation & Core Features (Rank 1)
**Goal:** Sistem dasar berjalan: user bisa browse produk, masuk akun, dan masukkan ke keranjang.

**Backlog Sprint 1:**
- [ ] Setup project Django (config, settings, base template, static files)
- [ ] Module 1: Registrasi, Login, Logout
- [ ] Module 2: Model Category & Product, halaman catalog list & detail
- [ ] Module 3: Model Cart & CartItem, tambah/hapus/update item di keranjang
- [ ] Module 6: Admin bisa tambah/edit/hapus produk (bisa via Django admin default dulu)
- [ ] Module 4: Model Order & OrderItem, halaman checkout dasar, pilih shipping method & input alamat
- [ ] Module 4: Halaman order detail & tracking status

### Sprint 2 — Payments & Critical Business Logic (Rank 2)
**Goal:** Sistem pembayaran berjalan dan pesanan bisa dikelola.

**Backlog Sprint 2:**
- [ ] Module 3: Upload desain custom (file upload) pada CartItem
- [ ] Module 5: Integrasi Midtrans Snap — buat token, redirect ke payment page
- [ ] Module 5: Webhook callback dari Midtrans → update status Order
- [ ] Module 4: Auto-cancel pesanan belum dibayar setelah 1 jam
- [ ] Module 6: Admin dapat melihat pesanan masuk + file desain yang diupload
- [ ] Module 6: Admin dapat update status pesanan

### Sprint 3 — Desirable Features & Polish (Rank 3)
**Goal:** Fitur pelengkap dan penyempurnaan UI/UX.

**Backlog Sprint 3:**
- [ ] Module 3: Fitur catatan/instruksi khusus pada CartItem
- [ ] Module 4: Halaman riwayat transaksi user
- [ ] Module 1: Edit profil user
- [ ] Module 6: Laporan transaksi admin (filter tanggal, export CSV)
- [ ] UI Polish: Responsif mobile, loading state, pesan error yang jelas
- [ ] Testing: Unit test per modul
- [ ] Dokumentasi: README, API docs (jika ada)

---

## 9. KONVENSI KODE TIM

### Penamaan
- **Apps:** snake_case (`accounts`, `catalog`, `orders`)
- **Models:** PascalCase (`OrderItem`, `CartItem`)
- **Views:** snake_case (`product_list`, `checkout_view`)
- **URLs:** kebab-case (`/cart/add-item/`, `/orders/order-detail/`)
- **Template vars:** snake_case (`cart_items`, `order_number`)

### Struktur File Per App
```
apps/
└── catalog/
    ├── __init__.py
    ├── admin.py
    ├── apps.py
    ├── forms.py        ← Django forms
    ├── models.py
    ├── urls.py
    ├── views.py
    └── templates/
        └── catalog/
            ├── product_list.html
            └── product_detail.html
```

### Environment Variables (wajib di `.env`, jangan di-commit)
```env
SECRET_KEY=...
DEBUG=True
DATABASE_URL=sqlite:///db.sqlite3
MIDTRANS_SERVER_KEY=...
MIDTRANS_CLIENT_KEY=...
MIDTRANS_IS_PRODUCTION=False
MEDIA_ROOT=media/
MAX_UPLOAD_SIZE=10485760   # 10MB
```

### Git Branch Strategy
```
main            ← production-ready code
dev             ← integration branch
feature/accounts
feature/catalog
feature/cart
feature/orders
feature/payments
feature/dashboard
```

**Aturan:** Setiap developer bekerja di branch `feature/<modul>`. Merge ke `dev` via Pull Request setelah review. Merge `dev` ke `main` setiap akhir sprint.

---

## 10. SETUP PROJECT (Quick Start)

```bash
# 1. Clone & setup environment
git clone <repo-url>
cd kahta_grafika
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install django pillow python-dotenv midtransclient

# 3. Setup database
python manage.py migrate

# 4. Buat superuser (untuk akses admin)
python manage.py createsuperuser

# 5. Jalankan server
python manage.py runserver
```

### `requirements.txt` (minimal)
```
django>=4.2
pillow>=10.0          # untuk ImageField
python-dotenv>=1.0    # untuk .env
midtransclient>=1.4   # payment gateway
whitenoise>=6.0       # serve static files
```

---

## 11. KONTEKS UNTUK AI CODING ASSISTANT

> Bagian ini khusus sebagai konteks bagi tools seperti GitHub Copilot, Cursor, atau Claude saat membantu vibe coding.

**Stack:** Django 4.x, Python 3.11+, SQLite (dev), Server-Side Rendering (Django Templates), Tailwind CSS / Bootstrap 5.

**Pola yang dipakai:**
- Function-based views (FBV) sebagai default, Class-based views (CBV) bila diperlukan (misal: ListView, DetailView)
- Forms menggunakan `django.forms.ModelForm`
- File upload disimpan di `MEDIA_ROOT/designs/`
- Autentikasi menggunakan `django.contrib.auth` bawaan Django
- Semua halaman admin menggunakan decorator `@login_required` + `@user_passes_test(lambda u: u.is_staff)`
- Payment callback endpoint harus `@csrf_exempt`

**Konteks domain bisnis:**
- Produk adalah barang percetakan kemasan custom (box, amplop, kertas)
- Pelanggan boleh memesan tanpa desain dulu (tapi bisa upload desain sebagai file)
- Admin memverifikasi dan memproses setiap pesanan secara manual
- Tidak ada fitur desain online — pelanggan upload file desain jadi (PDF/PNG/AI)
- Dua metode pengiriman: `DELIVERY` (isi alamat wajib) atau `PICKUP` (ambil di toko)
- Pembayaran via Midtrans Snap (pop-up payment page)
- Pesanan otomatis batal jika tidak dibayar dalam 1 jam

**Alur transaksi utama:**
```
Register/Login
  → Browse Katalog
    → Lihat Detail Produk
      → Tambah ke Keranjang (+ upload desain custom)
        → Checkout (pilih delivery/pickup, isi alamat)
          → Payment via Midtrans
            → [Sukses] Order status = PAID
            → [Tidak bayar 1 jam] Order status = CANCELLED (auto)
              → Admin update status: PROCESSING → SHIPPED → COMPLETED
                → User tracking status pesanan
```

---

*Dokumen ini dibuat berdasarkan Requirements Document KEL10 – Kahta Grafika (2026).*  
*Selalu update dokumen ini jika ada perubahan scope atau arsitektur selama development.*
