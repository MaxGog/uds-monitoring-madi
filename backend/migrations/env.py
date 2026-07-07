import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config
from backend.config.config import settings
from alembic import context

from backend.core.db.postgres.base_orm import Base
from backend.core.db.postgres.data_orms.user_orm import User
from backend.core.db.postgres.data_orms.task_orm import Task
from backend.core.db.postgres.data_orms.copmany_orm import Company
from backend.core.db.postgres.data_orms.work_orm import Work
from backend.core.db.postgres.data_orms.act_orm import WorkAct, WorkActItem
from backend.core.db.postgres.data_orms.contract_orm import Contract, ContractItem
from backend.core.db.postgres.data_orms.object_orm import Object
from backend.core.db.postgres.data_orms.document_orm import Document
from backend.core.db.postgres.data_orms.role_orm import Role, Permission

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

# Наши очень важные ормки с базой
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


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


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)
    
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """In this scenario we need to create an Engine
    and associate a connection with the context.

    """


    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    # Наши очень важные настройки
    database_url = settings.db.DB_URL
    config.set_main_option("sqlalchemy.url", database_url)

    configuration = config.get_section(config.config_ini_section) or {}
    configuration["sqlalchemy.url"] = database_url
    
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
