#!/bin/sh

host=${1}

source /cvmfs/cms.cern.ch/cmsset_default.sh

export SCRAM_ARCH=slc7_amd64_gcc630
eval `scramv1 runtime -sh`

source /cvmfs/sft.cern.ch/lcg/contrib/gcc/7.3.0/x86_64-centos7-gcc7-opt/setup.sh
source /cvmfs/sft.cern.ch/lcg/app/releases/ROOT/6.16.00/x86_64-centos7-gcc48-opt/bin/thisroot.sh

if [ $host == 'BRUX' ] || [ $host == 'brux' ] || [ $host == 'Brux' ] 
then
  python ./BRUX/VariableImportanceBRUX_resubmit.py # running on BRUX clusters
elif [ $host == 'LPC' ] || [ $host == 'lpc' ] || [ $host == 'Lpc' ]
then
  python ./LPC/VariableImportanceLPC_resubmit.py   # running on LPC clusters, use this if input variables > 20
else
  echo Invalid or No Option Used. Submit as "./resubmit_VariableImportance.sh BRUX" or "./resubmit_VariableImportance.sh LPC".
fi
