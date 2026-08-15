"""The analysis core: everything else in this repository imports from here.

I split the aluminium value chain the way the tariff schedule splits it, following
Corden's definition of an *activity* as a stage of conversion from a traded input to
a traded output. A NIC class is downstream if and only if its principal output falls
inside HS 7604-7616, the thirteen lines on which the report estimates effective
protection:

    UPSTREAM    NIC 2420                  primary metal, HS 7601-7603
    DOWNSTREAM  NIC 2432, 2511, 2599      conversion, HS 7604-7616

NIC 2710, 2732, 2733 and 3030 are excluded: their principal outputs are in HS
Chapters 85 and 88, which makes them a different activity facing different tariffs.

Units: the ASI publishes in INR lakh. `block()` returns money in INR crore and
employment in persons. Value added per person comes out in INR lakh directly, which
is a convenience of the source units rather than a conversion.
"""
import numpy as np
import pandas as pd

from paths import ASI_CSV, ECTR_CSV

# --------------------------------------------------------------------------- setup
YEARS = ['2011-12', '2012-13', '2013-14', '2014-15', '2015-16', '2016-17',
         '2017-18', '2018-19', '2019-20', '2020-21', '2021-22', '2022-23',
         '2023-24']

#: 2023-24 is excluded from every stated statistic. Reported wages fall in every
#: class that year while output and employment rise, and the identity linking
#: directly-employed and contract workers to total workers fails.
CLEAN = YEARS[:-1]

UPSTREAM = ['2420']
DOWNSTREAM = ['2432', '2511', '2599']
DOWNSTREAM_WIDE = ['2432', '2511', '2599', '2710', '2732']   # earlier, wider basket

LAKH_TO_CR = 1 / 100.0

#: ASI indicator names, exactly as they appear in the source file.
INDICATORS = {
    'gva':      'Gross Value Added',
    'output':   'Total Output',
    'inputs':   'Total Inputs',
    'nva':      'Net Value Added',
    'profit':   'Net Profit',
    'wages':    'Wages and Salaries',
    'pe':       'Total Number of Persons Engaged',
    'workers':  'Total Number of Workers',
    'direct':   'No. of Directly Employed  Workers',   # two spaces, as published
    'contract': 'No. of Workers employed Through Contractors',
    'eow':      'No. of Employees Other Than Workers',
}

_PIVOT = None
_ECTR = None


def _load():
    """Read the ASI file once and index it by (nic_code, year) per indicator."""
    global _PIVOT, _ECTR
    if _PIVOT is not None:
        return

    d = pd.read_csv(ASI_CSV)
    d['nic_code'] = d['nic_code'].astype(str)
    d['value'] = pd.to_numeric(d['value'], errors='coerce')

    _PIVOT = {}
    for key, name in INDICATORS.items():
        s = d[d.indicator == name].set_index(['nic_code', 'year'])['value']
        _PIVOT[key] = s[~s.index.duplicated()]

    e = pd.read_csv(ECTR_CSV)
    e['nic_code'] = e['nic_code'].astype(str)
    _ECTR = {(r.year, r.nic_code): r.ectr for r in e.itertuples()}


def get(key, nic, year):
    """One published cell, in the ASI's own units (INR lakh, or persons)."""
    _load()
    try:
        return float(_PIVOT[key].loc[(nic, year)])
    except KeyError:
        return np.nan


def ectr(nic, year):
    """Effective corporate tax rate, per cent."""
    _load()
    return _ECTR.get((year, nic))


def tax(nic, year):
    """Estimated corporate tax, INR lakh.

    The ASI publishes net profit, not tax paid. I estimate tax as net profit times
    the effective rate for the year, and *exclude* loss-making observations rather
    than netting them off -- a negative tax has no behavioural interpretation. One
    observation among the retained classes is affected: NIC 2432 in 2013-14.
    """
    p = get('profit', nic, year)
    r = ectr(nic, year)
    if r is None or np.isnan(p) or p <= 0:
        return 0.0
    return p * r / 100.0


def _agg(codes, key, year):
    return float(np.nansum([get(key, c, year) for c in codes]))


def block(codes, years=None):
    """Every series for a set of NIC classes, indexed by year.

    Money in INR crore, employment in persons, shares in per cent, and
    ``gva_per_pe_lakh`` in INR lakh per person.
    """
    years = years or YEARS
    rows = []
    for y in years:
        gva = _agg(codes, 'gva', y)
        out = _agg(codes, 'output', y)
        inp = _agg(codes, 'inputs', y)
        wg = _agg(codes, 'wages', y)
        pe = _agg(codes, 'pe', y)
        wk = _agg(codes, 'workers', y)
        ct = _agg(codes, 'contract', y)
        dr = _agg(codes, 'direct', y)
        tx = float(np.nansum([tax(c, y) for c in codes]))
        rows.append(dict(
            year=y,
            gva_cr=gva * LAKH_TO_CR,
            out_cr=out * LAKH_TO_CR,
            inp_cr=inp * LAKH_TO_CR,
            wages_cr=wg * LAKH_TO_CR,
            tax_cr=tx * LAKH_TO_CR,
            pe=pe, workers=wk, contract=ct, direct=dr,
            gva_per_pe_lakh=(gva / pe) if pe else np.nan,
            wage_share=100 * wg / gva if gva else np.nan,
            contract_share=100 * ct / wk if wk else np.nan,
            input_share=100 * inp / out if out else np.nan,
            va_margin=100 * gva / out if out else np.nan,
            pe_per_cr_tax=pe / (tx * LAKH_TO_CR) if tx else np.nan,
        ))
    return pd.DataFrame(rows).set_index('year')


# ------------------------------------------------------------------ derived series
def index_100(frame, column, base='2011-12'):
    """Index a column to 100 in the base year."""
    return frame[column] / frame.loc[base, column] * 100


def labour_intensity(up=None, dn=None):
    """Upstream GVA per person divided by downstream: the headline ratio.

    Above one means a rupee of value added created downstream sustains that many
    times the employment of a rupee created upstream.
    """
    up = block(UPSTREAM) if up is None else up
    dn = block(DOWNSTREAM) if dn is None else dn
    return up['gva_per_pe_lakh'] / dn['gva_per_pe_lakh']


def volatility(frame, column='gva_cr', years=None):
    """Sample standard deviation of year-on-year log growth.

    Log differences rather than percentage changes: they are symmetric in direction
    and additive over time, which matters for a series that moves +74 and -34 per
    cent in adjacent years.
    """
    years = years or CLEAN
    g = frame.loc[years, column].astype(float).values
    return float(np.diff(np.log(g)).std(ddof=1))


def endpoint_growth(frame, column='gva_cr', first=None, last=None, span=9):
    """Growth between three-year averages at each end, and the compound rate.

    Single-endpoint growth is unstable because upstream value added is volatile
    enough that the sign of the differential moves with the base year. `span` is the
    number of years between the *midpoints* of the two windows, not the endpoints.
    """
    first = first or ['2011-12', '2012-13', '2013-14']
    last = last or ['2020-21', '2021-22', '2022-23']
    a = frame.loc[first, column].mean()
    b = frame.loc[last, column].mean()
    return {'from': a, 'to': b,
            'growth_pct': 100 * (b / a - 1),
            'cagr_pct': 100 * ((b / a) ** (1 / span) - 1)}


def apportionment_bounds(year='2022-23'):
    """The labour-intensity ratio is bounded whatever aluminium shares are assumed.

    An apportioned segment productivity is a weighted average of its class
    productivities, so it is bounded by their range for *any* positive apportionment
    vector; upstream is a single class, so its own coefficient cancels exactly.
    That makes the objection "these classes are not purely aluminium" answerable by
    proof rather than by simulation.
    """
    v_u = block(UPSTREAM).loc[year, 'gva_per_pe_lakh']
    v = {c: block([c]).loc[year, 'gva_per_pe_lakh'] for c in DOWNSTREAM}
    return {'lower': v_u / max(v.values()),
            'upper': v_u / min(v.values()),
            'undiscounted': v_u / block(DOWNSTREAM).loc[year, 'gva_per_pe_lakh'],
            'class_productivity': v}


def amplification(year='2022-23'):
    """m/(1-m): how far an input-cost change is amplified when it reaches value added.

    Value added is what remains after inputs, so with an input share m the ratio
    m/(1-m) is the factor by which any proportional change in input cost is
    magnified by the time it shows up in value added.
    """
    m = block(DOWNSTREAM).loc[year, 'input_share'] / 100
    return m / (1 - m)


def pgfplots_coords(series, years, decimals=1, label=None):
    """Emit a pgfplots coordinate string, optionally with printed value labels.

    The figures in the report are built from these strings, so a chart cannot drift
    away from the data behind it.
    """
    out = []
    for y in years:
        x = y[2:]
        v = f'{series[y]:.{decimals}f}'
        out.append(f'({x},{v})' + (f'[{v}]' if label else ''))
    return ''.join(out)
