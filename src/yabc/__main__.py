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
from yabc import coinpool
from yabc.costbasisreport import ReportBatch


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("filenames", nargs="+", metavar="filename")
    args = parser.parse_args()
    tx_files = [
        yabc.transaction_parser.TxFile(open(fname), None) for fname in args.filenames
    ]
    parser = yabc.transaction_parser.TransactionParser(tx_files)
    parser.parse()
    if parser.flags:
        for flag in parser.flags:
            print(flag, file=sys.stderr)
        print("Quitting yabc.", file=sys.stderr)
        sys.exit(1)
    processor = basis.BasisProcessor(coinpool.PoolMethod.FIFO, parser.txs)
    reports = processor.process()
    batch = ReportBatch(reports)
    print(batch.human_readable_report())
    print("Remaining coins after sales:")
    for symbol in processor.get_pool().known_symbols():
        for coin in processor.get_pool().get(symbol):
            print(coin)


if __name__ == "__main__":
    main()
