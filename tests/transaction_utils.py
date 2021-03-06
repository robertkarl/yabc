#  Copyright (c) 2019. Robert Karl. All rights reserved.
#  Licensed under the MIT License. See LICENSE in the project root for license information.
import datetime

import yabc
from yabc import transaction
from yabc.transaction import Transaction


def make_buy(
    quantity=1,
    fees=0,
    subtotal=10000,
    date=datetime.datetime(2015, 2, 5, 6, 27, 56, 373000),
    symbol="BTC",
):
    """
    Convenience method for creating valid transaction objects; used in tests only.

    Without any parameters passed, creates a 1 BTC buy for 10,000 USD in 2015. Not a great deal then.
    """
    return Transaction(
        operation=yabc.transaction.Operation.BUY,
        symbol_received=symbol,
        quantity_received=quantity,
        symbol_traded="USD",
        quantity_traded=subtotal,
        date=date,
        fees=fees,
        fee_symbol="USD",
    )


def make_sale(
    quantity=1,
    fees=0,
    subtotal=10000,
    date=datetime.datetime(2015, 2, 5, 6, 27, 56, 373000),
    symbol="BTC",
):
    """
    Without any parameters passed, creates a 1 BTC sell for 10,000 USD in 2015.

    A sweet trade then.

    Used in tests only.
    """
    return Transaction(
        operation=yabc.transaction.Operation.SELL,
        symbol_received="USD",
        quantity_received=subtotal,
        symbol_traded=symbol,
        quantity_traded=quantity,
        date=date,
        fees=fees,
        fee_symbol="USD",
    )


def make_transaction(
    kind: Transaction.Operation = Transaction.Operation.BUY,
    quantity=1,
    fees=0,
    subtotal=10000,
    date=datetime.datetime(2015, 2, 5, 6, 27, 56, 373000),
    asset_name="BTC",
):
    """
    Convenience method for creating valid transaction objects; used in tests only.
    """
    if kind == transaction.Operation.BUY:
        return make_buy(quantity, fees, subtotal, date, asset_name)
    elif kind == transaction.Operation.SELL:
        return make_sale(quantity, fees, subtotal, date, asset_name)
    else:
        raise RuntimeError("Make a Transaction object please")
