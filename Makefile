# Reproduce everything. Requires python 3.9+ and xelatex.
PY := python
TEXFLAGS := -interaction=nonstopmode -output-directory=build

.PHONY: all series verify tariff report clean

all: series verify tariff report

series:            ## build every series and emit plotting coordinates
	$(PY) src/build_series.py

verify:            ## re-derive every plotted point and quoted statistic
	$(PY) src/verify_figures.py

tariff:            ## public-finance arithmetic and sensitivity
	$(PY) src/tariff_gst.py

report: series     ## assemble and typeset the report (three passes for refs)
	$(PY) src/build_report.py
	$(PY) -c "import subprocess,sys; [subprocess.run(['xelatex','-interaction=nonstopmode','-output-directory=build','build/aluminium_report_downstream.tex'],stdout=subprocess.DEVNULL) for _ in range(3)]"
	@echo "build/aluminium_report_downstream.pdf"

clean:
	rm -rf build/*.aux build/*.log build/*.out build/*.toc
