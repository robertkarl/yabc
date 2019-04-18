import hashlib
import tempfile

import flask
import sqlalchemy
from sqlalchemy.orm import sessionmaker

from yabc import Base
from yabc import basis
from yabc import taxdoc
from yabc import transaction
from yabc import user

# TODO: remove all references to `storage'


class SqlBackend:
    def __init__(self):
        # Note: some web servers (aka Flask) will create a new instance of this
        # class for each request.
        engine = sqlalchemy.create_engine("sqlite:///tmp.db", echo=True)
        Session = sessionmaker(bind=engine)
        self.session = Session()
        Base.metadata.create_all(engine)

    def add_tx(self, userid):
        tx = flask.request.get_data()
        if not userid in storage[ADHOC_KEY]:
            storage[ADHOC_KEY][userid] = []
        loaded_tx = transaction.Transaction.FromCoinbaseJSON(json.loads(tx))
        storage[ADHOC_KEY][userid].append(loaded_tx)
        return "Transaction added. Operation is {}.\n".format(loaded_tx.operation)

    def add_user(self, userid):
        user_obj = user.User(user_id=userid)
        self.session.add(user_obj)
        self.session.commit()
        return "user {} created\n".format(userid)

    def add_document(self, exchange, userid):
        submitted_stuff = flask.request.get_data()
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
        print(docs)
        all_txs = []
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
        ans += "total profit of {}".format(profit)
        return ans
