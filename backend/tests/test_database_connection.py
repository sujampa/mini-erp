from sqlmodel import Session, text

from app.core.database import engine


def test_database_connection():
    with Session(engine) as session:
        result = session.exec(text("SELECT current_database()"))
        database_name = result.one()[0]

        print(f"Connected database: {database_name}")

        assert database_name == "mini_erp"


if __name__ == "__main__":
    test_database_connection()
    print("Database connection test passed.")
