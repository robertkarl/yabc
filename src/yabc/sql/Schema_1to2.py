import sys

from yabc.basis import CostBasisReport
from yabc.server import sql_backend 

def main(args):
    db = sql_backend.SqlBackend(args[1])
    CostBasisReport.__table__.create(db.engine)

if __name__ == "__main__":
    main(sys.argv)
