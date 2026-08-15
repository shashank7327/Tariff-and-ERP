"""Check that every number printed in the report is the number the data produces.

I recompute each series from source, pull every plotting coordinate out of the
LaTeX, and ask of each one: is this a correct rounding of the computed value *at
the precision it is printed*? Then I re-check the statistics quoted in prose.

Testing "is this a correct rounding" rather than equality against a re-rounded
value matters: Python's round() is banker's rounding and will report false
positives if you use it naively.

On its first run this caught four errors that had survived several drafts -- three
plotted points rounded twice, and an amplification factor computed from a rounded
input share. None changed an argument; none would have been found by reading.

    python src/verify_figures.py        # exit status 0 if everything passes

Keep SERIES in step with the figures. The checker matches each computed series
against the coordinate block that plots it, so a series that is no longer plotted
gets matched against the wrong block and reported as a spurious mismatch.
"""
import re
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
import asi_data as A
from paths import TEX

SECTION = TEX / 'asi_section_downstream.tex'
TOL_EPS = 1e-9

up = A.block(A.UPSTREAM)
dn = A.block(A.DOWNSTREAM)
cls = {c: A.block([c]) for c in ['2420', '2432', '2511', '2599']}
lam = A.labour_intensity(up, dn)
Y, C = A.YEARS, A.CLEAN

SERIES = {
    'Fig 4.1  GVA index, upstream':         (A.index_100(up, 'gva_cr'), Y),
    'Fig 4.1  GVA index, downstream':       (A.index_100(dn, 'gva_cr'), Y),
    'Fig 4.2  Labour-intensity ratio':      (lam, C),
    'Fig 4.3  Wage share, upstream':        (up['wage_share'], C),
    'Fig 4.3  Wage share, downstream':      (dn['wage_share'], C),
    'Fig 4.4  GVA index, NIC 2420':         (A.index_100(cls['2420'], 'gva_cr'), C),
    'Fig 4.4  GVA index, NIC 2432':         (A.index_100(cls['2432'], 'gva_cr'), C),
    'Fig 4.4  GVA index, NIC 2511':         (A.index_100(cls['2511'], 'gva_cr'), C),
    'Fig 4.4  GVA index, NIC 2599':         (A.index_100(cls['2599'], 'gva_cr'), C),
    'Fig 4.5  Contract share, upstream':    (up['contract_share'], C),
    'Fig 4.5  Contract share, downstream':  (dn['contract_share'], C),
    'Fig 4.6  Employment yield, upstream':  (up['pe_per_cr_tax'], C),
    'Fig 4.6  Employment yield, downstream': (dn['pe_per_cr_tax'], C),
}


def parse_blocks(tex):
    """Every \\addplot coordinate block, keeping the precision each value is printed at."""
    blocks = []
    for blk in re.findall(r'coordinates\s*\{((?:\s*\([^)]*\)(?:\[[^\]]*\])?)+)\s*\}', tex):
        d = {}
        for x, y in re.findall(r'\(([^,]+),([^)]+)\)', blk):
            y = y.strip()
            try:
                d[x.strip()] = (float(y), len(y.split('.')[1]) if '.' in y else 0)
            except ValueError:
                pass
        if len(d) >= 2:
            blocks.append(d)
    return blocks


def rounds_to(computed, printed, dp):
    return abs(computed - printed) <= 0.5 * 10 ** (-dp) + TOL_EPS


def main():
    tex = SECTION.read_text(encoding='utf-8')
    blocks = parse_blocks(tex)
    print(f'parsed {len(blocks)} coordinate blocks from {SECTION.name}\n')

    problems = 0
    width = max(len(k) for k in SERIES)
    points = 0

    for name, (series, years) in SERIES.items():
        want = {y[2:]: float(series[y]) for y in years}
        best, errs = None, None
        for d in blocks:
            if set(want) - set(d):
                continue
            e = [(k, want[k], d[k][0], d[k][1]) for k in want
                 if not rounds_to(want[k], d[k][0], d[k][1])]
            if best is None or len(e) < len(errs):
                best, errs = d, e
            if not e:
                break
        if best is None:
            print(f'  {name:<{width}}   NOT FOUND in the figure source')
            problems += 1
        elif errs:
            print(f'  {name:<{width}}   {len(errs)} point(s) mis-rounded:')
            for k, c, p, dp in errs:
                print(f'        {k:<6} computed {c:10.4f}  plotted {p:.{dp}f}')
            problems += len(errs)
        else:
            print(f'  {name:<{width}}   ok  ({len(want)} points)')
            points += len(want)

    y = '2022-23'
    quoted = [
        ('labour-intensity ratio', lam[y], 3.14, 2),
        ('median of the ratio', float(np.median([lam[t] for t in C])), 3.93, 2),
        ('minimum of the ratio', float(min(lam[t] for t in C)), 3.08, 2),
        ('maximum of the ratio', float(max(lam[t] for t in C)), 6.18, 2),
        ('wage share, downstream', dn.loc[y, 'wage_share'], 38.4, 1),
        ('wage share, upstream', up.loc[y, 'wage_share'], 17.6, 1),
        ('employment yield, downstream', dn.loc[y, 'pe_per_cr_tax'], 151, 0),
        ('employment yield, upstream', up.loc[y, 'pe_per_cr_tax'], 39, 0),
        ('input share, downstream', dn.loc[y, 'input_share'], 83.1, 1),
        ('input share, upstream', up.loc[y, 'input_share'], 88.8, 1),
        ('contract share, upstream', up.loc[y, 'contract_share'], 54.1, 1),
        ('contract share, downstream', dn.loc[y, 'contract_share'], 40.9, 1),
        ('persons engaged, downstream', dn.loc[y, 'pe'], 523899, 0),
        ('persons engaged, upstream', up.loc[y, 'pe'], 170871, 0),
        ('GVA downstream, INR crore', dn.loc[y, 'gva_cr'], 41653, 0),
        ('GVA upstream, INR crore', up.loc[y, 'gva_cr'], 42662, 0),
        ('estimated tax, downstream', dn.loc[y, 'tax_cr'], 3473, 0),
        ('estimated tax, upstream', up.loc[y, 'tax_cr'], 4411, 0),
        ('GVA growth, upstream %', 100 * (up.loc[y, 'gva_cr'] / up.loc['2011-12', 'gva_cr'] - 1), 138.4, 1),
        ('GVA growth, downstream %', 100 * (dn.loc[y, 'gva_cr'] / dn.loc['2011-12', 'gva_cr'] - 1), 114.5, 1),
        ('contract growth, upstream %', 100 * (up.loc[y, 'contract'] / up.loc['2011-12', 'contract'] - 1), 100.0, 1),
        ('contract growth, downstream %', 100 * (dn.loc[y, 'contract'] / dn.loc['2011-12', 'contract'] - 1), 9.0, 1),
    ]
    b = A.apportionment_bounds()
    derived = [
        ('volatility, upstream', A.volatility(up), 0.373, 3),
        ('volatility, downstream', A.volatility(dn), 0.105, 3),
        ('volatility ratio', A.volatility(up) / A.volatility(dn), 3.6, 1),
        ('amplification m/(1-m)', A.amplification(), 4.91, 2),
        ('apportionment lower bound', b['lower'], 3.01, 2),
        ('apportionment upper bound', b['upper'], 3.38, 2),
        ('wage-share multiple', dn.loc[y, 'wage_share'] / up.loc[y, 'wage_share'], 2.18, 2),
        ('yield multiple', dn.loc[y, 'pe_per_cr_tax'] / up.loc[y, 'pe_per_cr_tax'], 3.89, 2),
    ]

    for heading, group in [('quoted in the text', quoted), ('derived statistics', derived)]:
        print(f'\n{heading} (checked at the precision quoted):')
        for label, got, said, dp in group:
            ok = rounds_to(got, said, dp)
            problems += 0 if ok else 1
            print(f'  {label:<30} computed {got:12.4f}   text {said:>10}   '
                  f'{"ok" if ok else "*** MISMATCH"}')

    n = len(quoted) + len(derived)
    print()
    if problems:
        print(f'{problems} PROBLEM(S) FOUND')
        return 1
    print(f'ALL CHECKS PASS across {points} plotted points and {n} quoted statistics')
    return 0


if __name__ == '__main__':
    sys.exit(main())
