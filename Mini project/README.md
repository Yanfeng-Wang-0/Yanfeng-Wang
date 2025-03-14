# CMEE Coursework: Microbial Population Growth

## Author
- **Name**: Yanfeng Wang (yw4524@ic.ac.uk)  
- **Date**: March 3rd – March 14th, 2025  

## Overview
This repository contains mini project for the CMEE program, specifically focusing on microbial growth modeling using various mathematical techniques. The project includes data preprocessing, model fitting, and evaluation using multiple modeling approaches.

## Project Workflow
1. **Data Cleaning**: Prepares the dataset by filtering and transforming microbial growth data.
2. **Model Fitting**: Applies various growth models (Exponential, Gompertz, Logistic, Power, GAM, Neural Network, Random Forest) to the cleaned dataset.
3. **Performance Evaluation**: Compares models based on R², AIC, and BIC metrics.
4. **Report Generation**: Compiles a LaTeX report summarizing the results.

## Directory Structure
- **`Code/`**: Contains all script files (e.g., `.sh`, `.R`, `.tex`).  
- **`Data/`**: Contains raw and cleaned datasets.  
- **`Results/`**: Stores output files (e.g., CSVs, .png plots).  
- **`Sandbox/`**: A workspace for temporary testing and debugging.  

## Installation
### Prerequisites
Ensure the following software is installed:
- **R** (version 4.0 or higher)
- **LaTeX distribution** (for compiling reports)
- **Bash shell** (for running automation scripts)

### R Package Installation
Run the following command to install dependencies:
```r
install.packages(c("dplyr", "readr", "ggplot2", "mgcv", "minpack.lm", "nnet", "randomForest", "caret", "Metrics", "tidyr", "Rlof", "car"))
```

## Running the Project

### Running with Shell Script
To execute the full workflow using the shell script, run:
```bash
bash run.sh
```

This will:

 1. Run final.R to clean data, fit models, and generate comparison results.
 2. Compile the LaTeX report with model evaluation results.

If run.sh fails or is not executable, you can manually execute the commands from the script:
```bash
# Run the R script
Rscript final.R || { echo "Running final.R failed!"; exit 1; }

# Compile the LaTeX report
pdflatex report.tex || { echo "Running LaTeX failed on the first attempt!"; exit 1; }
bibtex report || { echo "Running BibTeX failed!"; exit 1; }
pdflatex report.tex || { echo "Running LaTeX failed on the second attempt!"; exit 1; }
pdflatex report.tex || { echo "Running LaTeX failed on the third attempt!"; exit 1; }

# Open the report
xdg-open report.pdf &

echo "All done!"
```

If xdg-open does not work on your system, manually open report.pdf using your preferred PDF viewer.

## Output Files
- **`Data/Cleaned_LogisticGrowthData.csv`**: Preprocessed dataset.
- **`Results/Per_ID_Comparison/`**: Directory with model comparison plots.
- **`Results/model_comparison_metrics.csv`**: Model performance metrics.
- **`Results/model_comparison_summary.csv`**: Summary ranking models by performance.
- **`report.pdf`**: Final report summarizing the findings.

## Troubleshooting
- If `final.R` fails, ensure all required R packages are installed.
- If `pdflatex` fails, verify that LaTeX is correctly installed and `report.tex` is error-free.


