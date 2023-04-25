import tkinter as tk
from tkinter import filedialog
import pickle
import os.path
from collections import UserDict
import pandas as pd

def promptUserFunct(dialogueName,question):
    msg_box = tk.messagebox.askquestion(dialogueName,question, icon='warning')
    if msg_box == 'yes':
        return True
    return False

        
def select_data(filePathsUsed):
    if os.path.isfile("lastFilesUsed.txt"):
        promptUser = True
    with open("lastFilesUsed.txt",'r') as lastFilesUsed:
        lastFilenames = lastFilesUsed.readlines()
    if os.path.isfile("LastFittedCurves.obj") and os.path.isfile("LastTORLFile.obj"):
        print("Previous files recognized")
    else:
        promptUser = False

    if len(lastFilenames) != 2:
        lastFilenames = ["",""]

    FittedCurveCSV = None
    promptFail = True
    while promptFail:
        if promptUser == False:
            prompt1 = False
            print("No previous file recognized.")
        else:
            lastFileName1 = lastFilenames[0]
            prompt1 = promptUserFunct("Use last FittingCurveFile?","Use last FittingCurveFile?\n"+lastFileName1[:10]+"..."+lastFileName1[-40:])
        if prompt1 == True:
            filePathsUsed.append(lastFilenames[0])
            pickleFittedCurveFile = open("LastFittedCurves.obj",'rb')
            FittedCurveCSV = pickle.load(pickleFittedCurveFile)
            pickleFittedCurveFile.close()
            promptFail = False

        if prompt1 == False:
            FittedCurveFilename = filedialog.askopenfilename()
            if len(FittedCurveFilename) > 40:
                filePathsUsed.append(FittedCurveFilename+"\n")
            else:
                filePathsUsed.append(FittedCurveFilename+"\n")

            FittedCurveCSV = pd.read_table(FittedCurveFilename)

            pickleFittedCurveFile = open("LastFittedCurves.obj",'wb')
            pickle.dump(FittedCurveCSV,pickleFittedCurveFile)
            pickleFittedCurveFile.close()
            promptFail = False


    promptFail = True
    TORLClassCSV = None
    while promptFail:
        if promptUser == False:
            prompt2 = False
        else:
            lastFileName2 = lastFilenames[1]
            prompt2 = promptUserFunct("Use last TORL Class File?","Use last TORL Class File?\n"+lastFileName2[:10]+"..."+lastFileName2[-40:])
        if prompt2 == True:
            filePathsUsed.append(lastFilenames[1])
            pickleTORLCLASSFile = open("LastTORLFile.obj",'rb')
            TORLClassCSV = pickle.load(pickleTORLCLASSFile)
            pickleTORLCLASSFile.close()
            promptFail = False

        elif prompt2 == False:
            TORLClassFilename = filedialog.askopenfilename()
            if len(TORLClassFilename) > 40:
                filePathsUsed.append(TORLClassFilename+"\n")
            else:
                filePathsUsed.append(TORLClassFilename+"\n")

            TORLClassCSV = pd.read_table(TORLClassFilename)

            pickleTORLCLASSFile = open("LastTORLFile.obj",'wb')
            pickle.dump(TORLClassCSV,pickleTORLCLASSFile)
            pickleTORLCLASSFile.close()
            promptFail = False


    return FittedCurveCSV, TORLClassCSV


def import_data():
    filePathsUsed = list()
    lastFilenames = list()
    Flagged_CellLineIDs = list()
    drugIDs = list()

    FittedCurveCSV, TORLClassCSV = select_data(filePathsUsed)

    FittedTORL_DF = pd.merge(FittedCurveCSV, TORLClassCSV, on="Cell_Line_ID", how='inner')
    colList = FittedTORL_DF.columns
    DesiredCols = ['ExperimentID', 'ControlID', 'TreatmentBarcode', 'Treatment.position',
       'Staff_ID', 'Cell_Line', 'SetupDate', 'Drug_ID_1',
       'Day1Barcode', 'Day1Location', 'Day7Barcode', 'Day7Location',
       'Cell_Line_ID','IC50g', 'QC_check', 'TORClass']
    removeList = list(filter(lambda i: i not in DesiredCols, colList))

    FittedTORL_DF = FittedTORL_DF.drop(columns=removeList,axis=1)
    # FittedTORL_DF = FittedTORL_DF.set_index("ExperimentID")
    drugIDs = list(FittedTORL_DF['Drug_ID_1'].unique())
    histologyList = list(FittedTORL_DF['TORClass'].unique())

    if len(filePathsUsed) > 0:
        with open("lastFilesUsed.txt",'w') as lastFilesUsed:
            lastFilesUsed.writelines(filePathsUsed)

    return FittedTORL_DF, drugIDs, histologyList