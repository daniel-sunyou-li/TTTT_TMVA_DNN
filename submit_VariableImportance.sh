#!/bin/sh

host=${1}
year=${2}
seeds=${3}
corrCut=${4}

source /cvmfs/cms.cern.ch/cmsset_default.sh

export SCRAM_ARCH=slc7_amd64_gcc630
eval `scramv1 runtime -sh`

source /cvmfs/sft.cern.ch/lcg/contrib/gcc/7.3.0/x86_64-centos7-gcc7-opt/setup.sh
source /cvmfs/sft.cern.ch/lcg/app/releases/ROOT/6.16.00/x86_64-centos7-gcc48-opt/bin/thisroot.sh

if [ $host = 'BRUX' ] || [ $host = 'brux' ] || [ $host = 'Brux' ] && [ [ $year = '2017' ] || [ $year = '2018' ] ]
then
  if [ $seeds = '' ] || [ $corrCut = '' ]
    python ./BRUX/VariableImportanceBRUX_step1.py $year # running on BRUX clusters
  else
    python ./BRUX/VariableImportanceBRUX_step1.py $year $seeds $corrCut
  fi
elif [ $host = 'LPC' ] || [ $host = 'lpc' ] || [ $host = 'Lpc' ] && [ [ $year = '2017' ] || [ $year = '2018' ] ]
then
  if [ $seeds = '' ] || [ $corrCut = '' ]
  then
    python ./LPC/VariableImportanceLPC_step1.py $year # running on LPC clusters, use this if input variables > 20 
  else
    python ./LPC/VariableImportanceLPC_step1.py $year $seeds $corrCut
  fi
else
  echo Invalid or No Option Used. Submit as "./submit_VariableImportance.sh BRUX 2017 100 80" or "./submit_VariableImportance.sh LPC 2017 100 80".
fi
