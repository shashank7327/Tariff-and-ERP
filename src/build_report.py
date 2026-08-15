"""Assemble the report from its parts.

I keep Section 4 and the methodology appendix as separate files and splice them into
the base report at build time. That way the section I am actively working on is not
buried in a 1,700-line document, and the assembly is deterministic: the same inputs
always produce the same output, and every anchor is asserted so a silent
mis-splice is impossible.

    python src/build_report.py
    xelatex -output-directory=build build/aluminium_report_downstream.tex   (x3)
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from paths import TEX, BUILD
from report_patches import (PATCHES, NEW_BIBITEMS,
                            ABSTRACT_PATTERN, ABSTRACT_REPLACEMENT)

BASE = TEX / 'aluminium_report.tex'
SECTION = TEX / 'asi_section_downstream.tex'
APPENDIX = TEX / 'asi_appendix_methodology.tex'
OUT = BUILD / 'aluminium_report_downstream.tex'

# Section 4 occupies these lines of the base file (1-indexed, inclusive of the
# first, exclusive of the last).
SECTION_START, SECTION_END = 615, 847


def strip_header(path):
    """Drop the leading comment block, keep everything else.

    Everything else includes the \\pgfplotsset and \\tikzset figure styles that sit
    above \\section{}, which is why I do not simply skip to the first \\section.
    """
    lines = path.read_text(encoding='utf-8').split('\n')
    start = next(i for i, l in enumerate(lines)
                 if l.strip() and not l.lstrip().startswith('%'))
    return '\n'.join(lines[start:]).rstrip()


def add_label(lines, needle, label):
    for i, l in enumerate(lines):
        if l.startswith(needle):
            if label not in lines[i + 1]:
                lines.insert(i + 1, label)
            return
    raise SystemExit(f'anchor not found: {needle}')


def main():
    src = BASE.read_text(encoding='utf-8').split('\n')
    section = strip_header(SECTION).split('\n')

    assert any(l.startswith('\\pgfplotsset') for l in section), 'figure styles lost'
    assert any(l.startswith('\\tikzset') for l in section), 'series styles lost'
    assert src[SECTION_START - 1].startswith('\\section{Policy Plight'), \
        'section 4 does not start where expected'
    assert src[SECTION_END - 1].startswith('\\subsection{Compliance Headwinds'), \
        'section 4 does not end where expected'

    out = src[:SECTION_START - 1] + section + [''] + src[SECTION_END - 1:]

    add_label(out, '\\subsection{Scope and Objective: Focus on HS Codes 7601--7616}',
              '\\label{sec:scope}')
    add_label(out, '\\section{Effective Rate of Protection and the role of Inverted Duty Structure}',
              '\\label{sec:erp}')
    add_label(out, '\\section{Appendix: Technical Framework of ERP Analysis}',
              '\\label{app:erp}')

    txt = '\n'.join(out)

    txt, n = re.subn(ABSTRACT_PATTERN, lambda _m: ABSTRACT_REPLACEMENT, txt,
                     count=1, flags=re.S)
    assert n == 1, 'abstract environment not found'
    print('  patched: abstract')

    for label, old, new in PATCHES:
        assert txt.count(old) == 1, f'anchor not found or not unique: {label}'
        txt = txt.replace(old, new, 1)
        print(f'  patched: {label}')

    anchor = '\\section{Appendix: Supplementary Figures}'
    assert txt.count(anchor) == 1, 'supplementary-figures anchor not found'
    txt = txt.replace(anchor, strip_header(APPENDIX) + '\n\n\\newpage\n' + anchor)

    assert txt.count('\\end{thebibliography}') == 1
    txt = txt.replace('\\end{thebibliography}',
                      NEW_BIBITEMS + '\n\\end{thebibliography}')

    # DejaVu Sans is not installed everywhere; fall back rather than fail.
    txt = txt.replace(
        '\\setmainfont{DejaVu Sans}',
        '\\IfFontExistsTF{DejaVu Sans}\n'
        '  {\\setmainfont{DejaVu Sans}}\n'
        '  {\\IfFontExistsTF{Verdana}{\\setmainfont{Verdana}}{\\setmainfont{Arial}}}')

    OUT.write_text(txt, encoding='utf-8')
    print(f'{OUT} written: {len(out)} lines')


if __name__ == '__main__':
    main()
