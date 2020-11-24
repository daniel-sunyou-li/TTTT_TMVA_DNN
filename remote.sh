#!/bin/sh

eos_username=${1}
year=${2}
seed_vars=${3}
njets=${4}
nbjets=${5}

echo ">> Setting Up TTTT Job"

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

echo "[OK ] Setup finished."

python remote.py -y $year -s $seed_vars -nj $njets -nb $nbjets
