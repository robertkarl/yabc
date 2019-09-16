[![yabc on PyPI](https://img.shields.io/pypi/v/yabc.svg)](https://pypi.org/project/yabc/)
![MIT License badge](https://img.shields.io/badge/license-MIT-green.svg)
[![yabc on TravisCI](https://travis-ci.org/robertkarl/yabc.svg?branch=master)](https://travis-ci.org/robertkarl/yabc)
![Supported Python versions](https://img.shields.io/pypi/pyversions/yabc.svg)

# yabc - a bitcoin tax calculator
yabc translates cryptocurrency trades, mining, and spending data into a list of
reports that can be sent to tax authorities.  

yabc is the tax calculator behind [https://costbasis.report/](https://costbasis.report/).

```
$ pip install yabc
$ python -m yabc ./testdata/synthetic_gemini_csv.csv ./testdata/synthetic_coinbase_csv.csv 
13 transactions to be reported

<Sold 0.76 BTC for 236 total profiting -155. Adjustment 0>
<Sold 1 BTC for 311 total profiting 29. Adjustment 0>
<Sold 2 BTC for 622 total profiting 546. Adjustment 0>
<Sold 2.5 BTC for 777 total profiting 666. Adjustment 0>
<Sold 0.04290503 BTC for 594 total profiting 572. Adjustment 0>
<Sold 0.35608537 BTC for 4929 total profiting 4746. Adjustment 0>
<Sold 0.00100960 BTC for 14 total profiting 13. Adjustment 0>
<Sold 0.50000000 BTC for 7032 total profiting 6775. Adjustment 0>
<Sold 0.03500000 BTC for 496 total profiting 478. Adjustment 0>
<Sold 0.03518002 BTC for 498 total profiting 480. Adjustment 0>
<Sold 0.03447186 BTC for 488 total profiting 470. Adjustment 0>
<Sold 0.01057786 BTC for 150 total profiting 145. Adjustment 0>
<Sold 0.03500000 BTC for 496 total profiting 478. Adjustment 0>

total gain or loss for above transactions: 15243

total basis for above transactions: 1400
total proceeds for above transactions: 16643
```

An adhoc CSV format is supported for non-exchange transactions like mining and purchases.

yabc also includes a set of HTTP endpoints that allow for storing data more
permanently in a database, sqlite by default. Postgres as a backend is also supported.

# TODO

- [ ] TODO: Support coin/coin trades like BTC/ETH.
- [ ] TODO: Enable importing from more exchanges (binance)
- [ ] TODO: Add better historical price lookup support; it is now a stub that returns $17

# Installation, with virtualenv
```
git clone git@github.com:robertkarl/yabc.git
cd yabc
virtualenv -p python3 venv
. venv/bin/activate
python setup.py install
```

# Notes
File structure and setup.py usage inspired by source and test layout of python modules
[sshuttle](https://github.com/sshuttle/sshuttle) and
[flask](https://github.com/pallets/flask).

# Caveats
Please note that yabc is not a tax service or tax accounting software and is
provided with no warranty. Please see the LICENSE file for more details.

yabc is not associated with any of the mentioned exchanges or companies
including but not limited to binance, coinbase, or gemini. Any trademarks are
property of their respective owners.
