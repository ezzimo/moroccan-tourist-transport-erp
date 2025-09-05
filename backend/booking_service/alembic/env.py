import os
import sys
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlmodel import SQLModel

# Add the project root to the Python path for module resolution
sys.path.insert(0, os.path.realpath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))

# Import your app's engine and models
from backend.booking_service.database import engine
from backend.booking_service import models  # noqa: F401 ensures models are registered

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set target metadata for 'autogenerate' support
target_metadata = SQLModel.metadata

# Naming convention for Alembic autogenerate to prevent churn
naming_convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}
# Apply naming convention to the metadata in the context
# This is an alternative to setting it on the MetaData object directly
# and is often more reliable when metadata is implicitly created by a framework.
# However, for this to work, we must ensure the context is configured with it.
# The most robust way is to pass it to context.configure.

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = str(engine.url)
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        naming_convention=naming_convention,
        compare_type=True,
        compare_server_default=True,
        render_as_batch=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    # Use the application's engine directly
    connectable = engine

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            naming_convention=naming_convention,
            compare_type=True,
            compare_server_default=True,
            render_as_batch=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
