import numpy as np
import root_numpy as rnp
import ROOT
import pandas as pd
import sys
import h5py

pTMin, pTMax = 20, 200
VertexMin, VertexMax = 23, 24

def pol2kar(norm, phi):
    x = np.cos(phi)*norm
    y = np.sin(phi)*norm
    return(x, y)

def pandasaddxy(pandas, metDefs):
    keys = metDefs+["l1","l2","genbosonpt"]
    for key in keys:
        if key=="l1":
            columnpT = "pt_1"
            columnphi = "phi_1"
            columnx = "Px_1"
            columny = "Py_1"
        elif key=="l2":
            columnpT = "pt_2"
            columnphi = "phi_2"
            columnx = "Px_2"
            columny = "Py_2"
        elif key=="genbosonpt":
            columnpT = "genbosonpt"
            columnphi = "genbosonphi"
            columnx = "genbosonpx"
            columny = "genbosonpy"
        else:
            columnpT = "met"+key+"Pt"
            columnphi = "met"+key+"Phi"
            columnx = "met"+key+"Px"
            columny = "met"+key+"Py"
        valx, valy = pol2kar(pandas[columnpT], pandas[columnphi])
        if key not in ["l1","l2","genbosonpt"]:
            pandas[columnx] = pd.Series(-valx, index=pandas.index)
            pandas[columny] = pd.Series(-valy, index=pandas.index)
        else:
            pandas[columnx] = pd.Series(valx, index=pandas.index)
            pandas[columny] = pd.Series(valy, index=pandas.index)
    return pandas

def getrecoil(pandas):
    RecoilMetsKeys = ["met", "metPuppi", "metNoPU", "metPUCorrected", "metTrack"]
    dfRecoil = pd.DataFrame()
    for key in RecoilMetsKeys:
        #recoil defininition
        dfRecoil[key+"Px"] = pd.Series(pandas[key+"Px"]-pandas["Px_1"]-pandas["Px_2"], index=pandas.index)
        dfRecoil[key+"Py"] = pd.Series(pandas[key+"Py"]-pandas["Py_1"]-pandas["Py_2"], index=pandas.index)
        dfRecoil[key+"SumEt"] = pd.Series(pandas[key+"SumEt"] - np.sqrt(np.square(pandas["Px_1"])+np.square(pandas["Py_1"])) - np.sqrt(np.square(pandas["Px_2"])+np.square(pandas["Py_2"])), index=pandas.index)
    #collect remaining columns where no changes are made
    Test_pT = np.sqrt(np.add(np.square(pandas["genbosonpx"]), np.square(pandas["genbosonpy"])))
    print("Mean deviation of x,y pT and genbosonpt", np.mean(np.add(Test_pT,-pandas["genbosonpt"])))
    dfRecoil["Px_1"] = pd.Series(pandas["Px_1"], index=pandas.index)
    dfRecoil["Boson_Pt"] = pd.Series(pandas["genbosonpt"], index=pandas.index)
    dfRecoil["Boson_Phi"] = pd.Series(pandas["genbosonphi"], index=pandas.index)
    dfRecoil["genbosonpx"] = pd.Series(pandas["genbosonpx"], index=pandas.index)
    dfRecoil["genbosonpy"] = pd.Series(pandas["genbosonpy"], index=pandas.index)
    dfRecoil["Px_2"] = pd.Series(pandas["Px_2"], index=pandas.index)
    dfRecoil["Py_1"] = pd.Series(pandas["Py_1"], index=pandas.index)
    dfRecoil["Py_2"] = pd.Series(pandas["Py_2"], index=pandas.index)
    dfRecoil["npv"] = pd.Series(pandas["npv"], index=pandas.index)
    dfRecoil["metPUPx"] = pd.Series(pandas["metPUPx"], index=pandas.index)
    dfRecoil["metPUPy"] = pd.Series(pandas["metPUPy"], index=pandas.index)
    dfRecoil["metPUSumEt"] = pd.Series(pandas["metPUSumEt"], index=pandas.index)
    return dfRecoil

def writehdf5(DataF, dset):
    IdxpTCut = (DataF['Boson_Pt']>pTMin) & (DataF['Boson_Pt']<=pTMax) & (DataF['npv']<=VertexMax) & (DataF['npv']>VertexMin)
    print("min boson pt ", np.min(DataF['Boson_Pt'][IdxpTCut]))
    print("max boson pt ", np.max(DataF['Boson_Pt'][IdxpTCut]))
    set_BosonPt = dset.create_dataset("Boson_Pt",  dtype='f',
        data=[ DataF['Boson_Pt'][IdxpTCut]])

    dset_PF = dset.create_dataset("PF",  dtype='f',
        data=[DataF['metPx'][IdxpTCut], DataF['metPy'][IdxpTCut],
        DataF['metSumEt'][IdxpTCut]])

    dset_Track = dset.create_dataset("Track",  dtype='f',
        data=[DataF['metTrackPx'][IdxpTCut], DataF['metTrackPy'][IdxpTCut],
        DataF['metTrackSumEt'][IdxpTCut]])

    dset_NoPU = dset.create_dataset("NoPU",  dtype='f',
        data=[DataF['metNoPUPx'][IdxpTCut], DataF['metNoPUPy'][IdxpTCut],
        DataF['metNoPUSumEt'][IdxpTCut]])

    dset_PUCorrected = dset.create_dataset("PUCorrected",  dtype='f',
        data=[DataF['metPUCorrectedPx'][IdxpTCut], DataF['metPUCorrectedPy'][IdxpTCut],
        DataF['metPUCorrectedSumEt'][IdxpTCut]])

    dset_PU = dset.create_dataset("PU",  dtype='f',
        data=[DataF['metPUPx'][IdxpTCut], DataF['metPUPy'][IdxpTCut],
        DataF['metPUSumEt'][IdxpTCut]])

    dset_Puppi = dset.create_dataset("Puppi",  dtype='f',
        data=[DataF['metPuppiPx'][IdxpTCut], DataF['metPuppiPy'][IdxpTCut],
        DataF['metPuppiSumEt'][IdxpTCut]])

    dset_NoPV = dset.create_dataset("NVertex",  dtype='f',data=[DataF['npv'][IdxpTCut]] )

    print("Hier wird Target erzeugt")
    dset_Target = dset.create_dataset("Target",  dtype='f',
            data=[-DataF["genbosonpx"][IdxpTCut],
            -DataF["genbosonpy"][IdxpTCut]])
    print("Target wurde erzeugt")
    dset.close()

def getInputs(rootFile,ll,filesD):
  treename = ll+"_nominal/ntuple"

  #collect NN input and target data
  metDefs = ["", "Puppi","NoPU","PU","PUCorrected","Track"]
  variables = ["Pt","Phi","SumEt"]
  branches = []
  for defs in metDefs:
      for var in variables:
          branches = branches + ["met%s%s"%(defs,var)]
  branchesadd = ["npv", "pt_1", "phi_1", "pt_2","phi_2", "met", "metphi", "genbosonpt", "genbosonphi"]
  branches = branches+branchesadd
  print("branches",branches)
  array = rnp.root2array(rootFile, treename=treename, branches=branches)
  print("array keys", array)
  pandas = pd.DataFrame.from_records(array.view(np.recarray))
  #print("pandas", pandas)

  pandasxy = pd.DataFrame()
  pandasrecoil = pd.DataFrame()
  pandasxy = pandasaddxy(pandas, metDefs)
  print("pandas xy added  ", pandas)
  pandasrecoil = getrecoil(pandas)
  print("pandas recoil ", pandasrecoil)

  #write inputs in hdf5 file for NN
  outputDir = filesD
  print("outputDir is ", outputDir)
  writeInputs_apply = h5py.File("%sNN_Input_apply_%s.h5"%(outputDir,ll), "w")
  writehdf5(pandasrecoil, writeInputs_apply)



if __name__ == "__main__":
    ll = sys.argv[1]
    rootFile = sys.argv[2]
    filesD = sys.argv[3]
    #{}"output.root"
    getInputs(rootFile,ll,filesD)
