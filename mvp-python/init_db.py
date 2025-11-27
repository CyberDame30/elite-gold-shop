# init_db.py — окремий скрипт для створення БД і початкового адміна

from models import init_db, create_user, find_user_by_email

if __name__ == "__main__":
    print("🔧 Initializing database...")

    # створення таблиць
    init_db()

    # перевірка чи є адмін
    admin_email = "admin@elitegold.local"
    admin_pass = "admin123"

    admin = find_user_by_email(admin_email)

    if not admin:
        create_user(admin_email, admin_pass, role="admin")
        print(f"✅ Створено адміністратора:")
        print(f"    Email: {admin_email}")
        print(f"    Пароль: {admin_pass}")
    else:
        print("ℹ️ Адміністратор вже існує:")
        print(f"    {admin_email}")
