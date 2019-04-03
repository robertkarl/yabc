"""
Usage: python3 basis_to_applescript.py --coinbase cb.csv --gemini gems.csv

Used to generate applescript, which generates form 8949.

Each 8949 form holds 14 entries only.

YMMV with use as this is clumsy with many transactions and requires OS X.

TODO: Generate the 8949 content programmatically and emit a PDF.

"""

__author__ = "Robert Karl <robertkarljr@gmail.com>"

import argparse

from yabc import basis


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


NUM_ENTRIES_IN_8949 = 14
TAX_YEAR = "2018"

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--coinbase", type=str, required=True)
    parser.add_argument("--gemini", type=str, required=True)
    args = parser.parse_args()

    txs = basis.process_all(basis.get_all_transactions(args.coinbase, args.gemini))
    txs = list(filter(lambda x: TAX_YEAR in x.date_sold, txs))

    i = 0
    batch = []
    while txs:
        batch = []
        while txs and len(batch) < NUM_ENTRIES_IN_8949:
            batch.append(txs.pop(0))
        with open("populate_8949-{}.script".format(i), "w") as of:
            of.writelines([i + "\n" for i in get_preamble()])
            of.writelines([i + "\n" for i in get_strokes(batch)])
            of.writelines([i + "\n" for i in get_suffix()])
        i += 1
