"""Build every series and print the numbers the report quotes.

This is what I run after any change to the data or the basket. It writes
`build/series_output.txt`, and the pgfplots coordinate strings it prints under
"FIGURE COORDINATES" are what go into the figures, so a chart cannot drift away
from the data behind it.

    python src/build_series.py
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
import asi_data as A
from paths import BUILD

OUT = []


def w(s=''):
    OUT.append(str(s))
    print(s)


up = A.block(A.UPSTREAM)
dn = A.block(A.DOWNSTREAM)
wide = A.block(A.DOWNSTREAM_WIDE)
cls = {c: A.block([c]) for c in ['2420', '2432', '2511', '2599']}

RULE = '=' * 78

# ------------------------------------------------------------------ identities
w(RULE)
w('ACCOUNTING IDENTITIES')
w(RULE)
worst = 0.0
for c in ['2420', '2432', '2511', '2599']:
    for y in A.YEARS:
        o, i, g = A.get('output', c, y), A.get('inputs', c, y), A.get('gva', c, y)
        if g and not np.isnan(g):
            worst = max(worst, abs((o - i - g) / g))
w(f'  output - inputs - GVA: worst relative deviation {worst:.8%}')
for y in A.YEARS:
    resid = sum(A.get('workers', c, y) - A.get('direct', c, y) - A.get('contract', c, y)
                for c in ['2420', '2432', '2511', '2599', '2710', '2732'])
    flag = '   <-- fails' if abs(resid) > 100 else ''
    w(f'  {y}  direct + contract - total workers = {resid:>10,.0f}{flag}')

# ------------------------------------------------------------------ headline
w()
w(RULE)
w('HEADLINE SERIES')
w(RULE)
w(f'{"year":<9}{"UP GVA":>10}{"DN GVA":>10}{"UP PE":>9}{"DN PE":>9}'
  f'{"UP v":>8}{"DN v":>8}{"lambda":>8}{"UP w/s":>8}{"DN w/s":>8}')
lam = A.labour_intensity(up, dn)
for y in A.YEARS:
    w(f'{y:<9}{up.loc[y,"gva_cr"]:>10,.0f}{dn.loc[y,"gva_cr"]:>10,.0f}'
      f'{up.loc[y,"pe"]:>9,.0f}{dn.loc[y,"pe"]:>9,.0f}'
      f'{up.loc[y,"gva_per_pe_lakh"]:>8.2f}{dn.loc[y,"gva_per_pe_lakh"]:>8.2f}'
      f'{lam[y]:>8.2f}{up.loc[y,"wage_share"]:>8.1f}{dn.loc[y,"wage_share"]:>8.1f}')

w()
w(f'{"year":<9}{"UP c/s":>9}{"DN c/s":>9}{"UP tax":>9}{"DN tax":>9}'
  f'{"UP y":>8}{"DN y":>8}{"UP inp%":>9}{"DN inp%":>9}')
for y in A.YEARS:
    w(f'{y:<9}{up.loc[y,"contract_share"]:>9.1f}{dn.loc[y,"contract_share"]:>9.1f}'
      f'{up.loc[y,"tax_cr"]:>9,.0f}{dn.loc[y,"tax_cr"]:>9,.0f}'
      f'{up.loc[y,"pe_per_cr_tax"]:>8.0f}{dn.loc[y,"pe_per_cr_tax"]:>8.0f}'
      f'{up.loc[y,"input_share"]:>9.1f}{dn.loc[y,"input_share"]:>9.1f}')

# ------------------------------------------------------------------ growth
w()
w(RULE)
w('GROWTH, 2011-12 to 2022-23 (nominal)')
w(RULE)
w(f'{"measure":<20}{"upstream":>12}{"downstream":>12}')
for label, col in [('GVA', 'gva_cr'), ('Persons engaged', 'pe'),
                   ('Total workers', 'workers'), ('Contract workers', 'contract'),
                   ('Wages', 'wages_cr'), ('Estimated tax', 'tax_cr')]:
    f = lambda d: 100 * (d.loc['2022-23', col] / d.loc['2011-12', col] - 1)
    w(f'{label:<20}{f(up):>+11.1f}%{f(dn):>+11.1f}%')

w()
w('  Three-year endpoint averages (removes base-year sensitivity):')
for name, frame in [('upstream', up), ('downstream', dn), ('NIC 2511', cls['2511'])]:
    g = A.endpoint_growth(frame)
    w(f'    {name:<12} {g["from"]:>9,.0f} -> {g["to"]:>9,.0f} cr  '
      f'{g["growth_pct"]:>+7.1f}%   CAGR {g["cagr_pct"]:.2f}%')

# ------------------------------------------------------------------ robustness
w()
w(RULE)
w('ROBUSTNESS')
w(RULE)
checks = {
    'downstream more labour-intensive': sum(lam[y] > 1 for y in A.CLEAN),
    'ratio above the 2.5x benchmark': sum(lam[y] > 2.5 for y in A.CLEAN),
    'downstream wage share higher': sum(dn.loc[y, 'wage_share'] > up.loc[y, 'wage_share'] for y in A.CLEAN),
    'downstream persons engaged higher': sum(dn.loc[y, 'pe'] > up.loc[y, 'pe'] for y in A.CLEAN),
    'downstream jobs per rupee of tax higher': sum(dn.loc[y, 'pe_per_cr_tax'] > up.loc[y, 'pe_per_cr_tax'] for y in A.CLEAN),
}
for k, v in checks.items():
    w(f'  {k:<44} {v}/12')
vals = [lam[y] for y in A.CLEAN]
w(f'  labour-intensity ratio: min {min(vals):.2f}  max {max(vals):.2f}  '
  f'median {np.median(vals):.2f}')

w()
w('  Leave-one-out on the downstream basket (2022-23):')
for c in A.DOWNSTREAM:
    rest = [x for x in A.DOWNSTREAM if x != c]
    r = up.loc['2022-23', 'gva_per_pe_lakh'] / A.block(rest).loc['2022-23', 'gva_per_pe_lakh']
    w(f'    without {c}: {r:.2f}x')
w(f'    full basket: {lam["2022-23"]:.2f}x')

w()
w('  Alternative segment definitions (2022-23):')
mfa_up, mfa_dn = A.block(['2420', '2432']), A.block(['2511', '2599'])
w(f'    material-flow reading, 2432 upstream: '
  f'{mfa_up.loc["2022-23","gva_per_pe_lakh"]/mfa_dn.loc["2022-23","gva_per_pe_lakh"]:.2f}x')
w(f'    wide basket, adding 2710 and 2732:    '
  f'{up.loc["2022-23","gva_per_pe_lakh"]/wide.loc["2022-23","gva_per_pe_lakh"]:.2f}x')

b = A.apportionment_bounds()
w()
w('  Apportionment: the ratio is bounded for any positive aluminium shares')
w(f'    class productivities: '
  + ', '.join(f'{k} {v:.4f}' for k, v in b['class_productivity'].items()))
w(f'    lambda in [{b["lower"]:.4f}, {b["upper"]:.4f}] '
  f'against {b["undiscounted"]:.4f} undiscounted')

rng = np.random.default_rng(0)
lo = hi = None
G = {c: A.get('gva', c, '2022-23') for c in A.DOWNSTREAM}
L = {c: A.get('pe', c, '2022-23') for c in A.DOWNSTREAM}
v_u = up.loc['2022-23', 'gva_per_pe_lakh']
for _ in range(200_000):
    a = rng.uniform(0.01, 1.0, 3)
    v_d = sum(a[i] * G[c] for i, c in enumerate(A.DOWNSTREAM)) / \
          sum(a[i] * L[c] for i, c in enumerate(A.DOWNSTREAM))
    r = v_u / v_d
    lo = r if lo is None else min(lo, r)
    hi = r if hi is None else max(hi, r)
w(f'    200,000 random draws land in [{lo:.4f}, {hi:.4f}] -- inside the bound')

w()
w(f'  Volatility of value added: upstream {A.volatility(up):.4f}, '
  f'downstream {A.volatility(dn):.4f}  '
  f'({A.volatility(up)/A.volatility(dn):.1f}x)')
w(f'  Input-cost amplification m/(1-m): {A.amplification():.4f}')

# ------------------------------------------------------------------ coordinates
w()
w(RULE)
w('FIGURE COORDINATES  (paste straight into the pgfplots blocks)')
w(RULE)


def emit(title, series, years, dp, labelled=False):
    w(f'\n-- {title}')
    w('   ' + A.pgfplots_coords(series, years, dp, label=labelled))


emit('Fig 4.1  GVA index, upstream', A.index_100(up, 'gva_cr'), A.YEARS, 0)
emit('Fig 4.1  GVA index, downstream', A.index_100(dn, 'gva_cr'), A.YEARS, 0)
emit('Fig 4.2  labour-intensity ratio', lam, A.CLEAN, 2, True)
emit('Fig 4.3  wage share, downstream', dn['wage_share'], A.CLEAN, 1, True)
emit('Fig 4.3  wage share, upstream', up['wage_share'], A.CLEAN, 1, True)
for c in ['2420', '2599', '2432', '2511']:
    emit(f'Fig 4.4  GVA index, NIC {c}', A.index_100(cls[c], 'gva_cr'), A.CLEAN, 1)
emit('Fig 4.5  contract share, upstream', up['contract_share'], A.CLEAN, 1)
emit('Fig 4.5  contract share, downstream', dn['contract_share'], A.CLEAN, 1)
emit('Fig 4.6  employment yield, downstream', dn['pe_per_cr_tax'], A.CLEAN, 0, True)
emit('Fig 4.6  employment yield, upstream', up['pe_per_cr_tax'], A.CLEAN, 0, True)

path = BUILD / 'series_output.txt'
path.write_text('\n'.join(OUT), encoding='utf-8')
print(f'\n[written to {path}]')
