# Adhoc Transaction Format
## Dates
Dates should be in YYYY/MM/DD format.

## File format
Adhoc transactions are defined in a CSV file. You can start with a copy of [this one](./adhoc.csv)
It is recommended that the CSV file is edited with a program like Excel or Google Sheets before use with yabc or [costbasis.io](https://costbasis.io).

## Number formatting
All values should be positive in your adhoc transaction sheet.

Use US-style formatting, with a period `.` for delineating dollars and cents: $10,000.00.
10,000 or 10000 are also accepted.

## Supported types:
1) Mining
    - for mining, the TradedCurrency and TradedAmount fields should be blank
2) Trading 
    - This can be selling coins to receive USD, buying crypto with dollars, or trading crypto for crypto.
    - For a coin/coin trade, for example trading ether for bitcoin, use a sell.
3) Spending
    - ReceivedCurrency and ReceivedAmount can optionally hold the USD value of the purchased goods.
    - Example:`USD,3000,2018/3/4,Spending,1,BTC` indicates selling 1 BTC for $3000 worth of goods.
4) Gift received
    - For gifts received, you can place the cost basis in the Traded fields. For example:
      `BTC,3,2018/3/4,GiftReceived,750,USD` indicates  receiving 3 bitcoin which were purchased for $750.
5) Gift sent
     - Not usually taxable in the US, unless the value is over $15,000 or under other rare conditions.
       Traded* columns are ignored.
