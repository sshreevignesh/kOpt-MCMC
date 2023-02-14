#!/bin/bash
#SBATCH -A research
#SBATCH -n 2
#SBATCH --mem-per-cpu=2048
#SBATCH --mail-type=END
#SBATCH --time=4-00:00:00
#SBATCH --array=1-30

for iter in 500000 1000000 3000000 5000000
do
for i in {0..101..10}
do	
	python3 newmcmcmultikopt.py $SLURM_ARRAY_TASK_ID $i $iter 95
done
done
