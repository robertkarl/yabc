[![yabc on PyPI](https://img.shields.io/pypi/v/yabc.svg)](https://pypi.org/project/yabc/)
![MIT License badge](https://img.shields.io/badge/license-MIT-green.svg)
[![yabc on TravisCI](https://travis-ci.org/robertkarl/yabc.svg?branch=master)](https://travis-ci.org/robertkarl/yabc)
![Supported Python versions](https://img.shields.io/pypi/pyversions/yabc.svg)

# yabc - a bitcoin tax calculator
yabc translates cryptocurrency trades, mining, and spending data into a list of
reports that can be sent to tax authorities. It is most useful for
cryptocurrency traders in the US.

yabc is the tax calculator behind [https://CostBasis.Report/](https://costbasis.report/).

```
13 transactions to be reported

<Sold 0.76 BTC on 2008-04-21 01:12:00 for $236. Exchange: coinbase. Profit:$-155.
	<TX 2008-04-21 01:12:00 SELL 1993.93 USD for 6.26 BTC, from exchange coinbase. Fee 48.44 USD>>
<Sold 1 BTC on 2008-04-21 01:12:00 for $311. Exchange: coinbase. Profit:$29.
	<TX 2008-04-21 01:12:00 SELL 1993.93 USD for 6.26 BTC, from exchange coinbase. Fee 48.44 USD>>
<Sold 2 BTC on 2008-04-21 01:12:00 for $622. Exchange: coinbase. Profit:$546.
	<TX 2008-04-21 01:12:00 SELL 1993.93 USD for 6.26 BTC, from exchange coinbase. Fee 48.44 USD>>
<Sold 2.5 BTC on 2008-04-21 01:12:00 for $777. Exchange: coinbase. Profit:$666.
	<TX 2008-04-21 01:12:00 SELL 1993.93 USD for 6.26 BTC, from exchange coinbase. Fee 48.44 USD>>
<Sold 0.04290503 BTC on 2008-08-13 06:27:56.145000 for $594. Exchange: gemini. Profit:$572.
	<TX 2008-08-13 06:27:56.145000 SELL 595.36 USD for 0.04290503 BTC, from exchange gemini. Fee 1.49 USD>>
<Sold 0.35608537 BTC on 2008-08-14 06:27:56.146000 for $4929. Exchange: gemini. Profit:$4746.
	<TX 2008-08-14 06:27:56.146000 SELL 4941.11 USD for 0.35608537 BTC, from exchange gemini. Fee 12.35 USD>>
<Sold 0.0010096 BTC on 2008-08-15 06:27:56.147000 for $14. Exchange: gemini. Profit:$13.
	<TX 2008-08-15 06:27:56.147000 SELL 14.01 USD for 0.0010096 BTC, from exchange gemini. Fee 0.04 USD>>
<Sold 0.5 BTC on 2008-08-18 06:27:56.150000 for $7032. Exchange: gemini. Profit:$6775. Long term.
	<TX 2008-08-18 06:27:56.150000 SELL 7050.00 USD for 0.5 BTC, from exchange gemini. Fee 17.63 USD>>
<Sold 0.035 BTC on 2008-08-20 06:27:56.152000 for $496. Exchange: gemini. Profit:$478. Long term.
	<TX 2008-08-20 06:27:56.152000 SELL 497.44 USD for 0.035 BTC, from exchange gemini. Fee 1.24 USD>>
<Sold 0.03518002 BTC on 2008-08-21 06:27:56.153000 for $498. Exchange: gemini. Profit:$480. Long term.
	<TX 2008-08-21 06:27:56.153000 SELL 499.51 USD for 0.03518002 BTC, from exchange gemini. Fee 1.25 USD>>
<Sold 0.03447186 BTC on 2008-08-22 06:27:56.154000 for $488. Exchange: gemini. Profit:$470. Long term.
	<TX 2008-08-22 06:27:56.154000 SELL 489.45 USD for 0.03447186 BTC, from exchange gemini. Fee 1.22 USD>>
<Sold 0.01057786 BTC on 2008-08-23 06:27:56.155000 for $150. Exchange: gemini. Profit:$145. Long term.
	<TX 2008-08-23 06:27:56.155000 SELL 150.19 USD for 0.01057786 BTC, from exchange gemini. Fee 0.38 USD>>
<Sold 0.035 BTC on 2009-08-24 06:27:56.156000 for $496. Exchange: gemini. Profit:$478. Long term.
	<TX 2009-08-24 06:27:56.156000 SELL 496.95 USD for 0.035 BTC, from exchange gemini. Fee 1.24 USD>>

total gain or loss for above transactions: 15243

total basis for above transactions: 1400
total proceeds for above transactions: 16643
Remaining coins after sales: <yabc.coinpool.CoinPool object at 0x7efc4b9003c8>
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
