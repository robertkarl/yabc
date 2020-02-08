"""
Script used to convert values from the old Coinbase output format
to the new (as of February 2020) format.

Used by RK at least once. ymmv
"""
import csv
import sys
fields="Timestamp,Transaction Type,Asset,Quantity Transacted,USD Spot Price at Transaction,USD Amount Transacted (Inclusive of Coinbase Fees),Address,Notes".split(',')
outfields = "Timestamp,Transaction Type,Asset,Quantity Transacted,USD Spot Price at Transaction,Subtotal,Total (inclusive of fees),Notes".split(',')
r = csv.DictReader(open(sys.argv[1], 'r'), fieldnames=fields)
w = csv.DictWriter(open(sys.argv[2], 'w'), fieldnames=outfields)
SUBTOTAL = 'Subtotal'
TOTAL_OUT ='Total (inclusive of fees)'
for tx in r:
    old = tx['USD Amount Transacted (Inclusive of Coinbase Fees)']
    tx['Total (inclusive of fees)'] = "{} USD".format(old)
    tx['Subtotal'] = "0 USD"
    if tx['Transaction Type'] in { 'Receive', 'Send'}:
        tx[SUBTOTAL] = ""
        tx[TOTAL_OUT] = ""
    del tx['Address']
    del tx['USD Amount Transacted (Inclusive of Coinbase Fees)']
    w.writerow(tx)

