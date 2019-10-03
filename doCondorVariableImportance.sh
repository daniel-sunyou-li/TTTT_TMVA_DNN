#!/bin/sh

runDir=${1}
fileName=${2}
method=${3}
vListKey=${4}
nTrees=${5}
mDepth=${6}
str_xbitset=${7}

source /cvmfs/cms.cern.ch/cmsset_default.sh

cd $runDir
export SCRAM_ARCH=slc7_amd64_gcc630
eval `scramv1 runtime -sh`

source /cvmfs/sft.cern.ch/lcg/contrib/gcc/7.3.0/x86_64-centos7-gcc7-opt/setup.sh
source /cvmfs/sft.cern.ch/lcg/app/releases/ROOT/6.16.00/x86_64-centos7-gcc48-opt/bin/thisroot.sh

# python TMVAClassification.py -m $method -l $vListKey -n $nTrees -d $mDepth $str_xbitset

python TMVAClassification_VarImportance.py -m $method -l $vListKey -n $nTrees -d $mDepth -s $str_xbitset
