from app.core.config import get_settings
from app.db.seed import seed_demo_data
from app.db.session import create_engine_and_session_factory


def main() -> None:
    settings = get_settings()
    engine, session_factory = create_engine_and_session_factory(settings)
    with session_factory() as session:
        seed_demo_data(session)
    engine.dispose()
    print("Seed data created or updated.")


if __name__ == "__main__":
    main()
