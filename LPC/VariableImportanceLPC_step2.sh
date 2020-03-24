#!/bin/sh

str_xbitset=${1}
eosDir=${2}
eosUserName="dali" # change me

source /cvmfs/cms.cern.ch/cmsset_default.sh

xrdcp -s root://cmseos.fnal.gov//store/user/$eosUserName/CMSSW946.tgz .
tar -xf CMSSW946.tgz
rm CMSSW946.tgz

xrdcp -s root://cmseos.fnal.gov//store/user/$eosUserName/$eosDir/TTTT_TuneCP5_PSweights_13TeV-amcatnlo-pythia8_split0.root .
xrdcp -s root://cmseos.fnal.gov//store/user/$eosUserName/$eosDir/TTToSemiLeptonic_TuneCP5_PSweights_13TeV-powheg-pythia8_HT0Njet0_ttbb_split0.root .
xrdcp -s root://cmseos.fnal.gov//store/user/$eosUserName/$eosDir/TTToSemiLeptonic_TuneCP5_PSweights_13TeV-powheg-pythia8_HT0Njet0_ttcc_split0.root .
xrdcp -s root://cmseos.fnal.gov//store/user/$eosUserName/$eosDir/TTToSemiLeptonic_TuneCP5_PSweights_13TeV-powheg-pythia8_HT0Njet0_ttjj_1_split0.root .
xrdcp -s root://cmseos.fnal.gov//store/user/$eosUserName/$eosDir/TTToSemiLeptonic_TuneCP5_PSweights_13TeV-powheg-pythia8_HT0Njet0_ttjj_2_split0.root .
xrdcp -s root://cmseos.fnal.gov//store/user/$eosUserName/$eosDir/TTToSemiLeptonic_TuneCP5_PSweights_13TeV-powheg-pythia8_HT0Njet0_ttjj_3_split0.root .
xrdcp -s root://cmseos.fnal.gov//store/user/$eosUserName/$eosDir/TTToSemiLeptonic_TuneCP5_PSweights_13TeV-powheg-pythia8_HT0Njet0_ttjj_4_split0.root .
xrdcp -s root://cmseos.fnal.gov//store/user/$eosUserName/$eosDir/TTToSemiLeptonic_TuneCP5_PSweights_13TeV-powheg-pythia8_HT0Njet0_ttjj_5_split0.root .
xrdcp -s root://cmseos.fnal.gov//store/user/$eosUserName/$eosDir/TTToSemiLepton_HT500Njet9_TuneCP5_PSweights_13TeV-powheg-pythia8_ttbb_split0.root .
xrdcp -s root://cmseos.fnal.gov//store/user/$eosUserName/$eosDir/TTToSemiLepton_HT500Njet9_TuneCP5_PSweights_13TeV-powheg-pythia8_ttcc_split0.root .
xrdcp -s root://cmseos.fnal.gov//store/user/$eosUserName/$eosDir/TTToSemiLepton_HT500Njet9_TuneCP5_PSweights_13TeV-powheg-pythia8_ttjj_split0.root .
xrdcp -s root://cmseos.fnal.gov//store/user/$eosUserName/$eosDir/TTTo2L2Nu_TuneCP5_PSweights_13TeV-powheg-pythia8_ttbb_split0.root .
xrdcp -s root://cmseos.fnal.gov//store/user/$eosUserName/$eosDir/TTTo2L2Nu_TuneCP5_PSweights_13TeV-powheg-pythia8_ttcc_split0.root .
xrdcp -s root://cmseos.fnal.gov//store/user/$eosUserName/$eosDir/TTTo2L2Nu_TuneCP5_PSweights_13TeV-powheg-pythia8_ttjj_split0.root .
xrdcp -s root://cmseos.fnal.gov//store/user/$eosUserName/$eosDir/TTToHadronic_TuneCP5_PSweights_13TeV-powheg-pythia8_ttbb_split0.root .
xrdcp -s root://cmseos.fnal.gov//store/user/$eosUserName/$eosDir/TTToHadronic_TuneCP5_PSweights_13TeV-powheg-pythia8_ttcc_split0.root .
xrdcp -s root://cmseos.fnal.gov//store/user/$eosUserName/$eosDir/TTToHadronic_TuneCP5_PSweights_13TeV-powheg-pythia8_ttjj_split0.root .

mv *.root ./CMSSW_9_4_6_patch1/src/TTTT_TMVA_DNN/

cd ./CMSSW_9_4_6_patch1/src

export SCRAM_ARCH=slc7_amd64_gcc630
eval `scramv1 runtime -sh`

source /cvmfs/sft.cern.ch/lcg/contrib/gcc/7.3.0/x86_64-centos7-gcc7-opt/setup.sh
source /cvmfs/sft.cern.ch/lcg/app/releases/ROOT/6.16.00/x86_64-centos7-gcc48-opt/bin/thisroot.sh

cd ./TTTT_TMVA_DNN/

python TMVAClassification_VariableImportance.py -s $str_xbitset -w lpc
