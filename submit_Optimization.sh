#!/bin/sh

host=${1}
year=${2}
numVars=${3}
option=${4}
dataset=${5}

source /cvmfs/cms.cern.ch/cmsset_default.sh

export SCRAM_ARCH=slc7_amd64_gcc630
eval `scramv1 runtime -sh`

source /cvmfs/sft.cern.ch/lcg/contrib/gcc/7.3.0/x86_64-centos7-gcc7-opt/setup.sh
source /cvmfs/sft.cern.ch/lcg/app/releases/ROOT/6.16.00/x86_64-centos7-gcc48-opt/bin/thisroot.sh

if [ $host == 'BRUX' ] || [ $host == 'brux' ] || [ $host == 'Brux' ] && [ [ $year = '2017' ] || [ $year = '2018' ] ]
then
  python TMVAClassification_OptimizationWrapper -w brux -n $numVars -o $option -y $year -d $dataset
elif [ $host == 'LPC' ] || [ $host == 'lpc' ] || [ $host == 'Lpc' ] && [ [ $year = '2017' ] || [ $year = '2018' ] ]
then
  python TMVAClassification_OptimizationWrapper.py -w lpc -n $numVars -o $option -y $year -d $dataset
else
  echo Invalid or No Options Used. Need to include "host" and "number of variables". 
  echo Example submissions: "./submit_OptimizationWrapper.sh lpc 2017 20 1 dataset" or "./submit_OptimizationWrapper.sh brux 2018 20 0 dataset"
fi
