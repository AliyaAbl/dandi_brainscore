#!/bin/bash

#SBATCH --time=10:00:00
#SBATCH --ntasks=1
#SBATCH -N 1
#SBATCH --mem=10G
#SBATCH --output=output.log        # Specify the output file
#SBATCH --error=error.log          # Specify the error file


hostname
echo 'Opening python'
python main.py 
