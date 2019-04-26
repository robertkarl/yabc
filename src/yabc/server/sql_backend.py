"""
Track the sql alchemy session and provide methods for endpoints.
"""

__author__ = "Robert Karl <robertkarljr@gmail.com>"

import hashlib
import json
import tempfile

import sqlalchemy
from sqlalchemy.orm import sessionmaker

from yabc import Base
from yabc import basis
from yabc import taxdoc
from yabc import transaction
from yabc import user


class SqlBackend:
    def __init__(self):
        # Note: some web servers (aka Flask) will create a new instance of this
        # class for each request.
        self.engine = sqlalchemy.create_engine("sqlite:///tmp.db", echo=True, poolclass=sqlalchemy.pool.QueuePool)
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
        user_obj = user.User(name=name)
        self.session.add(user_obj)
        self.session.commit()
        return json.dumps(user_obj.id)

    def user_read(self, uid):
        user_obj = user.User(id=userid)
        users = self.session.query(user.User).filter_by(userid=uid)
        if users:
            return json.dumps(users[0])
        return None

    def taxdoc_create(self, exchange, userid, submitted_stuff):
        contents_md5_hash = hashlib.md5(submitted_stuff).hexdigest()
        taxdoc_obj = taxdoc.TaxDoc(
            exchange=exchange,
            user_id=userid,
            file_hash=contents_md5_hash,
            contents=submitted_stuff,
        )
        self.session.add(taxdoc_obj)
        self.session.commit()
        return "File stored. hash: {}\n".format(contents_md5_hash)

    def run_basis(self, userid):
        """
        Given a userid, look up all of their tax documents and run basis calculator
        on all txs.

        Returns: the total profit as a JSON object (just an integer or float).
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
        ans = ""
        for tx in basis_reports:
            ans += "Profit (loss) of {} on {}\n".format(tx.gain_or_loss, tx.date_sold)
        profit = sum([tx.gain_or_loss for tx in basis_reports])
        ans += "total profit of {}\n".format(profit)
        return ans
