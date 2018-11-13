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

colors_InOut = cm.brg(np.linspace(0, 1, 8))
nbinsHistBin = 150
pTMin, pTMax = 20, 200
VertexMin, VertexMax = 23, 24

def pol2kar(norm, phi):
    x = np.cos(phi)*norm
    y = np.sin(phi)*norm
    return(x, y)

def kar2pol(x, y):
    rho = np.sqrt(np.multiply(x,x) + np.multiply(y,y))
    phi = np.arctan2(y, x)
    return(rho, phi)

def loadInputsTargets(file):
    InputsTargets = h5py.File("%s"%(file), "r")
    print("InputsTargets keys", InputsTargets.keys())
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
    Target =  InputsTargets['Target']
    return (InputsTargets, Target)

def getHistogram(data, String, String2, pltmin, pltmax):
    Mean = np.mean(data)
    Std = np.std(data)
    if String2 == " new":
        bin = 2
    else:
        bin = 6
    #Reso = np.divide(-(DFName[branchString]),DFName[Target_Pt].values)
    #n, _ = np.histogram(-(DFName[branchString])-DFName[Target_Pt].values, bins=nbinsHistBin)
    plt.hist(data, bins=nbinsHistBin, range=[pltmin, pltmax], label=String+String2+': %8.2f $\pm$ %8.2f'%(Mean, Std), histtype='step', ec=colors_InOut[bin], normed=True)



def pltHistograms(plotDir, NewData,OldData, String):
    fig=plt.figure(figsize=(10,6))
    fig.patch.set_facecolor('white')
    ax = plt.subplot(111)
    ax.spines['top'].set_linewidth(0.5)
    ax.spines['right'].set_linewidth(0.5)
    ax.spines['bottom'].set_linewidth(0.5)
    ax.spines['left'].set_linewidth(0.5)
    ax.spines['top'].set_color('black')
    ax.spines['right'].set_color('black')
    ax.spines['bottom'].set_color('black')
    ax.spines['left'].set_color('black')

    pltmin = np.min([np.percentile(NewData, 2), np.percentile(OldData, 2)])
    pltmax = np.max([np.percentile(NewData, 98), np.percentile(OldData, 98)])
    getHistogram(NewData, String, " new", pltmin, pltmax)
    getHistogram(OldData, String, " old", pltmin, pltmax)


    box = ax.get_position()
    ax.set_position([box.x0, box.y0, box.width * 0.85, box.height])
    handles, labels = ax.get_legend_handles_labels()
    #handles.insert(0,mpatches.Patch(color='none', label=pTRangeStringNVertex))

    plt.xlabel(String, fontsize=18)
    plt.xlim(pltmin,pltmax)
    plt.ylabel('density', fontsize=18)

    legend = plt.legend(ncol=1, bbox_to_anchor=(1.05, 1.00), loc=4, borderaxespad=0., fontsize='large', numpoints=1, framealpha=1.0	, handles=[Line2D([], [], c=h.get_edgecolor()) for h in handles],  labels=labels)
    plt.setp(legend.get_title(),fontsize='x-large')
    plt.tick_params(axis='both', which='major', labelsize=18)
    plt.grid(color='black', linestyle='-', linewidth=0.1)
    plt.savefig("%s%s.png"%(plotDir,String), bbox_inches="tight")
    plt.close()


def compareInputs(plotsDir, filesDir):
    FileOld = "%sNN_Input_apply_xy_old.h5"%(filesDir)
    FileNew = "%sNN_Input_apply_mm.h5"%(filesDir)
    InputsNew, TargetsNew = loadInputsTargets(FileNew)
    InputsOld, TargetsOld = loadInputsTargets(FileOld)

    BosonPtNew, BosonPhiNew = kar2pol(TargetsNew[0,:], TargetsNew[1,:])
    BosonPtOld, BosonPhiOld = kar2pol(TargetsOld[0,:], TargetsOld[1,:])




    #PF
    PFMETNew = np.sqrt(np.add(np.square(InputsNew["PF"][0,:]-TargetsNew[0,:]),np.square(InputsNew["PF"][1,:]-TargetsNew[1,:])))
    PFMETOld = np.sqrt(np.add(np.square(InputsOld["PF"][0,:]-TargetsOld[0,:]),np.square(InputsOld["PF"][1,:]-TargetsOld[1,:])))
    pltHistograms(plotsDir, PFMETNew, PFMETOld, "PF_MET")
    pltHistograms(plotsDir, InputsNew["PF"][0,:], InputsOld["PF"][0,:], "PF_x")
    pltHistograms(plotsDir, InputsNew["PF"][1,:], InputsOld["PF"][1,:], "PF_y")
    pltHistograms(plotsDir, InputsNew["PF"][0,:]-TargetsNew[0,:], InputsOld["PF"][0,:]-TargetsOld[0,:], "PF_METx")
    pltHistograms(plotsDir, InputsNew["PF"][1,:]-TargetsNew[1,:], InputsOld["PF"][1,:]-TargetsOld[1,:], "PF_METy")
    pltHistograms(plotsDir, InputsNew["PF"][2,:], InputsOld["PF"][2,:], "PF_SumEt")

    #Puppi
    PuppiMETNew = np.sqrt(np.add(np.square(InputsNew["Puppi"][0,:]-TargetsNew[0,:]),np.square(InputsNew["Puppi"][1,:]-TargetsNew[1,:])))
    PuppiMETOld = np.sqrt(np.add(np.square(InputsOld["Puppi"][0,:]-TargetsOld[0,:]),np.square(InputsOld["Puppi"][1,:]-TargetsOld[1,:])))
    pltHistograms(plotsDir, PuppiMETNew, PuppiMETOld, "Puppi_MET")
    pltHistograms(plotsDir, InputsNew["Puppi"][0,:], InputsOld["Puppi"][0,:], "Puppi_x")
    pltHistograms(plotsDir, InputsNew["Puppi"][1,:], InputsOld["Puppi"][1,:], "Puppi_y")
    pltHistograms(plotsDir, InputsNew["Puppi"][0,:]-TargetsNew[0,:], InputsOld["Puppi"][0,:]-TargetsOld[0,:], "Puppi_METx")
    pltHistograms(plotsDir, InputsNew["Puppi"][1,:]-TargetsNew[1,:], InputsOld["Puppi"][1,:]-TargetsOld[1,:], "Puppi_METy")
    pltHistograms(plotsDir, InputsNew["Puppi"][2,:], InputsOld["Puppi"][2,:], "Puppi_SumEt")

    #Track
    pltHistograms(plotsDir, InputsNew["Track"][0,:], InputsOld["Track"][0,:], "Track_x")
    pltHistograms(plotsDir, InputsNew["Track"][1,:], InputsOld["Track"][1,:], "Track_y")
    pltHistograms(plotsDir, InputsNew["Track"][0,:]-TargetsNew[0,:], InputsOld["Track"][0,:]-TargetsOld[0,:], "Track_METx")
    pltHistograms(plotsDir, InputsNew["Track"][1,:]-TargetsNew[1,:], InputsOld["Track"][1,:]-TargetsOld[1,:], "Track_METy")
    pltHistograms(plotsDir, InputsNew["Track"][2,:], InputsOld["Track"][2,:], "Track_SumEt")

    #NoPU
    pltHistograms(plotsDir, InputsNew["NoPU"][0,:], InputsOld["NoPU"][0,:], "NoPU_x")
    pltHistograms(plotsDir, InputsNew["NoPU"][1,:], InputsOld["NoPU"][1,:], "NoPU_y")
    pltHistograms(plotsDir, InputsNew["NoPU"][0,:]-TargetsNew[0,:], InputsOld["NoPU"][0,:]-TargetsOld[0,:], "NoPU_METx")
    pltHistograms(plotsDir, InputsNew["NoPU"][1,:]-TargetsNew[1,:], InputsOld["NoPU"][1,:]-TargetsOld[1,:], "NoPU_METy")
    pltHistograms(plotsDir, InputsNew["NoPU"][2,:], InputsOld["NoPU"][2,:], "NoPU_SumEt")

    #PUCorrected
    pltHistograms(plotsDir, InputsNew["PUCorrected"][0,:], InputsOld["PUCorrected"][0,:], "PUCorrected_x")
    pltHistograms(plotsDir, InputsNew["PUCorrected"][1,:], InputsOld["PUCorrected"][1,:], "PUCorrected_y")
    pltHistograms(plotsDir, InputsNew["PUCorrected"][0,:]-TargetsNew[0,:], InputsOld["PUCorrected"][0,:]-TargetsOld[0,:], "PUCorrected_METx")
    pltHistograms(plotsDir, InputsNew["PUCorrected"][1,:]-TargetsNew[1,:], InputsOld["PUCorrected"][1,:]-TargetsOld[1,:], "PUCorrected_METy")
    #pltHistograms(plotsDir, InputsNew["PUCorrected"][2,:], InputsOld["PUCorrected"][2,:], "PUCorrected_SumEt")

    #PU
    pltHistograms(plotsDir, InputsNew["PU"][0,:], InputsOld["PU"][0,:], "PU_x")
    pltHistograms(plotsDir, InputsNew["PU"][1,:], InputsOld["PU"][1,:], "PU_y")
    pltHistograms(plotsDir, InputsNew["PU"][0,:]-TargetsNew[0,:], InputsOld["PU"][0,:]-TargetsOld[0,:], "PU_METx")
    pltHistograms(plotsDir, InputsNew["PU"][1,:]-TargetsNew[1,:], InputsOld["PU"][1,:]-TargetsOld[1,:], "PU_METy")
    pltHistograms(plotsDir, InputsNew["PU"][2,:], InputsOld["PU"][2,:], "PU_SumEt")

    #NVertex
    pltHistograms(plotsDir, InputsNew["NVertex"][0,:], InputsOld["NVertex"][0,:], "NVertex")

    #Target
    pltHistograms(plotsDir, TargetsNew[0,:], TargetsOld[0,:], "Target_x")
    pltHistograms(plotsDir, TargetsNew[1,:], TargetsOld[1,:], "Target_y")
    #pltHistograms(plotsDir, InputsNew["Boson_Pt"][:], InputsOld["Boson_Pt"][:], "Target_pT")


if __name__ == "__main__":
    plotsDir = sys.argv[1]
    filesDir = sys.argv[2]
    compareInputs(plotsDir,filesDir)
