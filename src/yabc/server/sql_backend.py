import sqlalchemy
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from yabc import basis
from yabc import transaction


class SqlBackend():

    def __init__(self):
        engine = sqlalchemy.create_engine("sqlite:///:memory:", echo=True)
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


    def add_document(self, exchange, userid):
        submitted_stuff = flask.request.get_data()
        contents_md5_hash = hashlib.md5(submitted_stuff).hexdigest()
        storage[DOCS_KEY][contents_md5_hash] = {
            "exchange": exchange,
            "userid": userid,
            "contents": submitted_stuff,
        }
        return "stored in memory. hash: {}\n".format(contents_md5_hash)


    def run_basis(self, userid):
        """
        Given a userid, look up all of their tax documents and run basis calculator
        on all trannies.

        Returns: the total profit as a JSON object (just an integer or float).
        """
        docs = []
        for object_key in storage[DOCS_KEY]:
            if storage[DOCS_KEY][object_key]["userid"] == userid:
                docs.append(storage[DOCS_KEY][object_key])
        all_txs = []
        if userid in storage[ADHOC_KEY]:
            all_txs.extend(storage[ADHOC_KEY][userid])
        for taxdoc in docs:
            tmp_fname = "/tmp/tmp"
            temp = tempfile.NamedTemporaryFile(delete=False)
            temp.write(taxdoc["contents"])
            temp.close()
            if taxdoc["exchange"] == "gemini":
                all_txs.extend(basis.get_all_transactions(None, temp.name))
            if taxdoc["exchange"] == "coinbase":
                all_txs.extend(basis.get_all_transactions(temp.name, None))
        basis_reports = basis.process_all(all_txs)
        ans = ""
        for tx in basis_reports:
            ans += "Profit (loss) of {} on {}\n".format(tx.gain_or_loss, tx.date_sold)
        profit = sum([tx.gain_or_loss for tx in basis_reports])
        ans += "total profit of {}".format(profit)
        return ans
