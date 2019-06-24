"""
Entry point to command line yabc usage.
"""
import argparse

from yabc.transaction_parser import TransactionParser, TxFile

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("filenames", nargs="+", metavar="filename")
    args = parser.parse_args()
    tx_files = [TxFile(open(fname), None) for fname in args.filenames]
    parser = TransactionParser(tx_files)
    print(parser.txs)


print(__name__)
if __name__ == "__main__":
    main()