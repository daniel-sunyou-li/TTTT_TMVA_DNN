#!/bin/sh

host=${1}
numVars=${2}

if [ $host == 'BRUX' ] || [ $host == 'brux' ] || [ $host == 'Brux' ]
then
  source /cvmfs/cms.cern.ch/cmsset_default.sh
  export SCRAM_ARCH=slc7_amd64_gcc630
  eval `scramv1 runtime -sh`
  source /cvmfs/sft.cern.ch/lcg/contrib/gcc/7.3.0/x86_64-centos7-gcc7-opt/setup.sh
  source /cvmfs/sft.cern.ch/lcg/app/releases/ROOT/6.16.00/x86_64-centos7-gcc48-opt/bin/thisroot.sh
  python TMVAClassification_OptimizationWrapper brux $numVars
elif [ $host == 'LPC' ] || [ $host == 'lpc' ] || [ $host == 'Lpc' ]
then
  source /cvmfs/cms.cern.ch/cmsset_default.csh
  setenv SCRAM_ARCH slc7_amd64_gcc630
  eval `scramv1 runtime -csh`
  source /cvmfs/sft.cern.ch/lcg/contrib/gcc/7.3.0/x86_64-centos7-gcc7-opt/setup.csh
  source /cvmfs/sft.cern.ch/lcg/app/releases/ROOT/6.16.00/x86_64-centos7-gcc48-opt/bin/thisroot.csh
  python TMVAClassification_OptimizationWrapper.py lpc $numVars
else
  echo Invalid or No Options Used. Need to include "host" and "number of variables". 
  echo Example submissions: "./submit_OptimizationWrapper.sh lpc 20" or "./submit_OptimizationWrapper.sh brux 20"
fi
