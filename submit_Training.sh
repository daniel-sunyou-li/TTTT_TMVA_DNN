#!/bin/sh

host=${1}
option=${2}
dataset=${3}

source /cvmfs/cms.cern.ch/cmsset_default.sh

export SCRAM_ARCH=slc7_amd64_gcc630

eval `scramv1 runtime -sh`

source /cvmfs/sft.cern.ch/lcg/contrib/gcc/7.3.0/x86_64-centos7-gcc7-opt/setup.sh
source /cvmfs/sft.cern.ch/lcg/app/releases/ROOT/6.16.00/x86_64-centos7-gcc48-opt/bin/thisroot.sh

if [ $host == 'BRUX' ] || [ $host == 'brux' ] || [ $host == 'Brux' ]
then
  if [ $option == '0' ]
  then
    python TMVAClassification_Training.py -w brux -o 0 -d dataset
  elif [ $option == '1' ]  
  then
    python TMVAClassification_Training.py -w brux -o 1 -d $dataset
  fi
elif [ $host == 'LPC' ] || [ $host == 'lpc' ] || [ $host == 'Lpc' ]
then
  if [ $option == '0' ]
  then
    python TMVAClassification_Training.py -w lpc -o 0 -d dataset
  elif [ $option == '1' ]
  then
    python TMVAClassification_Training.py -w lpc -o 1 -d $dataset
  fi
else
  echo Invalid or No Options Used.  Need to include "host" , "option" and "dataset"
  echo Example submissions: "./submit_Training.sh brux 0" or "./submit_Training.sh lpc 1 dataset" 
fi

