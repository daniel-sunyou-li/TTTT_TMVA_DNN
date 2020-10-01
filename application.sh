#!/bin/sh

condorDir=${1}
fileName=${2}
outputDir=${3}

source /cvmfs/cms.cern.ch/cmsset_default.sh
source /cvmfs/sft.cern.ch/lcg/contrib/gcc/7.3.0/x86_64-centos7-gcc7-opt/setup.sh

python step3.py -i $condorDir -f $fileName -o $outputDir
