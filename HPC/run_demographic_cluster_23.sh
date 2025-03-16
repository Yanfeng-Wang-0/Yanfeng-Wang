#!/bin/bash
#PBS -lwalltime=12:00:00
#PBS -lselect=1:ncpus=1:mem=1gb


module load R
echo "R running"
cd /rds/general/user/yw4524/home/
Rscript yw4524_HPC_2024_neutral_cluster.R
echo "R work done"
