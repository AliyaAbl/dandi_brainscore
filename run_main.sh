#!/bin/bash

#SBATCH --job-name=nwb_file_creation
#SBATCH --array=0-55
#SBATCH --time=01:00:00
#SBATCH --output=spikes.txt
#SBATCH --ntasks=1
#SBATCH --mem=8000
#SBATCH --exclude=node[066,067,115]
#SBATCH -c4
#SBATCH -p dicarlo
#SBATCH --output=output.log        # Specify the output file
#SBATCH --error=error.log          # Specify the error file

hostname

python main.py $SLURM_ARRAY_TASK_ID ${*:1}
