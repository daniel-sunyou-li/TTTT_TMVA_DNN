#!/bin/bash

YEAR=${1}
CATEGORY=${2}
VARIABLE=${3}
EOSDIR=${4}
EOS_USERNAME=${5}

source /cvmfs/cms.cern.ch/cmsset_default.sh

xrdcp -s root://cmseos.fnal.gov//store/user/$EOS_USERNAME/CMSSW946.tgz
tar -xf CMSSW946.tgz
rm CMSSW946.tgz

cd ./CMSSW_9_4_6_patch1/src/TTTT_TMVA_DNN

eval `scramv1 runtime -sh`
source /cvmfs/sft.cern.ch/lcg/app/releases/ROOT/6.16.00/x86_64-centos7-gcc48-opt/bin/thisroot.sh

python hists.py -y $YEAR -v $VARIABLE -c $CATEGORY

xrdcp -f sig_$VARIABLE\.pkl root://cmseos.fnal.gov//store/user/$eosUserName/$EOSDIR
xrdcp -f bkg_$VARIABLE\.pkl root://cmseos.fnal.gov//store/user/$eosUserName/$EOSDIR
xrdcp -f data_$VARIABLE\.pkl root://cmseos.fnal.gov//store/user/$eosUserName/$EOSDIR
