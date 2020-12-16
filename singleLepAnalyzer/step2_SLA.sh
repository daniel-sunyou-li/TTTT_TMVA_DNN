#!/bin/bash

YEAR=${1}
JSON=${2}
EOSDIR=${3}
EOS_USERNAME=${4}

source /cvmfs/cms.cern.ch/cmsset_default.sh

xrdcp -s root://cmseos.fnal.gov//store/user/$EOS_USERNAME/CMSSW946.tgz
tar -xf CMSSW946.tgz
rm CMSSW946.tgz

cd ./CMSSW_9_4_6_patch1/src/TTTT_TMVA_DNN

eval `scramv1 runtime -sh`

python templates.py -y $YEAR -j $JSON
