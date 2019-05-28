import csv
import decimal
import subprocess
import io

from fdfgen import forge_fdf

def round_to_dollar_str(dec):
    """
    Convert an arbitrary precision decimal object to a string roudned to the NEAREST dollar.
    >>> round_to_dollar_str(decimal.Decimal("1.500001"))
    '2.'
    >>> round_to_dollar_str(decimal.Decimal("1.499999"))
    '1.'
    >>> round_to_dollar_str(decimal.Decimal("-1.499999"))
    '-1.'
    """
    return "{:.0f}.".format(dec.quantize(1))




class PdfFiller():

    def __init__(self):
        pass

    def pairs_for_report(self, report, row):
        """
        Return list of (key, value) pairs.
        """
        prefix = 'topmostSubform[0].Page1[0].Table_Line1[0].Row{}[0].f1_{}[0]'
        key_functions = [
                lambda report: report.description(),
                lambda report: report.date_purchased.date().isoformat(),
                lambda report: report.date_sold.date().isoformat(),
                lambda report: round_to_dollar_str(report.proceeds),
                lambda report: round_to_dollar_str(report.basis),
                lambda report: "",
                lambda report: "",
                lambda report: round_to_dollar_str(report.gain_or_loss)
                ]
        start = 3
        ans = []
        for i, f in enumerate(key_functions):
            field_index = start + (row - 1) * 8 + i
            ans.append((prefix.format(row, field_index), f(report)))
        print(ans)
        return ans


    def fill(self, reports):
        pairs = []
        for index, r in enumerate(reports[:10]):
            prefix = 'topmostSubform[0].Page1[0].Table_Line1[0].Row1[0].f1_{}[0]'
            pairs.extend(self.pairs_for_report(r, index))
        fdf = forge_fdf("",pairs,[],[],[])
        with open("data.fdf", "wb") as fdf_file:
            fdf_file.write(fdf)
        subprocess.call('pdftk /home/rk/code/yabc/2018-8949.pdf fill_form /home/rk/code/yabc/data.fdf output filled.8949.pdf flatten'.split())

