"""
Empirical arithmetic for the tariff-versus-GST note.

Every figure quoted in tariff_gst_note.tex is produced here. The baseline is
declared once, at the top, with a source and a plausible range for each
parameter; results are then reported at the baseline and across the ranges.

Run: python tariff_gst_arithmetic.py
"""
import sys
import itertools

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

CR = 1e7          # one crore, in rupees
LINE = '=' * 78


# ===========================================================================
# BASELINE  (B1-B12).  value, low, high, source
# ===========================================================================
class P:
    BCD      = 0.075                    # B1  basic customs duty, HS 7601
    SWS      = 0.10                     # B2  social welfare surcharge, on BCD
    GST      = 0.18                     # B3  GST/IGST on aluminium, creditable

    Q_C      = 4.50                     # B4  domestic primary consumption, Mt
    Q_C_RNG  = (3.50, 5.00)
    Q_M      = 0.392                    # B5  primary imports, Mt (2024)
    IMP_USD  = 1.03e9                   # B6  value of those imports, USD
    FX       = 87.0                     # B7  INR per USD
    FX_RNG   = (83.0, 90.0)

    PHI      = 1.00                     # B8  pass-through of duty into the
    PHI_RNG  = (0.70, 1.00)             #     domestic price (1 = full parity)
    F_FTA    = 0.40                     # B9  share of primary imports entering
    F_FTA_RNG = (0.00, 0.70)            #     duty-free under trade agreements

    EPS_S    = 0.20                     # B10 supply elasticity, primary metal
    EPS_S_RNG = (0.10, 0.50)
    EPS_D    = 0.50                     # B11 |demand elasticity| for the metal
    EPS_D_RNG = (0.20, 0.80)

    THETA    = 0.60                     # B12 metal share of the downstream
    THETA_RNG = (0.30, 0.70)            #     input bill

    # fixed, from the report
    AMPLIF       = 4.91                 # m/(1-m) with m = 0.8309
    DN_OUTPUT_CR = 246_299              # ASI downstream output 2022-23
    DN_GVA_CR    = 41_653               # ASI downstream GVA 2022-23
    GST_TOTAL_CR = 22_27_000            # FY26 gross GST collections


DUTY = P.BCD * (1 + P.SWS)              # effective pre-IGST duty
MU   = P.Q_M / P.Q_C                    # import penetration
PRICE_T = P.IMP_USD * P.FX / (P.Q_M * 1e6)   # implied landed price, INR/tonne


def transfer_cr(q_c=P.Q_C, q_m=P.Q_M, price=PRICE_T, phi=P.PHI, t=DUTY):
    """Area a: producer surplus gained on domestically supplied metal."""
    return phi * t * price * (q_c - q_m) * 1e6 / CR


def revenue_cr(q_m=P.Q_M, price=PRICE_T, f=P.F_FTA, t=DUTY):
    """Area c: duty actually collected, net of duty-free preferential imports."""
    return (1 - f) * t * price * q_m * 1e6 / CR


def deadweight_cr(q_c=P.Q_C, q_m=P.Q_M, price=PRICE_T,
                  eps_s=P.EPS_S, eps_d=P.EPS_D, phi=P.PHI, t=DUTY):
    """Areas b and d, linear approximation."""
    tp = phi * t
    b = 0.5 * eps_s * tp ** 2 * price * (q_c - q_m) * 1e6 / CR
    d = 0.5 * eps_d * tp ** 2 * price * q_c * 1e6 / CR
    return b, d


# ===========================================================================
print(LINE)
print('BASELINE')
print(LINE)
rows = [
    ('B1  basic customs duty, HS 7601', f'{P.BCD:.1%}', '--', 'tariff schedule'),
    ('B2  social welfare surcharge', f'{P.SWS:.0%} of BCD', '--', 'tariff schedule'),
    ('    effective pre-IGST duty t', f'{DUTY:.3%}', '--', 'derived'),
    ('B3  GST / IGST, creditable', f'{P.GST:.0%}', '--', 'GST schedule'),
    ('B4  domestic primary consumption', f'{P.Q_C:.2f} Mt', f'{P.Q_C_RNG[0]}-{P.Q_C_RNG[1]}', 'industry data, CY2024'),
    ('B5  primary imports (HS 7601)', f'{P.Q_M:.3f} Mt', '--', 'report §3.1, 2024'),
    ('    import penetration mu', f'{MU:.1%}', '--', 'derived'),
    ('B6  value of those imports', f'US${P.IMP_USD/1e9:.2f}bn', '--', 'report §3.1'),
    ('B7  exchange rate', f'INR {P.FX:.0f}/USD', f'{P.FX_RNG[0]:.0f}-{P.FX_RNG[1]:.0f}', 'assumption'),
    ('    implied landed price', f'INR {PRICE_T:,.0f}/t', '--', 'derived from B5, B6, B7'),
    ('B8  duty pass-through phi', f'{P.PHI:.2f}', f'{P.PHI_RNG[0]}-{P.PHI_RNG[1]}', 'import-parity pricing'),
    ('B9  duty-free share of imports f', f'{P.F_FTA:.0%}', f'{P.F_FTA_RNG[0]:.0%}-{P.F_FTA_RNG[1]:.0%}', 'FTA schedules; least certain'),
    ('B10 supply elasticity', f'{P.EPS_S:.2f}', f'{P.EPS_S_RNG[0]}-{P.EPS_S_RNG[1]}', 'metals literature'),
    ('B11 demand elasticity (abs)', f'{P.EPS_D:.2f}', f'{P.EPS_D_RNG[0]}-{P.EPS_D_RNG[1]}', 'metals literature'),
    ('B12 metal share of input bill', f'{P.THETA:.0%}', f'{P.THETA_RNG[0]:.0%}-{P.THETA_RNG[1]:.0%}', 'not observable in ASI'),
]
print(f'  {"parameter":<34}{"baseline":>16}{"range":>14}  source')
for a, b, c, d in rows:
    print(f'  {a:<34}{b:>16}{c:>14}  {d}')


# ===========================================================================
print()
print(LINE)
print('RESULT 1  The transfer-to-revenue ratio is an identity in import penetration')
print(LINE)
print('  a/c = phi (1 - mu) / [ mu (1 - f) ]')
print('  It contains no price, no exchange rate and no elasticity: those cancel.')
print()
print(f'  {"mu":>6}' + ''.join(f'{f"f={f:.0%}":>10}' for f in (0.0, 0.2, 0.4, 0.6)))
for mu in (0.05, 0.0871, 0.10, 0.15, 0.20):
    cells = ''.join(f'{P.PHI*(1-mu)/(mu*(1-f)):>10.1f}' for f in (0.0, 0.2, 0.4, 0.6))
    star = '   <- baseline' if abs(mu - MU) < 0.001 else ''
    print(f'  {mu:>6.1%}' + cells + star)
print()
print(f'  At the baseline (mu={MU:.1%}, f={P.F_FTA:.0%}, phi={P.PHI:.2f}): '
      f'{P.PHI*(1-MU)/(MU*(1-P.F_FTA)):.1f} : 1')
print(f'  Most conservative cell in the table (mu=20%, f=0, phi=0.7): '
      f'{0.7*(1-0.20)/(0.20*1.0):.1f} : 1')


# ===========================================================================
print()
print(LINE)
print('RESULT 2  Levels at the baseline (INR crore)')
print(LINE)
a = transfer_cr()
c = revenue_cr()
c_stat = revenue_cr(f=0.0)
b, d = deadweight_cr()
print(f'  a   upstream producer surplus gained          {a:>10,.0f}')
print(f'  c   duty collected, net of duty-free imports  {c:>10,.0f}')
print(f'      (at the statutory rate on every tonne)    {c_stat:>10,.0f}')
print(f'  b   production deadweight                     {b:>10,.0f}')
print(f'  d   conversion forgone                        {d:>10,.0f}')
print(f'  ---------------------------------------------{"":->11}')
print(f'  a+b+c+d  downstream surplus lost              {a+b+c+d:>10,.0f}')
print(f'  b+d      national welfare lost                {b+d:>10,.0f}')
print()
print(f'  Deadweight per rupee of revenue raised:  INR {(b+d)/c:.2f}')
print(f'  Transferred per rupee of revenue raised: INR {a/c:.2f}')


# ===========================================================================
print()
print(LINE)
print('RESULT 3  Replacing the revenue through GST')
print(LINE)
pp = 100 * c / P.DN_OUTPUT_CR
pp_stat = 100 * c_stat / P.DN_OUTPUT_CR
print(f'  Revenue to replace (net of duty-free imports)  INR {c:,.0f} crore')
print(f'  GST rate change on the downstream base         +{pp:.2f} pp  '
      f'({P.GST*100:.0f}% -> {P.GST*100+pp:.2f}%)')
print(f'  If instead the statutory maximum is replaced   +{pp_stat:.2f} pp  '
      f'({P.GST*100:.0f}% -> {P.GST*100+pp_stat:.2f}%)')
print(f'  As a share of FY26 gross GST                   {100*c/P.GST_TOTAL_CR:.3f}%')
print(f'  Days of GST collection at the FY26 average     {c/(P.GST_TOTAL_CR/365):.2f}')


# ===========================================================================
print()
print(LINE)
print('RESULT 4  The induced-expansion offset')
print(LINE)
print(f'  Downstream value added rises by  amplification x theta x t x phi')
print(f'  {"theta":>7}{"VA released":>16}{"GST on it":>14}{"vs revenue lost":>18}')
for th in (0.30, 0.45, 0.60, 0.70):
    gain_pct = P.AMPLIF * th * DUTY * P.PHI
    gain_cr = P.DN_GVA_CR * gain_pct
    gst_gain = gain_cr * P.GST
    verdict = 'covers' if gst_gain > c else 'does not cover'
    print(f'  {th:>6.0%}{gain_pct:>15.1%}{gain_cr:>10,.0f} cr{gst_gain:>10,.0f} cr'
          f'   {verdict}')
print()
print('  NOTE: illustrative. Assumes the relief is retained downstream rather than')
print('  competed away, that capacity exists to convert it, and that no offsetting')
print('  upstream contraction reduces the GST base elsewhere.')


# ===========================================================================
print()
print(LINE)
print('RESULT 5  Sensitivity of the headline ratio a/c')
print(LINE)
lo = hi = None
for q_c, phi, f, fx in itertools.product(P.Q_C_RNG, P.PHI_RNG, P.F_FTA_RNG, P.FX_RNG):
    price = P.IMP_USD * fx / (P.Q_M * 1e6)
    r = transfer_cr(q_c=q_c, price=price, phi=phi) / revenue_cr(price=price, f=f)
    lo = r if lo is None else min(lo, r)
    hi = r if hi is None else max(hi, r)
print(f'  Across all corners of the declared ranges: a/c from {lo:.1f} to {hi:.1f}')
print(f'  Baseline: {a/c:.1f}')
print()
print('  The ratio never approaches 1 under any combination, which is the only')
print('  thing the argument requires.')
