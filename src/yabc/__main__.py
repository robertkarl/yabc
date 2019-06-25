"""
Entry point to command line yabc usage.

Example:

```
pip install yabc
python -m yabc statement_from_coinbase.csv my_gemini_statement.csv adhoc.csv
```

File types are automatically detected.
"""
import argparse

import yabc.transaction_parser
from yabc import basis
from yabc.basis import human_readable_report


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("filenames", nargs="+", metavar="filename")
    args = parser.parse_args()
    tx_files = [
        yabc.transaction_parser.TxFile(open(fname), None) for fname in args.filenames
    ]
    parser = yabc.transaction_parser.TransactionParser(tx_files)
    processor = basis.BasisProcessor("FIFO", parser.txs)
    txs = processor.process()
    print(human_readable_report(txs))


if __name__ == "__main__":
    main()
