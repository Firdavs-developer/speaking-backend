# PythonAnywhere'ga joylash (deploy) — qadam-baqadam

> Quyida `YOURUSERNAME` ni o'zingizning PythonAnywhere foydalanuvchi nomingiz bilan
> almashtiring. Buyruqlar Linux bash uchun (oldinga qiya chiziq `/`).

---

## 0. Tayyorgarlik: kodni GitHub'ga yuklash

PythonAnywhere'ga kodni olib borishning eng oson yo'li — GitHub orqali.

Kompyuteringizda (bash terminalda, `speaking backend` papkasida):

```bash
git init
git add .
git commit -m "Speaking backend"
```

So'ng GitHub'da yangi (bo'sh) repo yarating, masalan `speaking-backend`, va:

```bash
git remote add origin https://github.com/SIZNING_GITHUB/speaking-backend.git
git branch -M main
git push -u origin main
```

> `.gitignore` `venv/`, `db.sqlite3`, `.env` ni yuklamaydi — bu to'g'ri, ularni
> serverda alohida yaratamiz.

---

## 1. PythonAnywhere'da ro'yxatdan o'tish

1. https://www.pythonanywhere.com → **Pricing & signup** → **Create a Beginner account** (bepul).
2. Email tasdiqlang, kiring.

---

## 2. Kodni serverga klonlash

Yuqori menyudan **Consoles → Bash** oching va yozing:

```bash
git clone https://github.com/SIZNING_GITHUB/speaking-backend.git
cd speaking-backend
```

---

## 3. Virtual environment va paketlar

```bash
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## 4. `.env` faylini yaratish

```bash
nano .env
```

Ichiga quyidagini yozing (qiymatlarni o'zgartiring):

```
DJANGO_SECRET_KEY=uzun-tasodifiy-maxfiy-kalit-bu-yerga
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=YOURUSERNAME.pythonanywhere.com
ADMIN_PASSWORD=admin123
CORS_ALLOWED_ORIGINS=http://localhost:3000,https://SIZNING-FRONTEND.vercel.app
```

`Ctrl+O` → `Enter` (saqlash), `Ctrl+X` (chiqish).

> `CORS_ALLOWED_ORIGINS` ga frontend manzilingizni yozing (Vercel'ga qo'ysangiz
> o'sha domen). Hozircha lokal test uchun `http://localhost:3000` qoldiring.

---

## 5. Database, savollar va admin

```bash
python manage.py migrate
python manage.py seed_questions
python manage.py collectstatic --noinput
python manage.py createsuperuser
```

`createsuperuser` email, ism, parol so'raydi — eslab qoling, admin panelga
shular bilan kirasiz.

---

## 6. Web ilovani yaratish

1. Yuqori menyu → **Web** → **Add a new web app** → **Next**.
2. **Manual configuration** (Django emas!) tanlang → **Python 3.11** → **Next**.

### 6a. Virtualenv yo'lini ko'rsatish
**Web** sahifasida **Virtualenv** bo'limiga yozing:

```
/home/YOURUSERNAME/speaking-backend/venv
```

### 6b. WSGI faylini sozlash
**Web** sahifasida **WSGI configuration file** havolasini bosing. Ichidagi hammasini
o'chirib, quyidagini yozing:

```python
import os
import sys

path = '/home/YOURUSERNAME/speaking-backend'
if path not in sys.path:
    sys.path.insert(0, path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

Saqlang (**Save**).

### 6c. Static fayllarni map qilish (admin CSS uchun)
**Web** sahifasida **Static files** bo'limiga qator qo'shing:

| URL | Directory |
|-----|-----------|
| `/static/` | `/home/YOURUSERNAME/speaking-backend/staticfiles` |

---

## 7. Ishga tushirish

**Web** sahifasi tepasidagi katta yashil **Reload** tugmasini bosing.

Tayyor! Backend manzilingiz:

```
https://YOURUSERNAME.pythonanywhere.com/
```

Tekshiring:
- `https://YOURUSERNAME.pythonanywhere.com/` → `{"status": "ok", ...}`
- `https://YOURUSERNAME.pythonanywhere.com/admin/` → admin panel
- `https://YOURUSERNAME.pythonanywhere.com/api/questions/` → savollar

---

## 8. Frontend'ni shu backendga ulash

Frontend (`speaking`) loyihasida `.env.local` ga yozing:

```
NEXT_PUBLIC_API_BASE_URL=https://YOURUSERNAME.pythonanywhere.com
```

Agar frontend'ni Vercel'ga qo'ysangiz, o'sha env o'zgaruvchini Vercel sozlamasiga
qo'shing va qayta deploy qiling. Shuningdek backend `.env` dagi
`CORS_ALLOWED_ORIGINS` ga frontend domenini qo'shib, **Reload** bosing.

---

## Keyinchalik kodni yangilash

Kompyuterda o'zgartirib `git push` qilganingizdan keyin, PythonAnywhere bash'da:

```bash
cd speaking-backend
git pull
source venv/bin/activate
pip install -r requirements.txt        # yangi paket bo'lsa
python manage.py migrate               # model o'zgarsa
python manage.py collectstatic --noinput
```

So'ng **Web → Reload**.

---

## Muhim eslatmalar (bepul reja)

- **Uxlamaydi**, lekin har **3 oyda** "Run until 3 months from today" tugmasini bosish
  kerak (emailga eslatma keladi).
- Tashqi internetga chiqish cheklangan (faqat oq ro'yxatdagi saytlar). Bu backend'ga
  ta'sir qilmaydi — u tashqi API chaqirmaydi. (Groq AI chaqiruvi frontend tomonida.)
- Database **SQLite** (`db.sqlite3`) — disk doimiy, ma'lumotlar saqlanib qoladi.
