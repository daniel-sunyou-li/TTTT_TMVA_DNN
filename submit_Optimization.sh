#/bin/csh

source /cvmfs/cms.cern.ch/cmsset_default.csh

setenv SCRAM_ARCH slc7_amd64_gcc630
#export SCRAM_ARCH=slc7_amd64_gcc630
eval `scramv1 runtime -csh`

source /cvmfs/sft.cern.ch/lcg/contrib/gcc/7.3.0/x86_64-centos7-gcc7-opt/setup.csh
source /cvmfs/sft.cern.ch/lcg/app/releases/ROOT/6.16.00/x86_64-centos7-gcc48-opt/bin/thisroot.csh

python TMVAClassification_OptimizationWrapper.py
