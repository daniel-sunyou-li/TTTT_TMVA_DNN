#!/bin/sh

inputDir=${1}
resultDir=${2}
fileName=${3}
condorDir=${4}
outName=$fileName\_step3.root

source /cvmfs/cms.cern.ch/cmsset_default.sh
export SCRAM_ARCH=slc7_amd64_gcc630
eval `scramv1 runtime -sh`

source /cvmfs/sft.cern.ch/lcg/contrib/gcc/7.3.0/x86_64-centos7-gcc7-opt/setup.sh
source /cvmfs/sft.cern.ch/lcg/app/releases/ROOT/6.16.00/x86_64-centos7-gcc48-opt/bin/thisroot.sh

python step3.py -i $inputDir -f $fileName -o $outName

echo Transferring $outName to $inputDir/step3/ ...
cp $outName $inputDir/step3/
