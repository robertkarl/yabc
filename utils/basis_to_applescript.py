"""
Given coinbase and gemini transaction histories, fill out IRS form 8949.

Warning: instead of programmatically generating PDFs, this script uses
applescript to populate PDFs from Preview.app in OS X. Your mileage may vary.

TODO: Generate the 8949 content programmatically and emit a PDF.

Requirements:
    - Coinbase tx history in CSV form
    - Gemini tx history in CSV form
    - OS X
    - Python and yabc library 0.0.2+

Usage / workflow:
    - Create and activate a virtualenv. Install yabc.

            virtualenv -p python3.5 venv
            source venv/bin/activate
            python setup.py install

    - Run this script, passing in the locations of cb and gemini files

        python3 basis_to_applescript.py --coinbase cb.csv --gemini gems.csv

    - This script emits applescript to the current directory.
    - For each applescript file emitted
        - open a fresh copy of form 8949 in Preview.app
        - Run the generated applescript file with osascript

            osascript 'populate_8949-1.script'

        - Watch as applescript populates the PDF with your cost basis info.

Each 8949 form holds 14 entries only. This python script emits multiple
applescripts, each of which can fill a PDF with 14 transactions.

TODO: Don't require both a coinbase and a gemini file.
"""

__author__ = "Robert Karl <robertkarljr@gmail.com>"

import argparse

from yabc import basis


NUM_ENTRIES_IN_8949 = 14
TAX_YEAR = "2018"
GENERATED_FNAME_FMT = "populate_8949-{}.script"
REPORT_FNAME_FMT = "report-{}.txt"


def append_tab(strokes):
    strokes.append("    keystroke tab")


def append_string_as_keystroke(strokes, string):
    strokes.append('    keystroke "{}"'.format(string))


def get_strokes(txs):
    """
    Get the applescript lines needed to enter this transaction into a PDF and
    leave the cursor on the first entry of the next line.
    """
    total_proceeds = sum([tx.proceeds for tx in txs])
    total_basis = sum([tx.basis for tx in txs])
    total_gain_or_loss = sum([tx.gain_or_loss for tx in txs])
    applescript_keystroke_lines = []
    for tx in txs:
        """
        CostBasisReport(descr='1.500 BTC', date_acquired='12-11-2015',
        date_sold='01-14-2018', proceeds=21017, basis=650, gain_or_loss=20367)
        """
        append_string_as_keystroke(applescript_keystroke_lines, tx.descr)
        append_tab(applescript_keystroke_lines)
        append_string_as_keystroke(applescript_keystroke_lines, tx.date_acquired)
        append_tab(applescript_keystroke_lines)
        append_string_as_keystroke(applescript_keystroke_lines, tx.date_sold)
        append_tab(applescript_keystroke_lines)
        append_string_as_keystroke(applescript_keystroke_lines, tx.proceeds)
        append_tab(applescript_keystroke_lines)
        append_string_as_keystroke(applescript_keystroke_lines, tx.basis)
        append_tab(applescript_keystroke_lines)
        append_tab(applescript_keystroke_lines)
        append_tab(applescript_keystroke_lines)
        append_string_as_keystroke(applescript_keystroke_lines, tx.gain_or_loss)
        append_tab(applescript_keystroke_lines)
    applescript_keystroke_lines.append("-- Starting totals section")
    append_string_as_keystroke(applescript_keystroke_lines, total_proceeds)
    append_tab(applescript_keystroke_lines)
    append_string_as_keystroke(applescript_keystroke_lines, total_basis)
    append_tab(applescript_keystroke_lines)
    append_tab(applescript_keystroke_lines)
    append_string_as_keystroke(applescript_keystroke_lines, total_gain_or_loss)
    return applescript_keystroke_lines


def get_preamble():
    return """tell application "System Events"
	delay 0.5
	keystroke space using command down
	delay 0.5
	keystroke "Preview"
	delay 0.5
	keystroke return
	delay 0.5
	keystroke "d" using command down
	delay 0.5
	keystroke space
	delay 9""".split(
        "\n"
    )


def get_suffix():
    return ["end tell"]


def human_readable_report(txs):
    """
    Given a list of CostBasisReports to be submitted to tax authorities, generate a human
    readable report.
    """
    total_proceeds = sum([tx.proceeds for tx in txs])
    total_basis = sum([tx.basis for tx in txs])
    total_gain_or_loss = sum([tx.gain_or_loss for tx in txs])
    ans = ""
    ans += "{} transactions for ty {}\n\n".format(len(txs), TAX_YEAR)
    for i in txs:
        ans += "{}\n".format(str(i))
    ans += "\ntotal gain or loss for above transactions: {}".format(total_gain_or_loss)
    ans += "\n"
    ans += "\ntotal basis for above transactions: {}".format(total_basis)
    ans += "\ntotal proceeds for above transactions: {}".format(total_proceeds)
    return ans


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--coinbase", type=str, required=True)
    parser.add_argument("--gemini", type=str, required=True)
    args = parser.parse_args()

    txs = basis.process_all(basis.get_all_transactions(args.coinbase, args.gemini))
    txs = list(filter(lambda x: TAX_YEAR in x.date_sold, txs))
    print("Found {} matching transactions for tax year {}".format(len(txs), TAX_YEAR))
    for i in txs:
        print(i)

    i = 0
    batch = []
    while txs:
        batch = []
        while txs and len(batch) < NUM_ENTRIES_IN_8949:
            batch.append(txs.pop(0))
        with open(GENERATED_FNAME_FMT.format(i), "w") as of:
            of.write("-- Applescript for filling form 8949\n")
            of.write("-- usage: osascript {} \n".format(GENERATED_FNAME_FMT.format(i)))
            of.writelines([i + "\n" for i in get_preamble()])
            of.writelines([i + "\n" for i in get_strokes(batch)])
            of.writelines([i + "\n" for i in get_suffix()])
        with open(REPORT_FNAME_FMT.format(i), "w") as of:
            of.write(human_readable_report(batch))
        i += 1
