# init_db.py - convenience script to create DB and seed an admin
from models import init_db, create_user, find_user_by_email
if __name__ == "__main__":
    init_db()
    a = find_user_by_email("admin@elitegold.local")
    if not a:
        create_user("admin@elitegold.local", "admin123", role="admin")
        print("Seeded admin: admin@elitegold.local / admin123")
    else:
        print("Admin already exists")
