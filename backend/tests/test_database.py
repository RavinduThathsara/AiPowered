from unittest.mock import Mock, patch

import pytest

from app.database import create_database_engine, get_db


def test_sqlite_engine_enables_foreign_keys() -> None:
    engine = create_database_engine("sqlite://")

    with engine.connect() as connection:
        assert connection.exec_driver_sql("PRAGMA foreign_keys").scalar() == 1


def test_non_sqlite_engine_does_not_register_sqlite_connection_options() -> None:
    with patch("app.database.create_engine") as create_engine:
        create_database_engine("postgresql://user:password@localhost/example")

    create_engine.assert_called_once_with(
        "postgresql://user:password@localhost/example",
        connect_args={},
    )


def test_database_session_rolls_back_when_request_fails() -> None:
    session = Mock()

    with patch("app.database.SessionLocal", return_value=session):
        database = get_db()
        next(database)

        with pytest.raises(RuntimeError, match="request failed"):
            database.throw(RuntimeError("request failed"))

    session.rollback.assert_called_once_with()
    session.close.assert_called_once_with()
