# Speaking Backend (Django)

IELTS Speaking ilovasi uchun Django + DRF backend. Quyidagilarni
**databasega (SQLite) saqlaydi**:

- **Ro'yxatdan o'tgan userlar** — `accounts` app (`User` modeli, email orqali login)
- **Speaking savollar** — `questions` app (`Question` modeli)
- **Userlar natijalari** — `results` app (`Result` + `Answer` modellari)

## Ishga tushirish

```powershell
cd "speaking backend"

# Virtual environment (allaqachon yaratilgan bo'lsa o'tkazib yuboring)
py -m venv venv
./venv/Scripts/python.exe -m pip install -r requirements.txt

# Migratsiyalar va boshlang'ich savollar
./venv/Scripts/python.exe manage.py migrate
./venv/Scripts/python.exe manage.py seed_questions

# Admin panel uchun superuser (ixtiyoriy)
./venv/Scripts/python.exe manage.py createsuperuser

# Serverni ishga tushirish
./venv/Scripts/python.exe manage.py runserver
```

Backend `http://127.0.0.1:8000` da, admin panel `/admin/` da ishlaydi.

## Sozlamalar (.env)

`.env.example` ni `.env` ga nusxalang. Asosiy o'zgaruvchilar:

- `ADMIN_PASSWORD` — savollarni boshqarish paroli (frontend bilan bir xil, default `admin123`)
- `CORS_ALLOWED_ORIGINS` — frontend manzili (default `http://localhost:3000`)

## API endpointlar

### Auth (`accounts`)
| Metod | URL | Tavsif |
|-------|-----|--------|
| POST | `/api/auth/register/` | `{name, email, password}` → `{token, user}` |
| POST | `/api/auth/login/` | `{email, password}` → `{token, user}` |
| POST | `/api/auth/logout/` | tokenni o'chiradi (auth kerak) |
| GET | `/api/auth/me/` | joriy user (auth kerak) |

Auth uchun so'rovga header qo'shiladi: `Authorization: Token <token>`

### Savollar (`questions`)
| Metod | URL | Tavsif |
|-------|-----|--------|
| GET | `/api/questions/` | `{questions: [...]}` (hammaga ochiq) |
| POST | `/api/questions/` | butun savollar to'plamini almashtiradi (admin) |

Admin POST uchun header: `X-Admin-Token: <ADMIN_PASSWORD>`

### Natijalar (`results`)
| Metod | URL | Tavsif |
|-------|-----|--------|
| POST | `/api/results/` | `{answers, evaluation}` natijani saqlaydi |
| GET | `/api/results/` | joriy userning natijalari (auth kerak) |
| GET | `/api/results/<id>/` | bitta natija (auth kerak) |

JSON format frontenddagi `Question`, `SubmittedAnswer` va
`EvaluationResult` tiplariga mos.
