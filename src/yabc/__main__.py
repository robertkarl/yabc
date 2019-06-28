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
import sys

import yabc.transaction_parser
from yabc import basis
from yabc.costbasisreport import ReportBatch


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("filenames", nargs="+", metavar="filename")
    args = parser.parse_args()
    tx_files = [
        yabc.transaction_parser.TxFile(open(fname), None) for fname in args.filenames
    ]
    parser = yabc.transaction_parser.TransactionParser(tx_files)
    if parser.flags:
        for flag in parser.flags:
            print(flag, file=sys.stderr)
        print("Quitting yabc.", file=sys.stderr)
        sys.exit(1)
    processor = basis.BasisProcessor("FIFO", parser.txs)
    reports = processor.process()
    batch = ReportBatch(reports)
    print(batch.human_readable_report())


if __name__ == "__main__":
    main()
