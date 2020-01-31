#!/bin/sh

runDir=${1}
method=${2}
tag=${3}
str_xbitset=${4}

source /cvmfs/cms.cern.ch/cmsset_default.sh

xrdcp -s root://cmseos.fnal.gov//store/user/dsunyou/CMSSW946.tgz
tar -xf CMSSW946.tgz
rm CMSSW946.tgz

xrdcp -s root://cmseos.fnal.gov//store/user/dsunyou/TTTT_TuneCP5_PSweights_13TeV-amcatnlo-pythia8_hadd.root .
xrdcp -s root://cmseos.fnal.gov//store/user/dsunyou/TTToSemiLeptonic_TuneCP5_PSweights_13TeV-powheg-pythia8_HT0Njet0_ttbb_hadd.root .
xrdcp -s root://cmseos.fnal.gov//store/user/dsunyou/TTToSemiLeptonic_TuneCP5_PSweights_13TeV-powheg-pythia8_HT0Njet0_ttcc_hadd.root .
xrdcp -s root://cmseos.fnal.gov//store/user/dsunyou/TTToSemiLeptonic_TuneCP5_PSweights_13TeV-powheg-pythia8_HT0Njet0_ttjj_1_hadd.root .
#xrdcp -s root://cmseos.fnal.gov//store/user/dsunyou/TTToSemiLeptonic_TuneCP5_PSweights_13TeV-powheg-pythia8_HT0Njet0_ttjj_2_hadd.root .
#xrdcp -s root://cmseos.fnal.gov//store/user/dsunyou/TTToSemiLeptonic_TuneCP5_PSweights_13TeV-powheg-pythia8_HT0Njet0_ttjj_3_hadd.root .
#xrdcp -s root://cmseos.fnal.gov//store/user/dsunyou/TTToSemiLeptonic_TuneCP5_PSweights_13TeV-powheg-pythia8_HT0Njet0_ttjj_4_hadd.root .
#xrdcp -s root://cmseos.fnal.gov//store/user/dsunyou/TTToSemiLeptonic_TuneCP5_PSweights_13TeV-powheg-pythia8_HT0Njet0_ttjj_5_hadd.root .
xrdcp -s root://cmseos.fnal.gov//store/user/dsunyou/TTToSemiLepton_HT500Njet9_TuneCP5_PSweights_13TeV-powheg-pythia8_ttbb_hadd.root .
xrdcp -s root://cmseos.fnal.gov//store/user/dsunyou/TTToSemiLepton_HT500Njet9_TuneCP5_PSweights_13TeV-powheg-pythia8_ttcc_hadd.root .
xrdcp -s root://cmseos.fnal.gov//store/user/dsunyou/TTToSemiLepton_HT500Njet9_TuneCP5_PSweights_13TeV-powheg-pythia8_ttjj_hadd.root .
xrdcp -s root://cmseos.fnal.gov//store/user/dsunyou/TTTo2L2Nu_TuneCP5_PSweights_13TeV-powheg-pythia8_ttbb_hadd.root .
xrdcp -s root://cmseos.fnal.gov//store/user/dsunyou/TTTo2L2Nu_TuneCP5_PSweights_13TeV-powheg-pythia8_ttcc_hadd.root .
xrdcp -s root://cmseos.fnal.gov//store/user/dsunyou/TTTo2L2Nu_TuneCP5_PSweights_13TeV-powheg-pythia8_ttjj_hadd.root .
xrdcp -s root://cmseos.fnal.gov//store/user/dsunyou/TTToHadronic_TuneCP5_PSweights_13TeV-powheg-pythia8_ttbb_hadd.root .
xrdcp -s root://cmseos.fnal.gov//store/user/dsunyou/TTToHadronic_TuneCP5_PSweights_13TeV-powheg-pythia8_ttcc_hadd.root .
xrdcp -s root://cmseos.fnal.gov//store/user/dsunyou/TTToHadronic_TuneCP5_PSweights_13TeV-powheg-pythia8_ttjj_hadd.root .

mv *.root ./CMSSW_9_4_6_patch1/src/TTTT_TMVA_DNN/

cd ./CMSSW_9_4_6_patch1/src

export SCRAM_ARCH=slc7_amd64_gcc630
eval `scramv1 runtime -sh`

source /cvmfs/sft.cern.ch/lcg/contrib/gcc/7.3.0/x86_64-centos7-gcc7-opt/setup.sh
source /cvmfs/sft.cern.ch/lcg/app/releases/ROOT/6.16.00/x86_64-centos7-gcc48-opt/bin/thisroot.sh

cd ./TTTT_TMVA_DNN/

python TMVAClassification_VarImportanceDNN.py -m $method -i "TTTT_TuneCP5_PSweights_13TeV-amcatnlo-pythia8_hadd.root" -s $str_xbitset -t $tag
