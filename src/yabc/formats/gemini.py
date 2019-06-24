from yabc import csv_to_json
from yabc import transaction


def fname_to_tx_gemini(fname: str):
    gems = csv_to_json.gemini_to_dict(fname) if fname else None
    txs = []
    for g in gems:
        t = transaction.Transaction.FromGeminiJSON(g)
        txs.append(t)
    return txs


class GeminiParser:
    def __init__(self, fname_or_file):
        self.txs = []
        self.flags = []
        if isinstance(fname_or_file, str):
            self.txs = fname_to_tx_gemini(fname_or_file)
        else:
            tx_dicts = csv_to_json.from_gemini(fname_or_file)
            self.txs = [transaction.Transaction.FromGeminiJSON(i) for i in tx_dicts]

    def __iter__(self):
        return self

    def __next__(self):
        if not self.txs:
            raise StopIteration
        return self.txs.pop(0)
