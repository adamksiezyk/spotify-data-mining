from __future__ import annotations

import os
from sqlalchemy.dialects.postgresql import insert
import sqlalchemy.orm
from dotenv import load_dotenv
from typing import Optional, Tuple, Type, List, Dict, Any, Union


Base = sqlalchemy.orm.declarative_base()
Table = Type[Base]
Instance = Base

_CONNECTION_TYPES = {
    'sqlite': "sqlite:///{address}/{db_name}",
    'postgres': "postgresql://{username}:{password}@{address}:{port}/{db_name}"
}


class Connection:
    def __init__(self, url: str):
        self._engine = sqlalchemy.create_engine(url)

    def create_ddl(self, base: Table) -> None:
        base.metadata.create_all(self._engine)

    def upsert(self,
               table: Table,
               values: Union[Dict[str, Any], List[Dict[str, Any]]],
               *,
               columns: Optional[List[str]] = None) -> List[Tuple]:
        columns = ["id"] if columns is None else columns
        ret_val = [getattr(table, attr) for attr in columns]
        with self._engine.connect() as connection:
            return connection.execute(insert(table).\
                                          on_conflict_do_nothing(index_elements=columns).\
                                          returning(*ret_val),
                                      values).all()

    def select_all(self, table: Table) -> sqlalchemy.orm.Query:
        with sqlalchemy.orm.Session(self._engine) as session:
            return session.query(table)

    def delete(self, obj: Instance) -> None:
        with sqlalchemy.orm.Session(self._engine) as session:
            session.delete(obj)
            session.commit()


def connection_factory(connector_type: str,
                       address: str,
                       port: str,
                       db_name: str,
                       username: str,
                       password: str) -> Connection:
    conn_str = _CONNECTION_TYPES[connector_type]
    return Connection(conn_str.format(address=address,
                                      port=port,
                                      db_name=db_name,
                                      username=username,
                                      password=password))


load_dotenv()
_conn = connection_factory(
    connector_type=os.environ['DB_TYPE'],
    address=os.environ['DB_ADDRESS'],
    port=os.environ['DB_PORT'],
    db_name=os.environ['DB_NAME'],
    username=os.environ['DB_USERNAME'],
    password=os.environ['DB_PASSWORD'])
