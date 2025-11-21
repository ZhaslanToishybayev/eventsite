# 🔄 Синхронизация БД с Production

## Проблема:
Локальная копия проекта имеет **другую базу данных**, чем production сервер.

---

## ✅ РЕШЕНИЕ 1: Скопировать БД с production

### Если используете SQLite:

```bash
# На production сервере:
scp /path/to/db.sqlite3 user@local-machine:/path/to/project/

# На локальной машине:
# БД уже скопирована, перезапустите сервер
```

### Если используете PostgreSQL:

```bash
# На production сервере создайте дамп:
pg_dump -U postgres -d unitysphere > unitysphere_dump.sql

# Скопируйте на локальную машину:
scp unitysphere_dump.sql user@local-machine:/tmp/

# На локальной машине восстановите:
psql -U postgres -d unitysphere_local < /tmp/unitysphere_dump.sql
```

---

## ✅ РЕШЕНИЕ 2: Использовать production БД напрямую

### В settings.py укажите production БД:

```python
# core/settings.py

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'unitysphere',
        'USER': 'postgres',
        'PASSWORD': 'your_password',
        'HOST': 'your-production-server.com',  # ← Production сервер
        'PORT': '5432',
    }
}
```

**⚠️ ВНИМАНИЕ:** Это опасно для production! Используйте только для чтения.

---

## ✅ РЕШЕНИЕ 3: Создать тестовые данные локально

```bash
source venv/bin/activate
python manage.py shell
```

```python
from clubs.models import Club, ClubCategory, City
from django.contrib.auth import get_user_model

User = get_user_model()

# Создайте категории
sport, _ = ClubCategory.objects.get_or_create(name="Спортивные клубы")
hobby, _ = ClubCategory.objects.get_or_create(name="Хобби клубы")

# Создайте город
city, _ = City.objects.get_or_create(name="Алматы", iata_code="ALA")

# Создайте пользователя
user = User.objects.first() or User.objects.create_user('admin', 'admin@example.com', 'password')

# Создайте клубы
Club.objects.get_or_create(
    name="Танцующие Экстазы",
    defaults={
        'category': hobby,
        'description': 'Клуб для любителей танцев',
        'city': city,
        'creater': user,
        'is_active': True
    }
)

print("✅ Тестовые данные созданы!")
```

---

## 📊 ПРОВЕРКА:

```bash
python manage.py shell
```

```python
from clubs.models import Club
print(f"Всего клубов: {Club.objects.count()}")
for club in Club.objects.all():
    print(f"- {club.name}")
```

---

## 💡 РЕКОМЕНДАЦИЯ:

Для разработки используйте **отдельную БД** с тестовыми данными.
Для production - **никогда не меняйте данные** с локальной машины!
