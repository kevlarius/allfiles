import os
from logging.config import fileConfig

from sqlalchemy import create_engine, engine_from_config, pool, text
from sqlalchemy.engine.url import make_url

from alembic import context

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
from data.models import Base

target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.
section = config.config_ini_section
config.set_section_option(section, "DB_USER", os.environ.get("DB_USER", "postgres"))
config.set_section_option(section, "DB_PASS", os.environ.get("DB_PASS", "postgres"))


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def create_db_if_not_exist():
    db_url_key = "sqlalchemy.url"
    section_config = config.get_section(config.config_ini_section, {})
    if db_url_key not in section_config:
        raise Exception(f"Missing '{db_url_key}' in config")
    db_url = make_url(section_config[db_url_key])
    database_name = db_url.database
    db_url = db_url._replace(database=None)
    engine = create_engine(db_url.render_as_string(hide_password=False))
    connection = engine.connect()

    # check database presence on the server
    result = connection.execute(
        text(f"SELECT 1 FROM pg_database WHERE datname = '{database_name}'")
    )
    if result.first() is None:
        print(f"Database '{database_name}' is missing on the host. Creating database.")
        # committing will end a transaction
        connection.execute(text("COMMIT"))
        # we can run "CREATE DATABASE" only in not transaction mode
        connection.execute(
            text(
                f"CREATE DATABASE {database_name} "
                f"ENCODING='UTF8' LOCALE='ru_RU.UTF-8' TEMPLATE='template0'"
            )
        )


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    create_db_if_not_exist()
    run_migrations_online()
