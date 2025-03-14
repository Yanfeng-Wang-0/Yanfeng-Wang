#!/bin/bash

set -e

echo "Running: final.R"
Rscript final.R || { echo "Running data_cleaning.R fail！"; exit 1; }

echo "Running: references.bib"
pdflatex report.tex || { echo "Running LaTeX fail 1st！"; exit 1; }
bibtex report || { echo "Running BibTeX fal！"; exit 1; }

echo "Running: report.pdf"
pdflatex report.tex || { echo "Running LaTeX fail 2nd！"; exit 1; }
pdflatex report.tex || { echo "Running LaTeX fail 3rd！"; exit 1; }

echo "All done！"
