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
- **`code/`**: Contains all script files (e.g., `.sh`, `.R`, `.tex`).  
- **`data/`**: Contains raw and cleaned datasets.  
- **`results/`**: Stores output files (e.g., CSVs, .png plots).  
- **`sandbox/`**: A workspace for temporary testing and debugging.  

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