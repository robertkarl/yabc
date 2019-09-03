#  Copyright (c) 2019. Seattle Blockchain Solutions. All rights reserved.
#  Licensed under the MIT License. See LICENSE in the project root for license information.
from yabc.transaction import Transaction
import datetime
import yabc

def make_buy(
        quantity=1,
        fees=0,
        subtotal=10000,
        date=datetime.datetime(2015, 2, 5, 6, 27, 56, 373000),
        symbol="BTC",
):
    """
    Convenience method for creating valid transaction objects; used in tests only.

    Without any parameters passed, creates a 1 BTC buy for 10,000 USD

    TODO: Remove from here and add to tests if not used in the codebase.
    """
    return Transaction(
        operation=yabc.transaction.Operation.BUY,
        symbol_received=symbol,
        quantity_received=quantity,
        symbol_traded="USD",
        quantity_traded=subtotal,
        date=date,
        fees=fees,
        fee_symbol="USD"
    )

