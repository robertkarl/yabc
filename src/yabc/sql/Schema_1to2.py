import sys

from yabc.basis import CostBasisReport
from yabc.server import sql_backend


def main(args):
    db = sql_backend.SqlBackend(args[1])
    CREATE_META = """create table if not exists meta (id integer primary_key,
    schema integer);
    """
    db.session.execute(CREATE_META)
    db.session.execute(
        "insert into meta values (0, {});".format(sql_backend.SCHEMA_VERSION)
    )
    db.session.commit()
    CostBasisReport.__table__.create(db.engine)
    db.session.close()


if __name__ == "__main__":
    main(sys.argv)
