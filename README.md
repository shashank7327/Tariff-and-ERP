# Indian downstream aluminium: tariff analysis

Code and analysis behind *Rationalizing Tariff Structures in the Indian Downstream
Aluminium Industry* — a policy submission arguing for rationalisation of the basic
customs duty on primary aluminium (HS 7601).

The report makes two empirical claims. First, that the thirteen downstream product
lines HS 7604–7616 carry negative effective protection under India's preferential
trade agreements. Second, that the segment those lines belong to is the one on which
employment and household income depend. This repository contains the work behind the
second claim, the public-finance analysis of the fiscal objection to reform, and the
machinery that builds and checks the document.

---

## The problem this code solves

The tariff evidence and the industrial evidence had to describe **the same industry**.
Earlier drafts partitioned the Annual Survey of Industries by convention, which meant
the effective-protection tables and the employment tables were about different
sectors — an easy thing for a reviewer to notice and a hard thing to defend.

So I derived the industrial classification from the tariff schedule instead. Following
Corden's definition of an *activity* as a stage of conversion from a traded input to a
traded output, a NIC class is downstream if and only if its principal output falls
inside HS 7604–7616:

| | NIC classes | HS lines |
|---|---|---|
| **Upstream** | 2420 | 7601–7603 — the dutiable input |
| **Downstream** | 2432, 2511, 2599 | 7604–7616 — the thirteen ERP basket lines |

NIC 2710, 2732, 2733 and 3030 are excluded: their principal outputs sit in HS Chapters
85 and 88, which makes them a different activity facing different tariffs. Their effect
on the results is reported rather than assumed away.

## Principal findings

| Finding | Result | Robustness |
|---|---|---|
| Employment sustained per unit of value added | **3.14×** downstream (range 3.08–6.18, median 3.93) | Holds in 12 of 12 years |
| Labour share of value added | **38.4%** vs **17.6%** | Series never cross; uses only monetary variables |
| Employment per unit of estimated corporate tax | **151** vs **39** per crore | Ordering holds in 12 of 12 years |
| Structural products (NIC 2511, HS 7610) | **+15.0%** nominal over 11 years, workforce flat | The most disprotected line in the ERP table |
| Volatility of value added | Upstream **3.6×** downstream | sd of year-on-year log growth |
| Input-cost amplification | **4.91×** | From a measured input share of 83.1% |

Three results are derived formally rather than argued, and these are the parts I would
defend hardest:

- **Apportionment invariance.** None of the NIC classes is purely aluminium, and the
  obvious objection is that each should be scaled by its aluminium share. It does not
  matter. An apportioned segment productivity is necessarily a weighted average of its
  class productivities, so it is bounded by their range for *any* positive
  apportionment vector; upstream being a single class, its own coefficient cancels. The
  headline ratio lies in **[3.01, 3.38]** whatever is assumed. Verified against 200,000
  random draws.
- **The per-tonne decomposition.** Employment per tonne factors exactly into employment
  per rupee times value added per tonne (3.14 × 1.81 = 5.7). This reconciles my measure
  with the 35:1 ratios circulating in industry discussion, and shows those to come from
  comparing mismatched employment universes.
- **The transfer-to-revenue identity.** In the tariff-versus-GST analysis the ratio of
  surplus transferred to revenue collected reduces to `a/c = φ(1−μ)/[μ(1−f)]` — import
  penetration, pass-through, duty-free share. Price, exchange rate and both elasticities
  cancel, which makes it robust to the parameters I know least well.

## What the code does

```
src/
  paths.py            where everything lives; ALU_DATA overrides the data directory
  asi_data.py         the analysis core — every other script imports this
  build_series.py     builds all series, prints the numbers, emits plotting coordinates
  verify_figures.py   re-derives every plotted point and quoted statistic from source
  tariff_gst.py       public-finance analysis: welfare accounting and revenue arithmetic
  build_report.py     assembles the report from its parts
  report_patches.py   the body edits applied at build time, each with its anchor
tex/                  LaTeX sources: the base report, Section 4, the appendix, the notes
data/                 source data (see data/README.md)
build/                generated — not tracked
docs/                 compiled PDFs
```

### Reproducing everything

```bash
pip install -r requirements.txt

python src/build_series.py      # all series; writes build/series_output.txt
python src/verify_figures.py    # audit; exits non-zero if anything has drifted
python src/tariff_gst.py        # public-finance arithmetic and sensitivity
python src/build_report.py      # assemble the report

xelatex -output-directory=build build/aluminium_report_downstream.tex   # ×3
```

Or `make all`.

## The verification harness

`verify_figures.py` recomputes every series from source, parses every plotting
coordinate out of the LaTeX, and asks of each printed number: **is this a correct
rounding of the computed value, at the precision it is printed?** It then re-checks the
statistics quoted in prose. Current status: all checks pass across **158 plotted points
and 30 quoted statistics**.

I wrote it because I did not trust proofreading, and it turned out I was right not to.
On its first run it caught four errors that had survived several drafts — three plotted
points that had been rounded twice (136.47 printed as 137, 214.47 as 215, 139.47 as 140)
and an amplification factor computed from a rounded input share and printed as 4.92
instead of 4.91. None changed a conclusion. None would have been found by reading.

Two things worth knowing if you extend it:

- Test *correct rounding*, not equality against a re-rounded value. Python's `round()`
  is banker's rounding and will report false positives.
- Keep `SERIES` in step with the figures. The checker matches each computed series
  against the coordinate block that plots it, so a series that is no longer plotted gets
  matched against the wrong block and reported as a spurious mismatch.

## Figures

Twenty-one figures across the report, seven in the industrial-statistics section. The
plotting coordinates are emitted by `build_series.py` and pasted into the LaTeX, so a
chart cannot drift away from the data behind it — and if anyone edits one by hand, the
harness catches it.

They are built to survive being printed and photocopied, which is how a policy
submission actually gets read:

- every series is distinguished by **three redundant cues** — line style, marker shape
  and marker fill — so none depends on colour or grey level;
- every printed value sits on an **opaque white chip**, so a plot line passing beneath
  cannot obscure it;
- legends sit **outside the plotting area**, never over data;
- **values are printed on the chart**, so nothing has to be read off an axis;
- captions carry a **source line only** — construction and domain detail live in the
  appendix.

Where two series run close or cross, per-point labelling is replaced by direct
annotation of endpoints and turning points; white chips prevent lines obscuring text but
not text obscuring text.

## What I would not claim

The evidence is **association, not an identified causal effect**, and the report says so
in those words. There is no counterfactual India without the duty, the
effective-protection series covers three years against twelve of ASI data, and the
construction cycle is an uncontrolled alternative explanation for the structural-products
result specifically — a good one, since structural products track building activity
closely.

Known weak points, all stated in the documents rather than left to be found: the metal
share of the downstream input bill is assumed rather than measured; the per-tonne
figures mix official employment with industry-estimated tonnage; the corporate-tax series
is a proxy built from net profit and a uniform effective rate; and the ASI frame excludes
the unincorporated units in which downstream fabrication is concentrated.

## Data

Source data in `data/`. The ASI file is 3,705 observations across 15 indicators, 19 NIC
classes and 13 years (2011–12 to 2023–24). All stated statistics run to **2022–23**:
in 2023–24 reported wages fall in every class while output and employment rise, and the
identity linking directly-employed and contract workers to total workers fails with a
residual of 178,591 workers, having held exactly in each of the twelve preceding years.

See `data/README.md` for provenance.

## References

The argument is grounded in primary sources. The load-bearing ones:

- Corden (1966), *The Structure of a Tariff System and the Effective Protective Rate*, JPE 74(3) — supplies the segmentation rule
- Balassa (1965, 1968) — precedent for negative effective protection; tariff escalation
- Diamond & Mirrlees (1971), AER 61 — production efficiency: do not tax intermediate goods
- Bhagwati & Ramaswami (1963), JPE 71(1) — target the distortion at its source
- Emran & Stiglitz (2005) and Keen (2008), JPubE — the informality objection, and its limits
- Baunsgaard & Keen (2010), JPubE 94 — revenue recovery after trade liberalisation
- Bohlin & Widell (2006); Miller & Blair (2009) — technology assumptions and factor-content invariance
- Cullen & Allwood (2013); Bertram et al. (2009) — material-flow taxonomy of the aluminium system
- Pathania & Bhattacharjea (2020), FTR 55(2) — the modified Corden estimator
