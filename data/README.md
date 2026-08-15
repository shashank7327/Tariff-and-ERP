# Data

Everything the code reads. Provenance below, so any figure can be traced back to a
published cell.

| File | Source | Coverage |
|---|---|---|
| `ASI_National.csv` | Annual Survey of Industries, All-India summary results, NSO / MoSPI | 3,705 observations; 15 indicators, 19 NIC 2008 classes, 2011–12 to 2023–24. Values in INR lakh; employment in persons |
| `data_nic_ectr.csv` | Effective corporate tax rates by year | 2011–12 to 2023–24 |
| `Aluminium NIC - Aluminium NIC.csv` | NIC 2008 concordance for the aluminium chain | Phase, division, group, class |
| `ERP.xlsx` | Own estimates from MOSPI Supply–Use Tables and partner tariff schedules | Effective rate of protection, 13 HS lines × 6 partners, 2015–16 / 2019–20 / 2024–25 |
| `Tariff FD.xlsx` | Indian customs tariff and partner preferential schedules | 256 tariff lines, HS 7601–7616; MFN and preferential rates |

## Notes on use

**Units.** The ASI publishes money in INR lakh. `asi_data.block()` converts to INR
crore; value added per person comes out in INR lakh per person directly, which is a
convenience of the source units rather than a conversion.

**Indicator names are matched literally**, including `No. of Directly Employed  Workers`
with two spaces. If a future ASI release changes the spelling, `INDICATORS` in
`src/asi_data.py` is the only place to edit.

**2023–24.** Available but excluded from every stated statistic. Reported wages fall in
every class that year while output and persons engaged rise, and the identity linking
directly-employed and contract workers to total workers fails with a residual of 178,591
workers — 19.6 per cent of the total — having held exactly in each of the twelve
preceding years. Something changed in the definition or the coverage. Only the value
added index, which does not depend on either broken variable, extends to 2023–24, and it
is marked provisional where plotted.

**Not included here.** The Supply–Use Tables (26 supply and use files, 2011–12 to
2023–24) sit outside this repository for size. They feed the effective-protection
estimates in `ERP.xlsx` rather than any code in `src/`, so nothing here depends on them.

## Pointing elsewhere

```bash
export ALU_DATA=/path/to/data     # Windows: set ALU_DATA=...
python src/build_series.py
```
