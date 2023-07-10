import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker


def get_database_url():
    db_user = os.environ.get("DB_USER", "postgres")
    db_pass = os.environ.get("DB_PASS", "postgres")
    return f"postgresql://{db_user}:{db_pass}@localhost:5432/allfiles"


def open_connection(db_url) -> scoped_session:
    created_engine = create_engine(
        url=db_url,
        connect_args={"connect_timeout": 2},
        echo=False,
        pool_size=5,
    )
    session_factory = sessionmaker(bind=created_engine)
    session = scoped_session(session_factory)

    return session


def get_session() -> scoped_session:
    for _ in range(0, 3):
        try:
            return open_connection(get_database_url())
        except Exception as ex:
            print(f"Error {ex}")

    raise Exception("Could not connect to database")


def close_session(session: scoped_session):
    session.expunge_all()
    session.close()
    engine = session.get_bind()
    engine.dispose()
