"""
Add the column adjustment for wash sales, etc.
"""
import sys

from yabc.server import sql_backend


def main(args):
    db = sql_backend.SqlBackend(args[1])
    db.session.execute("alter table basis_report add adjustment varchar")
    db.session.commit()
    db.session.close()


if __name__ == "__main__":
    main(sys.argv)
