"""
Track the sql alchemy session and provide methods for endpoints.
"""
import datetime
import hashlib
import io
import json
import logging
from io import TextIOWrapper

import click
import flask
import sqlalchemy
from flask import make_response
from flask.cli import with_appcontext
from sqlalchemy.orm import sessionmaker

from yabc import Base
from yabc import basis
from yabc import costbasisreport
from yabc import taxdoc
from yabc import transaction
from yabc import user
from yabc.costbasisreport import CostBasisReport
from yabc.formats import coinbase
from yabc.transaction_parser import TransactionParser
from yabc.transaction_parser import TxFile
from yabc.user import User

__author__ = "Robert Karl <robertkarljr@gmail.com>"


DB_KEY = "yabc_db"


@click.command("init-db")
@with_appcontext
def init_db_command():
    db = get_db()
    db.create_tables()
    click.echo("Initialized the database.")


@click.command("show-db-config")
@with_appcontext
def show_db_command():
    db = get_db()
    click.echo(db._db_url)


def get_db():
    if DB_KEY not in flask.g:
        flask.g.yabc_db = SqlBackend(flask.current_app.config["DATABASE"])
    return flask.g.yabc_db


def close_db(e=None):
    db = flask.g.pop(DB_KEY, None)
    if db is not None:
        db.session.close()


def init_app(app):
    app.cli.add_command(init_db_command)
    app.cli.add_command(show_db_command)
    app.teardown_appcontext(close_db)


class SqlBackend:
    """
    Handle to the database as well as where DB routines are stored.

    All access to this class should be  done through get_db() above.
    TODO: move get_db() to be a staticmethod here.

    Two backends are supported: sqlite and postgres. Others may work unintentionally.

    NOTE: We must be able to create SqlBackends without a flask instance running.
    """

    def __init__(self, db_url=None):
        if db_url is None:
            db_url = flask.current_app.config["DATABASE"]
        self._db_url = db_url
        # Note: some web servers (aka Flask) will create a new instance of this
        # class for each request.
        self.engine = sqlalchemy.create_engine(
            db_url, poolclass=sqlalchemy.pool.QueuePool
        )
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    def create_tables(self):
        Base.metadata.create_all(self.engine, checkfirst=True)

    def add_tx(self, userid, tx):
        assert tx
        loaded_tx = coinbase.FromCoinbaseJSON(json.loads(tx))
        loaded_tx.user_id = userid
        self.session.add(loaded_tx)
        self.session.commit()
        return "Transaction added for user {}. Operation is {}.\n".format(
            userid, loaded_tx.operation
        )

    def user_create(self, name):
        user_obj = user.User(username=name, password="")
        self.session.add(user_obj)
        self.session.commit()
        return json.dumps(user_obj.id)

    def user_read(self, uid):
        users = self.session.query(user.User).filter_by(id=uid)
        if users.count():
            return json.dumps(users[0])
        return flask.jsonify({"error": "invalid userid"})

    def tx_delete(self, userid, txid):
        """
        Note that we need to clear BasisReports if transactions change.
        :param userid:
        :param txid:
        :return:
        """
        self.session.query(transaction.Transaction).filter_by(
            user_id=userid, id=txid
        ).delete()
        self.session.query(CostBasisReport).filter_by(user_id=userid).delete()
        self.session.commit()

    def tx_update(self, userid, txid, values):
        docs = self.session.query(transaction.Transaction).filter_by(
            user_id=userid, id=txid
        )
        obj = docs.all()[0]
        for key in values:
            if key in obj.__dict__:
                setattr(obj, key, values[key])
        self.session.commit()

    def tx_list(self, userid):
        docs = self.session.query(transaction.Transaction).filter_by(user_id=userid)
        ans = []
        for tx in docs.all():
            tx_dict = dict(tx.__dict__)
            tx_dict.pop("_sa_instance_state")
            ans.append(tx_dict)
            for numeric_key in ("usd_subtotal", "fees", "quantity"):
                tx_dict[numeric_key] = str(tx_dict[numeric_key])
            tx_dict["operation"] = tx_dict["operation"].value
        for item in ans:
            item["date"] = str(item["date"])
        return json.dumps(ans)

    def taxdoc_list(self, userid):
        docs = self.session.query(taxdoc.TaxDoc).filter_by(user_id=userid)
        result = []
        for obj in docs.all():
            preview = obj.contents[:10]
            if not isinstance(preview, str):
                # Sqlite seems to return the file contents as bytes, while
                # Postgres returns a string.
                preview = preview.decode()
            result.append(
                {
                    "userid": obj.user_id,
                    "file_name": obj.file_name,
                    "hash": obj.file_hash,
                    "preview": preview + "...",
                }
            )
        return flask.jsonify(result)

    def taxyear_list(self, userid, url_prefix, suffix):
        """
        Basic statistics and download links for each taxyear the given user has data for.

        @param userid
        @param url_prefix (str): for each row, a link for downloading is displayed.
        @param suffix (str): file suffix for the downloaded file.
        """
        current_year = 2019
        user = self.session.query(User).filter_by(id=userid).first()
        sale_dates = self.session.query(
            sqlalchemy.distinct(basis.CostBasisReport.date_sold)
        ).filter_by(user_id=userid)
        years = set([i[0].year for i in sale_dates])
        years.discard(current_year)
        years = sorted(years)
        result = []
        for ty in years:
            year_info = {"year": ty}
            reports = list(self.reports_in_taxyear(userid, ty))
            dollar_keys = ["taxable_income", "shortterm", "longterm"]
            year_info["taxable_income"] = int(sum([i.gain_or_loss for i in reports]))
            year_info["shortterm"] = int(
                sum([i.gain_or_loss for i in reports if not i.long_term])
            )
            year_info["longterm"] = int(
                sum([i.gain_or_loss for i in reports if i.long_term])
            )
            for key in dollar_keys:
                if year_info[key] >= 0:
                    year_info[key] = "${:,}".format(year_info[key])
                else:
                    year_info[key] = "-${:,}".format(-year_info[key])
            year_info["url8949"] = "{}/{}".format(url_prefix, ty)
            year_info["url8949_label"] = "{}-{}-8949.{}".format(
                user.username, ty, suffix
            )
            result.append(year_info)
        return flask.jsonify(result)

    def import_transaction_document(self, userid, submitted_file):
        """
        Add the tx doc for this user.

        - Perform inserts for each of its rows.
        - Recalculate CostBasisReports also.

        @param submitted_file: a filelike object
        exchange and userid should be strings.
        """
        submitted_stuff = submitted_file.read()
        text_mode_file = TextIOWrapper(submitted_file)
        submitted_file.seek(0)
        tx_file = TxFile(text_mode_file, None)
        parser = TransactionParser([tx_file])
        parser.parse()
        if not parser.succeeded():
            val = flask.jsonify({"result": "failure", "flags": parser.flags})
            return make_response(val, 400)
        tx = parser.txs
        contents_md5_hash = hashlib.md5(submitted_stuff).hexdigest()
        taxdoc_obj = taxdoc.TaxDoc(
            exchange=parser.get_exchange_name(),
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
        try:
            # It's possible for this to fail if the user uploads documents out of order (sells before buys)
            # TODO: gracefully handle transaction histories where a user reports SELL txs with no basis.
            self.run_basis(
                userid
            )  # TODO: determine if this is a performance bottleneck.
        except Exception as e:
            logging.warn("Failed to run basis ")
        return flask.jsonify(
            {
                "hash": contents_md5_hash,
                "result": "success",
                "exchange": parser.get_exchange_name(),
                "file_name": taxdoc_obj.file_name,
                "preview": str(submitted_stuff[:20]),
            }
        )

    def run_basis(self, userid):
        """
        Clear any CostBasisReports for this user in the database. Then recalculate them.

        TODO: There is some impedance mismatch between flask and python's csv
        module.  csv requires CSVs to be written as strings, while flask's
        underlying web server requires applications to write binary responses.
        Currently we write to the CSV with strings, and then read the entire
        contents into memory and write to an in-memory binary file-like object
        which is handed off to flask. Fix.

        Returns: just a status
        """
        self.session.query(costbasisreport.CostBasisReport).filter_by(
            user_id=userid
        ).delete()
        all_txs = list(
            self.session.query(transaction.Transaction).filter_by(user_id=userid)
        )
        basis_reports = basis.process_all("FIFO", all_txs)
        for i in basis_reports:
            self.session.add(i)
        self.session.commit()
        return "success"

    def reports_in_taxyear(self, userid, taxyear):
        start, end = self.get_tax_year_bounds(userid, taxyear)
        reports = (
            self.session.query(basis.CostBasisReport)
            .filter_by(user_id=userid)
            .filter(basis.CostBasisReport.date_sold >= start)
            .filter(basis.CostBasisReport.date_sold < end)
        )
        return reports

    def download_8949(self, userid, taxyear):
        assert isinstance(taxyear, int)
        reports = self.reports_in_taxyear(userid, taxyear)
        of = basis.reports_to_csv(reports)
        mem = io.BytesIO()
        mem.write(of.getvalue().encode("utf-8"))
        mem.seek(0)
        return mem

    def get_tax_year_bounds(self, userid, taxyear):
        first_invalid_date = datetime.datetime(taxyear + 1, 1, 1)
        start = datetime.datetime(taxyear, 1, 1)
        return start, first_invalid_date
