# CMEE Coursework Summary

- **Author**: Yanfeng Wang (yw4524@ic.ac.uk)  
- **Date**: October 11th – December 13th, 2024  

---

## Overview

This repository contains coursework for the CMEE program, spanning Weeks 1 through 4. Each week focuses on different programming skills, tools, and problem-solving techniques using **Shell scripts**, **Python**, **R**, and **LaTeX**. The tasks include data processing, visualization, statistical analysis, file operations, debugging, and scientific reporting.

---

## Directory Structure

- **`code/`**: Contains all script files (e.g., `.sh`, `.py`, `.R`, `.tex`).  
- **`data/`**: Input files used by the scripts.  
- **`results/`**: Output files generated by the scripts (e.g., CSVs, PDFs, plots).  
- **`sandbox/`**: A workspace for temporary testing and debugging.  

---

## Installation

1. Clone this repository to your local machine:
   ```bash
   git clone https://github.com/your-username/CMEECoursework.git
   cd CMEECoursework
   ```

2. Ensure execution permissions for the scripts:
   ```bash
   chmod +x code/*.sh
   chmod +x code/*.py
   chmod +x code/*.R
   ```

3. Install required dependencies:
   - **Shell Environment**: Use a Bash-compatible shell.  
   - **Python**: Ensure Python 3 is installed with required libraries (`pickle`, etc.).  
   - **R**: Install R (version 4.0 or higher) and required packages:
     ```R
     install.packages(c("ggplot2", "reshape2", "broom"))
     ```

4. Compile LaTeX files using a LaTeX editor or `pdflatex` for reports.

---

## Workflow

1. Place input files in the `data/` directory.  
2. Run scripts from the `code/` directory or repository root.  
3. Output files will be saved in the `results/` directory.  
4. Use the `sandbox/` directory for testing or debugging.  

---

## Week Highlights

### **Week 1: Shell Scripting**
- **Focus**: File operations (e.g., format conversion, concatenation).  
- **Key Scripts**:  
  - `csvtospace.sh`: Converts CSV files to space-separated format.  
  - `tabtocsv.sh`: Converts tab-delimited files to CSV format.  
  - `ConcatenateTwoFiles.sh`: Merges two files into one.  

### **Week 2: Python Programming**
- **Focus**: Data processing, debugging, and control flow.  
- **Key Scripts**:  
  - `python_align_seqs.py`: Aligns DNA sequences and calculates the best match.  
  - `oaks_debugme.py`: Filters oak species data from a dataset.  
  - `control_flow.py`: Demonstrates control structures and prime number identification.  

### **Week 3: R Programming**
- **Focus**: Data analysis, visualization, and optimization.  
- **Key Scripts**:  
  - `apply1.R`: Calculates row-wise and column-wise statistics for a matrix.  
  - `Girko.R`: Visualizes eigenvalues of a matrix in the complex plane.  
  - `TreeHeight.R`: Computes tree heights using angles and distances.  

### **Week 4: R and LaTeX**
- **Focus**: Statistical analysis and scientific reporting.  
- **Key Scripts**:  
  - `Florida.R`: Analyzes temperature trends in Key West, Florida, and visualizes results.  
  - `PP_Regress.R`: Performs regression analysis on predator-prey data.  
  - `Florida_Correlation.tex`: A LaTeX report summarizing the statistical findings.  
