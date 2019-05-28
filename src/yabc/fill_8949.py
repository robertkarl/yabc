import csv
import subprocess
import io

from fdfgen import forge_fdf

class PdfFiller()
    _2018_rows = ['descr', 'acquired', 'sold', 'proceeds', 'basis', 'code', 'adjustment', 'gain_or_loss']

    def __init__(self):
        pass

    def pairs_for_report(self, report):
        """
        Return list of (key, value) pairs.
        """
        ans = []
        prefix = 'topmostSubform[0].Page1[0].Table_Line1[0].Row1[0].f1_{}[0]'
        curr = 3
        ans.append((report.description())
        curr += 1


    def fill(self, reports):
        of = io.StringIO()
        writer = csv.writer(of)
        names = CostBasisReport.field_names()
        writer.writerow(names)
        pairs = []
        for r in reports[:1]:
            prefix = 'topmostSubform[0].Page1[0].Table_Line1[0].Row1[0].f1_{}[0]'
            for index, field in enumerate(r.fields()):
                pairs.append((prefix.format(3 + index), field))
        fdf = forge_fdf("",pairs,[],[],[])
        with open("data.fdf", "wb") as fdf_file:
            fdf_file.write(fdf)
        subprocess.call('pdftk /home/rk/code/yabc/2018-8949.pdf fill_form /home/rk/code/yabc/data.fdf output filled.8949.pdf flatten'.split())


