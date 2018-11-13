import numpy as np
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
plt.style.use('seaborn-whitegrid')
import matplotlib.gridspec as gridspec
import pandas as pd
import matplotlib.mlab as mlab
import ROOT
import matplotlib.cm as cm
import matplotlib.patches as mpatches
import scipy.stats
import matplotlib.ticker as mtick
from matplotlib.colors import LogNorm
from matplotlib.ticker import NullFormatter, MaxNLocator
import h5py
import sys
from matplotlib.lines import Line2D
from comparePhaseSpace import pol2kar, kar2pol, loadInputsTargets, getHistogram, pltHistograms

colors_InOut = cm.brg(np.linspace(0, 1, 8))
nbinsHistBin = 150
pTMin, pTMax = 20, 200
VertexMin, VertexMax = 2, 50

def loadPredTruth(file):
    InputsTargets = h5py.File("%s"%(file), "r")
    '''
    Input = np.row_stack((
                InputsTargets['PF'],
                InputsTargets['Track'],
                InputsTargets['NoPU'],
                InputsTargets['PUCorrected'],
                InputsTargets['PU'],
                InputsTargets['Puppi'],
                InputsTargets['NVertex']
                ))
    '''
    Prediction = np.transpose(InputsTargets['MET_Predictions'])
    Target =  np.transpose(InputsTargets['MET_GroundTruth'])
    Boson_Pt = np.transpose(InputsTargets['Boson_Pt'])
    return (Prediction, Target, Boson_Pt)


def compareOutputs(plotsDir, filesDir):
    FileOld = "%sNN_Output_applied_xy_old.h5"%(filesDir)
    FileNew = "%sNN_Output_applied_mm.h5"%(filesDir)
    print("file new ", FileNew)
    PredNew, TargetsNew, BosonPtNew = loadPredTruth(FileNew)
    PredOld, TargetsOld, BosonPtOld = loadPredTruth(FileOld)





    #NN
    METNew = np.sqrt(np.add(np.square(PredNew[0,:]-TargetsNew[0,:]),np.square(PredNew[1,:]-TargetsNew[1,:])))
    METOld = np.sqrt(np.add(np.square(PredOld[0,:]-TargetsOld[0,:]),np.square(PredOld[1,:]-TargetsOld[1,:])))
    pltHistograms(plotsDir, METNew, METOld, "NN_MET")
    pltHistograms(plotsDir, PredNew[0,:], PredOld[0,:], "NN_x")
    pltHistograms(plotsDir, PredNew[1,:], PredOld[1,:], "NN_y")
    pltHistograms(plotsDir, PredNew[0,:]-TargetsNew[0,:], PredOld[0,:]-TargetsOld[0,:], "NN_METx")
    pltHistograms(plotsDir, PredNew[1,:]-TargetsNew[1,:], PredOld[1,:]-TargetsOld[1,:], "NN_METy")



if __name__ == "__main__":
    plotsDir = sys.argv[1]
    filesDir = sys.argv[2]
    compareOutputs(plotsDir,filesDir)
