"""
Entry point to command line yabc usage.
"""
import argparse

import yabc.transaction_parser
from yabc import basis


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("filenames", nargs="+", metavar="filename")
    args = parser.parse_args()
    tx_files = [
        yabc.transaction_parser.TxFile(open(fname), None) for fname in args.filenames
    ]
    parser = yabc.transaction_parser.TransactionParser(tx_files)
    processor = basis.BasisProcessor("FIFO", parser.txs)
    for i in processor.process():
        print(i)

print(__name__)
if __name__ == "__main__":
    main()
