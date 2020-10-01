#!/bin/sh

eos_username=${1}
eos_folder=${2}
year=${3}
seed_vars=${4}

echo "Setting Up TTTT Job"

# Enter environment
source /cvmfs/cms.cern.ch/cmsset_default.sh

# Copy and Unpack Resources
xrdcp -s root://cmseos.fnal.gov//store/user/$eos_username/CMSSW946.tgz .
tar -xf CMSSW946.tgz
rm CMSSW946.tgz

cd ./CMSSW_9_4_6_patch1/src/TTTT_TMVA_DNN

export SCRAM_ARCH=slc7_amd64_gcc630
eval `scramv1 runtime -sh`
source /cvmfs/sft.cern.ch/lcg/app/releases/ROOT/6.16.00/x86_64-centos7-gcc48-opt/bin/thisroot.sh

cd ./TTTT_TMVA_DNN/

echo "Setup finished."

python remote.py $year $seed_vars
