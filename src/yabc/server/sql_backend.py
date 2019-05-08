"""
Track the sql alchemy session and provide methods for endpoints.
"""

__author__ = "Robert Karl <robertkarljr@gmail.com>"

import hashlib
import io
import json
import tempfile

import click
import flask
import sqlalchemy
from flask.cli import with_appcontext
from sqlalchemy.orm import sessionmaker

from yabc import Base
from yabc import basis
from yabc import taxdoc
from yabc import transaction
from yabc import user


@click.command("init-db")
@with_appcontext
def init_db_command():
    db = get_db()
    db.create_tables()
    click.echo("Initialized the database.")


def get_db():
    if "yabc_db" not in flask.g:
        flask.g.yabc_db = SqlBackend(flask.current_app.config["DATABASE"])
    return flask.g.yabc_db


def close_db(e=None):
    db = flask.g.pop("db", None)
    if db is not None:
        db.session.close()


def init_app(app):
    app.cli.add_command(init_db_command)
    app.teardown_appcontext(close_db)


class SqlBackend:
    def __init__(self, db_path):
        # Note: some web servers (aka Flask) will create a new instance of this
        # class for each request.
        self.engine = sqlalchemy.create_engine(
            "sqlite:///{}".format(db_path),
            echo=True,
            poolclass=sqlalchemy.pool.QueuePool,
        )
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    def create_tables(self):
        Base.metadata.create_all(self.engine, checkfirst=True)

    def add_tx(self, userid, tx):
        loaded_tx = transaction.Transaction.FromCoinbaseJSON(json.loads(tx))
        loaded_tx.user_id = userid
        self.session.add(loaded_tx)
        self.session.commit()
        return "Transaction added for user {}. Operation is {}.\n".format(
            userid, loaded_tx.operation
        )

    def user_create(self, name):
        user_obj = user.User(username=name)
        self.session.add(user_obj)
        self.session.commit()
        return json.dumps(user_obj.id)

    def user_read(self, uid):
        users = self.session.query(user.User).filter_by(id=uid)
        if users.count():
            return json.dumps(users[0])
        return flask.jsonify({"error": "invalid userid"})

    def tx_list(self, userid):
        """ TODO
        """
        docs = self.session.query(transaction.Transaction).filter_by(user_id=userid)
        ans = []
        for tx in docs.all():
            tx_dict = dict(tx.__dict__)
            tx_dict.pop('_sa_instance_state')
            ans.append(tx_dict)
        return flask.jsonify(ans)

    def taxdoc_list(self, userid):
        docs = self.session.query(taxdoc.TaxDoc).filter_by(user_id=userid)
        result = []
        for obj in docs.all():
            result.append(
                {
                    "userid": obj.user_id,
                    "file_name": obj.file_name,
                    "hash": obj.file_hash,
                    "preview": obj.contents[:10].decode() + "...",
                }
            )
        return flask.jsonify(result)

    def taxdoc_create(self, exchange, userid, submitted_file):
        """
        Add the tx doc for this user.

        Also perform inserts for each of its rows.

        @param submitted_file: a filelike object
        exchange and userid should be strings.
        """
        submitted_stuff = submitted_file.read()
        submitted_file.seek(0)
        tx = basis.transactions_from_file(submitted_file, exchange)
        contents_md5_hash = hashlib.md5(submitted_stuff).hexdigest()
        taxdoc_obj = taxdoc.TaxDoc(
            exchange=exchange,
            user_id=userid,
            file_hash=contents_md5_hash,
            contents=submitted_stuff,
            file_name=submitted_file.filename,
        )
        self.session.add(taxdoc_obj)
        for t in tx:
            t.user_id = userid
            self.session.add(t)
        self.session.commit()
        return flask.jsonify(
            {
                "hash": contents_md5_hash,
                "result": "success",
                "exchange": exchange,
                "preview": str(submitted_stuff[:20]),
            }
        )

    def run_basis(self, userid):
        """
        Given a userid, look up all of their tax documents and run basis calculator
        on all txs.

        TODO: There is some impedance mismatch between flask and python's csv
        module.  csv requires CSVs to be written as strings, while flask's
        underlying web server requires applications to write binary responses.
        Currently we write to the CSV with strings, and then read the entire
        contents into memory and write to an in-memory binary file-like object
        which is handed off to flask. Fix.

        Returns: CSV containing cost basis reports useful for the IRS.
        """
        docs = self.session.query(taxdoc.TaxDoc).filter_by(user_id=userid)
        adhoc_txs = self.session.query(transaction.Transaction).filter_by(
            user_id=userid
        )
        all_txs = list(adhoc_txs)
        for taxdoc_obj in docs:
            tmp_fname = "/tmp/tmp"
            temp = tempfile.NamedTemporaryFile(delete=False)
            temp.write(taxdoc_obj.contents)
            temp.close()
            if taxdoc_obj.exchange == "gemini":
                all_txs.extend(basis.get_all_transactions(None, temp.name))
            if taxdoc_obj.exchange == "coinbase":
                all_txs.extend(basis.get_all_transactions(temp.name, None))
        basis_reports = basis.process_all(all_txs)
        stringio_file = basis.reports_to_csv(basis_reports)
        mem = io.BytesIO()
        mem.write(stringio_file.getvalue().encode("utf-8"))
        mem.seek(0)
        return mem
