#  Copyright (c) 2019. Seattle Blockchain Solutions. All rights reserved.
#  Licensed under the MIT License. See LICENSE in the project root for license information.
import datetime

import yabc
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
    Convenience method for creating valid transaction objects; used in tests only.

    Without any parameters passed, creates a 1 BTC buy for 10,000 USD in 2015. Not a great deal then.
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

    Without any parameters passed, creates a 1 BTC buy for 10,000 USD

    TODO: Remove from here and add to tests if not used in the codebase.
    """
    return Transaction(
        operation=kind,
        asset_name=asset_name,
        date=date,
        fees=fees,
        quantity=quantity,
        usd_subtotal=subtotal,
    )
