#!/bin/bash
source /storage/b/tkopf/jdl_maerz/setup_maerz.sh

trainingsname="HttTraining_TrainingImplementation"
lepton=mm
files_di=/storage/b/tkopf/NTupleApplication/files/
plots_di=/storage/b/tkopf/NTupleApplication/plots/
mergedFile=/storage/b/akhmet/merged_files_from_naf/MVAMet_09_11_2018/DYJetsToLLM50_RunIIFall17MiniAODv2_PU2017RECOSIMstep_13TeV_MINIAOD_madgraph-pythia8_ext1-v1/DYJetsToLLM50_RunIIFall17MiniAODv2_PU2017RECOSIMstep_13TeV_MINIAOD_madgraph-pythia8_ext1-v1.root


if [ ! -d "$files_di${trainingsname}_$lepton/" ]; then
	mkdir $files_di${trainingsname}_${lepton}/
fi
files_directory=$files_di${trainingsname}_${lepton}/
cp NN_Input_apply_xy_old.h5 $files_directory
cp NN_Input_apply_xy_old_npv24.h5 $files_directory
cp NN_Output_applied_xy_old.h5 $files_directory
cp preprocessing_input.pickle $files_directory
cp checkpoint $files_directory


if [ ! -d "$plots_di${trainingsname}_${lepton}/" ]; then
	mkdir $plots_di${trainingsname}_${lepton}/
fi
plots_directory=$plots_di${trainingsname}_${lepton}/

#python getNNinputs.py $lepton $mergedFile $files_directory
#python comparePhaseSpace.py $plots_directory $files_directory
#python applyNNmodel.py $lepton $files_directory
#python compareOutput.py $plots_directory $files_directory


cp -r $plots_directory /usr/users/tkopf/www/NTupleApplication/
cp /usr/users/tkopf/www/index.php $plots_directory
cp /usr/users/tkopf/www/index.php /usr/users/tkopf/www/NTupleApplication/${trainingsname}_${lepton}/
