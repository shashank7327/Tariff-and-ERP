"""
Body patches applied by build_downstream_report.py to aluminium_report.tex.

Kept in a separate module so the build script stays readable and each patch can
be inspected on its own. Every patch is a (find, replace) pair applied exactly
once; the build asserts that the anchor was found.
"""

# ---------------------------------------------------------------------------
# 1. Abstract — rewritten to describe the report as it now stands: the ERP
#    estimates, the ASI evidence, and the policy conclusion.
# ---------------------------------------------------------------------------
# The whole abstract environment is replaced by regex rather than by exact match,
# because the original contains typographic quotes and em dashes that are awkward
# to reproduce byte-for-byte in a literal.
ABSTRACT_PATTERN = r'\\begin\{abstract\}.*?\\end\{abstract\}'

ABSTRACT_NEW = r"""\noindent \textit{This report argues for rationalising the basic customs duty on
primary aluminium (HS~7601), on the ground that the present structure taxes conversion
rather than protecting it. The case rests on two independent bodies of evidence.}

\smallskip
\noindent \textit{The first is an estimate of effective protection. Applying a modified
Corden measure to Supply--Use data and partner tariff schedules, we find that the thirteen
downstream product lines HS~7604--7616 carry \textbf{negative} effective protection against
Malaysia, Korea, Japan and Thailand by 2024--25, against a non-preferential benchmark of
$+0.50$. Preferential agreements have removed the duty from the finished good while leaving
it on the metal, so the escalation that ordinarily protects processing instead penalises it.
Because bought-in inputs are 83 per cent of downstream output value, the resulting wedge is
amplified roughly fivefold by the time it reaches value added.}

\smallskip
\noindent \textit{The second is the Annual Survey of Industries. Partitioning the ASI on the
same boundary the tariff schedule uses, we find that a rupee of value added created in
downstream fabrication sustains \textbf{3.1 times} the employment of a rupee created in
primary metal---a result that holds in every one of the twelve clean years, with a median of
3.9. Downstream converts \textbf{38.4 per cent} of value added into wages against 17.6 per
cent upstream, and supports \textbf{151 persons per crore} of estimated corporate tax against
39. Within that aggregate, the single class most exposed to duty-free finished
imports---structural products, which make HS~7610---grew nominal value added by 15 per
cent in eleven years while its workforce did not grow at all. The association is consistent in sign
throughout; we do not claim it is an identified causal effect, and say so.}

\smallskip
\noindent \textit{These findings are set against a demand environment that makes the
distortion more costly each year. Public capital expenditure of INR 12.2 lakh crore in
2026--27, of which INR 2.93 lakh crore is railway capital outlay, generates demand for
extrusions, structural sections and stranded conductor---precisely the lines on which
domestic effective protection is negative. Compounding this, geopolitical chokepoints,
subsidised Chinese competition and the carbon-compliance regimes now taking effect fall
hardest on the segment least able to absorb them. The policy imperative follows: correct the
input duty, and the demand that public investment is already creating can be met from
domestic capacity rather than imported.}"""


# ---------------------------------------------------------------------------
# 2. Introduction — the demand side of the argument. Public capital
#    expenditure generates demand in exactly the disprotected product lines.
# ---------------------------------------------------------------------------
CAPEX_ANCHOR = (
    r"Set against India's broader ambition of becoming a US\$30 trillion economy, "
    r"capturing even a fraction of this trajectory would require the downstream sector to "
    r"expand several-fold---underscoring why the structural disadvantages it currently "
    r"faces carry consequences far beyond the firms directly affected."
)

CAPEX_NEW = CAPEX_ANCHOR + r"""

\paragraph{The demand is already being created, by the public exchequer.} These
projections are not distant forecasts contingent on private appetite. A substantial
part of the incremental demand is being generated now, by budgeted public
expenditure, and it lands with unusual precision on the product lines this report is
about. Capital expenditure in the Union Budget for 2026--27 is set at INR~12.2 lakh
crore, of which \textbf{INR~2.93 lakh crore} is capital outlay on the railways---a
record, and a 5.4 per cent increase on the preceding year---including
INR~52,109~crore on rolling stock alongside seven new high-speed corridors and a
further dedicated freight corridor \cite{budget2027}\footnote{Ministry of Finance,
Government of India. \textit{Union Budget 2026--27}, Expenditure Profile and Demands
for Grants; railway allocations as presented on 1~February 2026.}.

Each of those heads converts into aluminium, and into specific tariff lines. Rolling
stock is the clearest case: aluminium car bodies are at least 30 per cent lighter
than stainless-steel equivalents, which is why the next generation of Indian trainsets
is moving to aluminium construction, and why an order for one hundred aluminium-bodied
Vande Bharat sleeper trainsets has been placed. A metro coach absorbs of the order of
six to eight tonnes of \emph{extruded profiles}---HS~7604---so that a single metro line
of thirty six-coach trains represents something near 1,500 tonnes of extrusion on its
own \cite{railal2026}\footnote{Trade estimates; Titagarh's Pune Metro coaches are
India's only operational aluminium metro fleet. Figures are indicative of order of
magnitude rather than precise engineering specifications.}. The grid tells the same
story through a different line: aluminium is the preferred conductor for overhead
transmission and distribution, and the National Electricity Plan requires inter-regional
transfer capacity of 143,850~MW by 2026--27 against a build-out of some 470~GW of solar
and wind over the decade \cite{cea2024}\footnote{Central Electricity Authority,
\textit{National Electricity Plan, Volume~II: Transmission} (2024), Ministry of Power,
Government of India.}---demand which materialises as stranded wire and cable, HS~7614.
Construction and infrastructure, meanwhile, remain the largest single end-use of Indian
extrusions at roughly 280,000--300,000 tonnes, arriving as structural sections, doors,
windows and fa\c{c}ades: HS~7610.

The significance of this is not that demand is growing. It is \emph{where} the demand
falls. Extrusions (HS~7604), structural products (HS~7610) and stranded conductor
(HS~7614) are among the lines on which Section~\ref{sec:erp} finds effective protection
to be negative, and HS~7610 is the line that the industrial statistics of
Section~\ref{sec:asi_method} show to be stagnant. India's aluminium extrusion
consumption is projected at \textbf{858,000 tonnes in 2026}, up 7.9 per cent in a single
year \cite{alcircle2026b}\footnote{``India's aluminium extrusion demand nears 858,000
tonnes,'' \textit{AL Circle} (2026); 795,000 tonnes in 2025.}. The question a tariff
schedule has to answer is who supplies that growth. On the present structure, a
fabricator buying metal at a duty-inclusive price competes for this business against a
finished import entering at zero duty---so public investment intended to build domestic
industrial capability is, at the margin, underwriting fabrication capacity abroad. That
is a strange result for an expenditure programme of this size to produce, and it is
correctable at the tariff line rather than through further subsidy."""


# ---------------------------------------------------------------------------
# 3. Bibliography entries required by the two patches above.
# ---------------------------------------------------------------------------
NEW_BIBITEMS = r"""
\bibitem{corden1966}
Corden, W. M. (1966).
\textit{The Structure of a Tariff System and the Effective Protective Rate.}
Journal of Political Economy, 74(3), 221--237.

\bibitem{balassa1965}
Balassa, B. (1965).
\textit{Tariff Protection in Industrial Countries: An Evaluation.}
Journal of Political Economy, 73(6), 573--594.

\bibitem{balassa1968}
Balassa, B. (1968).
\textit{Tariff Protection in Industrial Nations and Its Effects on the Exports of
Processed Goods from Developing Countries.}
Canadian Journal of Economics, 1(3), 583--594.

\bibitem{cullen2013}
Cullen, J. M., \& Allwood, J. M. (2013).
\textit{Mapping the Global Flow of Aluminum: From Liquid Aluminum to End-Use Goods.}
Environmental Science \& Technology, 47(7), 3057--3064. doi:10.1021/es304256s.

\bibitem{bertram2009}
Bertram, M., Martchek, K. J., \& Rombach, G. (2009).
\textit{Material Flow Analysis in the Aluminum Industry.}
Journal of Industrial Ecology, 13(5). doi:10.1111/j.1530-9290.2009.00158.x.

\bibitem{bohlin2006}
Bohlin, L., \& Widell, L. M. (2006).
\textit{Estimation of commodity-by-commodity input--output matrices.}
Economic Systems Research, 18(2), 205--215. doi:10.1080/09535310600653164.

\bibitem{gtri2026}
Global Trade Research Initiative (2026).
\textit{India's aluminium trade: primary metal exports and finished-product imports,
FY2025--26.} GTRI Policy Report, June 2026; figures as reported in
\textit{Business Standard}, 18 June 2026.

\bibitem{millerblair}
Miller, R. E., \& Blair, P. D. (2009).
\textit{Input--Output Analysis: Foundations and Extensions}, 2nd ed.
Cambridge University Press, ch. 5.
\bibitem{budget2027}
Ministry of Finance, Government of India (2026).
\textit{Union Budget 2026--27: Expenditure Profile, Expenditure Budget and Demands for
Grants.} New Delhi. Capital expenditure INR 12.2 lakh crore; Ministry of Railways
capital outlay INR 2,93,030 crore.

\bibitem{cea2024}
Central Electricity Authority (2024).
\textit{National Electricity Plan, Volume II: Transmission.}
Ministry of Power, Government of India, New Delhi.

\bibitem{alcircle2026b}
AL Circle (2026).
\textit{India's aluminium extrusion demand nears 858,000 tonnes.}
Industry data series, 2025--26.

\bibitem{railal2026}
Trade sources on aluminium in Indian rolling stock (2025--26), including
\textit{Mobility Outlook} on Titagarh's aluminium metro and Vande Bharat coach
programme, and reported tendering for aluminium-bodied Vande Bharat sleeper trainsets.
"""

ABSTRACT_REPLACEMENT = '\\begin{abstract}\n' + ABSTRACT_NEW + '\n\\end{abstract}'



# ---------------------------------------------------------------------------
# 4. Three further body edits arising from review: the UK series is a
#    non-preferential benchmark rather than a control; the import-parity price
#    spread is one mechanism rather than a demonstrated cause; and the export-mix
#    contrast is appended to the trade paragraph.
# ---------------------------------------------------------------------------
# (i) The UK series is a non-preferential benchmark, not a "control".
OLD_UK = ('\\item \\textbf{The contrast with a non-preferential benchmark is the control.} '
          'The United Kingdom, trading on MFN terms across these years, retained an average '
          'ERP of $+49.6$\\% in 2024--25.')
NEW_UK = ('\\item \\textbf{A non-preferential benchmark holds the method constant.} '
          'The United Kingdom, trading on MFN terms across these years, retained an average '
          'ERP of $+49.6$\\% in 2024--25. It is computed on the same thirteen product lines '
          'with the same estimator as the preferential partners and differs only in that its '
          'goods enter at most-favoured-nation rates; it is a benchmark rather than a control, '
          'and no causal weight is placed on the comparison beyond that.')

# (ii) Import-parity pricing: the duty sustains the spread, it is not shown to cause it.
OLD_IPP = ('upstream producers exploit the 8.25\\% tariff wall to practice \\textit{import-parity '
           'pricing} (IPP), benchmarking domestic prices to the LME plus the import duty and '
           'logistics premiums and thereby sustaining a persistent spread of roughly Rs 30,000 '
           'to Rs 60,000 per tonne over international prices')
NEW_IPP = ('upstream producers are able to price on an \\textit{import-parity} basis (IPP), '
           'benchmarking domestic prices to the LME plus the import duty and logistics premiums, '
           'alongside which a persistent spread of roughly Rs 30,000 to Rs 60,000 per tonne over '
           'international prices has been observed. The duty is one mechanism through which such '
           'a spread can be sustained, since it sets the floor beneath which imported metal '
           'cannot undercut domestic supply; we do not claim it is the sole driver, and a full '
           'decomposition against freight, insurance and physical premia lies outside this '
           'report\'s scope')

# (iii) The export-mix contrast (GTRI, FY2025-26), appended to the trade paragraph.
OLD_TRADE = ('plates) entering the country \\cite{mom_vision2025}\\footnote{Ministry of Mines, '
             'Government of India. (2025). \\textit{Vision Document on Aluminium Metal for India}.}.')
NEW_TRADE = (OLD_TRADE + ' The composition of the two countries\' trade states the policy '
             'difference more plainly than any tariff schedule. Of India\'s roughly US\\$7 '
             'billion of aluminium exports in FY2025--26, \\textbf{61.4 per cent was primary '
             'metal}; the corresponding share for China is \\textbf{2.8 per cent}, value-added '
             'products making up the remaining 97.2 per cent \\cite{gtri2026}. In the same year '
             'India imported approximately US\\$4.1 billion of \\emph{finished} aluminium '
             'goods---cables and conductors, packaging, engineering goods and automotive '
             'components---with about a quarter entering at low or zero duty under preferential '
             'agreements \\cite{gtri2026}. India exports the metal and imports the goods made '
             'from it.')

PATCHES = [
    ('introduction capex paragraph', CAPEX_ANCHOR, CAPEX_NEW),
    ('UK non-preferential benchmark', OLD_UK, NEW_UK),
    ('import-parity price spread', OLD_IPP, NEW_IPP),
    ('export-mix contrast', OLD_TRADE, NEW_TRADE),
]
