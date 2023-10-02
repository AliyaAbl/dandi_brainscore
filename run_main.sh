#!/bin/bash

#SBATCH --job-name=nwb_conversion
#SBATCH --time=10:00:00
#SBATCH --ntasks=1
#SBATCH --mem=8000
#SBATCH --exclude=node[066,067,115]
#SBATCH -c1
#SBATCH -p dicarlo
#SBATCH --mail-type=ALL
#SBATCH --output=output.log        # Specify the output file
#SBATCH --error=error.log          # Specify the error file

hostname
python main.py 
