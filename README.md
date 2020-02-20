[![yabc on PyPI](https://img.shields.io/pypi/v/yabc.svg)](https://pypi.org/project/yabc/)
![MIT License badge](https://img.shields.io/badge/license-MIT-green.svg)
[![yabc on TravisCI](https://travis-ci.org/robertkarl/yabc.svg?branch=master)](https://travis-ci.org/robertkarl/yabc)
![Supported Python versions](https://img.shields.io/pypi/pyversions/yabc.svg)

# yabc - a bitcoin tax calculator
yabc translates cryptocurrency trades, mining, and spending data into a list of
reports that can be sent to tax authorities. It is most useful for
cryptocurrency traders in the US.

yabc is the tax calculator behind [https://velvetax.com/](https://velvetax.com/).

```
python -m yabc testdata/gemini/sample_gemini.xlsx ./testdata/coinbase/sample_coinbase.csv
<CostBasisReport: Sold 0.76 BTC on 2008-04-21 01:12:00 for $236. Exchange: coinbase. Profit:$-155.
	<TX 2008-04-21 01:12:00 SELL 1993.93 USD for 6.26 BTC, from exchange coinbase. Fee 48.44 USD>>
<CostBasisReport: Sold 1 BTC on 2008-04-21 01:12:00 for $311. Exchange: coinbase. Profit:$29.
	<TX 2008-04-21 01:12:00 SELL 1993.93 USD for 6.26 BTC, from exchange coinbase. Fee 48.44 USD>>
<CostBasisReport: Sold 2 BTC on 2008-04-21 01:12:00 for $622. Exchange: coinbase. Profit:$546.
	<TX 2008-04-21 01:12:00 SELL 1993.93 USD for 6.26 BTC, from exchange coinbase. Fee 48.44 USD>>
<CostBasisReport: Sold 2.5 BTC on 2008-04-21 01:12:00 for $777. Exchange: coinbase. Profit:$666.
	<TX 2008-04-21 01:12:00 SELL 1993.93 USD for 6.26 BTC, from exchange coinbase. Fee 48.44 USD>>
<CostBasisReport: Sold 0.07453875 BTC on 2017-12-01 20:14:32.284003 for $786. Exchange: gemini. Profit:$748. Long term.
	<TX 2017-12-01 20:14:32.284003 SELL 788.39635875 USD for 0.07453875 BTC, from exchange gemini. Fee 1.970990896875 USD>>
<CostBasisReport: Sold 0.0429050269 BTC on 2017-12-24 23:04:26.829998 for $594. Exchange: gemini. Profit:$572. Long term.
	<TX 2017-12-24 23:04:26.829998 SELL 595.35873426978 USD for 0.0429050269 BTC, from exchange gemini. Fee 1.48839683567445 USD>>
<CostBasisReport: Sold 0.35608537 BTC on 2017-12-24 23:04:27.855999 for $4929. Exchange: gemini. Profit:$4746. Long term.
	<TX 2017-12-24 23:04:27.855999 SELL 4941.111811194 USD for 0.35608537 BTC, from exchange gemini. Fee 12.352779527985 USD>>
<CostBasisReport: Sold 0.0010096031 BTC on 2017-12-24 23:04:33.120005 for $14. Exchange: gemini. Profit:$13. Long term.
	<TX 2017-12-24 23:04:33.120005 SELL 14.00945453622 USD for 0.0010096031 BTC, from exchange gemini. Fee 0.03502363634055 USD>>
<CostBasisReport: Sold 0.5 BTC on 2017-12-24 23:56:38.505998 for $7032. Exchange: gemini. Profit:$6775. Long term.
	<TX 2017-12-24 23:56:38.505998 SELL 7049.995 USD for 0.5 BTC, from exchange gemini. Fee 17.6249875 USD>>
<CostBasisReport: Sold 0.035 BTC on 2018-01-14 02:30:07.163003 for $496. Exchange: gemini. Profit:$478. Long term.
	<TX 2018-01-14 02:30:07.163003 SELL 497.441 USD for 0.035 BTC, from exchange gemini. Fee 1.2436025 USD>>
<CostBasisReport: Sold 0.03518002 BTC on 2018-01-14 02:30:08.652997 for $498. Exchange: gemini. Profit:$480. Long term.
	<TX 2018-01-14 02:30:08.652997 SELL 499.5080873726 USD for 0.03518002 BTC, from exchange gemini. Fee 1.2487702184315 USD>>
<CostBasisReport: Sold 0.03447186 BTC on 2018-01-14 02:30:10.102003 for $488. Exchange: gemini. Profit:$470. Long term.
	<TX 2018-01-14 02:30:10.102003 SELL 489.4531855518 USD for 0.03447186 BTC, from exchange gemini. Fee 1.2236329638795 USD>>
<CostBasisReport: Sold 0.01057786 BTC on 2018-01-14 02:30:10.911001 for $150. Exchange: gemini. Profit:$145. Long term.
	<TX 2018-01-14 02:30:10.911001 SELL 150.1911203318 USD for 0.01057786 BTC, from exchange gemini. Fee 0.3754778008295 USD>>
<CostBasisReport: Sold 0.035 BTC on 2018-01-14 02:30:11.599998 for $496. Exchange: gemini. Profit:$478. Long term.
	<TX 2018-01-14 02:30:11.599998 SELL 496.95205 USD for 0.035 BTC, from exchange gemini. Fee 1.242380125 USD>>

total gain or loss for above transactions: 15991

total basis for above transactions: 1438
total proceeds for above transactions: 17429
Remaining coins after sales:
<TX 2007-08-18 01:12:00 BUY 4 BTC for 2048 USD, from exchange coinbase. Fee 11.11 USD>
<TX 2007-08-31 01:12:00 BUY 4 BTC for 97 USD, from exchange coinbase. Fee 11.12 USD>
<TX 2007-09-13 01:12:00 BUY 7 BTC for 102.34 USD, from exchange coinbase. Fee 14.98 USD>
<TX 2007-10-22 01:12:00 BUY 4 BTC for 45.6 USD, from exchange coinbase. Fee 31.9 USD>
<TX 2007-12-13 01:12:00 BUY 8 BTC for 13.2 USD, from exchange coinbase. Fee 32.25 USD>
<TX 2007-12-26 01:12:00 BUY 3 BTC for 98.04 USD, from exchange coinbase. Fee 9.54 USD>
<TX 2008-02-03 01:12:00 BUY 10.23 BTC for 203 USD, from exchange coinbase. Fee 92.2 USD>
<TX 2008-03-13 01:12:00 BUY 5.234 BTC for 302 USD, from exchange coinbase. Fee 30.4 USD>
<TX 2008-04-08 01:12:00 BUY 2.532 BTC for 1776.76 USD, from exchange coinbase. Fee 17.56 USD>
<TX 2015-10-16 06:27:56.139998 BUY 20.2092 BTC for 53.624236 USD, from exchange gemini. Fee 0.13406059 USD>
<TX 2015-10-16 06:27:56.373002 BUY 0.339 BTC for 86.89587 USD, from exchange gemini. Fee 0.217239675 USD>
<TX 2015-10-16 06:28:09.103999 BUY 0.323 BTC for 82.79459 USD, from exchange gemini. Fee 0.206986475 USD>
<TX 2015-10-16 06:28:09.735004 BUY 0.10020404 BTC for 25.6853015732 USD, from exchange gemini. Fee 0.064213253933 USD>
```

An adhoc CSV format is supported for non-exchange transactions like mining, gifts, and purchases.

yabc also includes a set of HTTP endpoints that allow for storing data more
permanently in a database, sqlite by default. Postgres as a backend is also supported.

# TODO

- [ ] TODO: Support coin/coin trades like BTC/ETH.
- [ ] TODO: Enable importing from more exchanges (binance)
- [ ] TODO: Add better historical price lookup support; it is now a stub.

# Installation from source, with virtualenv
```
git clone git@github.com:robertkarl/yabc.git
cd yabc
virtualenv -p python3 venv
. venv/bin/activate
python setup.py install
```

# Notes
File structure, setup.py usage, and shields inspired by source of python
modules [sshuttle](https://github.com/sshuttle/sshuttle),
[flask](https://github.com/pallets/flask), and
[black](https://github.com/psf/black/blob/master/README.md).

# Caveats
Please note that yabc is not a tax service or tax accounting software and is
provided with no warranty. Please see the LICENSE file for more details.

yabc is not associated with any of the mentioned exchanges or companies
including but not limited to binance, coinbase, or gemini. Any trademarks are
property of their respective owners.
14 transactions to be reported

