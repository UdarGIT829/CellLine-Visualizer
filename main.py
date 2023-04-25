import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
import import_from_fitted as importFittedCurves
import pandas as pd
import tkinter as tk

#   Run the import data function
#       This will read the data from the selected CSV's into Pandas dataframes (the TORL Class will be a column)
importedData, drugIDs, histologyList = importFittedCurves.import_data()
#
#   Subset the full dataset by drugs (expecting 2, but because it will iterate through it can be any amount)
#
Drug_SubsetDict = dict()
for drugID in drugIDs:
    Drug_SubsetDict[drugID] = importedData[importedData['Drug_ID_1'] == drugID]
#
#   Subset the drug datasets by histology (tissue type)
#
DrugHistology_SubsetDict = dict()
histology_SubsetDict = dict()
for key,val in Drug_SubsetDict.items():
    DrugHistology_SubsetDict[drugID] = histology_SubsetDict
    DrugHistology_SubsetDict[key] = dict()
    for histology in histologyList:
        thisHistologydf = val[val['TORClass'] == histology]
        DrugHistology_SubsetDict[key][histology] = thisHistologydf
#
#Subsets have been made as in:  [DrugTreatment1]:[Histology1],[Histology2],[Histology3]
#                               [DrugTreatment2]:[Histology1],[Histology2],[Histology3]
#                               etc.
drugSubplot_Dict = dict()
subplot_Dict = dict()

for drugKey, drugDF in DrugHistology_SubsetDict.items():
    mainplottableDF = pd.DataFrame()
    for histologyName, histologyDF in drugDF.items():
        subplottableDF = pd.DataFrame()
        thisHistology_IC50 = list(histologyDF["IC50g"])
        subplottableDF[histologyName] = thisHistology_IC50
        mainplottableDF = pd.concat([mainplottableDF,subplottableDF],axis=1)
        list1, list2 = list(), list()
        for count, value in enumerate(subplottableDF.columns):
            list1.append(count+1)
            list2.append(value)
        # for i, d in enumerate(mainplottableDF):
        #     y = mainplottableDF[d]
        #     x = np.random.normal(i + 1, 0.04, len(y))
        #     plt.scatter(x, y)
        subplot_Dict[histologyName] = subplottableDF
    drugSubplot_Dict[drugKey] = subplot_Dict

        # mainplottableDF = mainplottableDF.fillna(0)
        # fig, ax = plt.subplots(sharey=True)
        # ax.set_yscale('log')
        # ax.boxplot(subplottableDF, showfliers=False)
        
    #For now only the first drug

####
#   Begin tkinter selection area



def ok():
    global drug_view
    global histology_view
    drug_view = drug_var.get()
    histology_view = hist_var.get()
    root.destroy()


root = tk.Tk()
root.title("Choose the Drug and Histology")
# use width x height + x_offset + y_offset (no spaces!)
root.geometry("%dx%d" % (330, 200))
root.title("tk.Optionmenu as combobox")

drug_var = tk.StringVar(root)
hist_var = tk.StringVar(root)
# initial value
drug_var.set('Select a Drug')
hist_var.set('Select a Histology')

# Drug choices dropdown
drug_choices = drugIDs
drug_option = tk.OptionMenu(root, drug_var, *drug_choices)
drug_option.pack(side='left', padx=10, pady=10)

# Histology choices dropdown
hist_choices = histologyList
hist_option = tk.OptionMenu(root, hist_var, *hist_choices)
hist_option.pack(side='left', padx=10, pady=10)

# Ok button calls above "ok()"" function
button = tk.Button(root, text="OK", command=ok)
button.pack(side='left', padx=10, pady=10)

root.mainloop()

###
#   At this point a drug to view and histology to view should be selected

drugDataLookup_forThisSubplot = dict(enumerate(DrugHistology_SubsetDict[drug_view][histology_view].index.values))
accessibleDF = drugSubplot_Dict.get(drug_view).get(histology_view)
fig, ax = plt.subplots(sharey=True)
ax.set_yscale('log')
ax.boxplot(accessibleDF, showfliers=False)


list1, list2 = list(), list()
for count, value in enumerate(accessibleDF.columns):
    list1.append(count+1)
    list2.append(value)

tenOverflow = 0.0001
thirtytwoOverflow = 0.0001
ADF_asDict = accessibleDF.to_dict()

plt.xticks(list1, list2)
for i, d in enumerate(accessibleDF):
    preOverflow_y = accessibleDF[d]
    data = list()
    for index in preOverflow_y.index:
        if preOverflow_y[index] >= 10.0:
            data.append(preOverflow_y[index]+tenOverflow)
            ADF_asDict[histology_view][index] = preOverflow_y[index]+tenOverflow
            tenOverflow += 0.0001
        elif preOverflow_y[index] <= 0.0032:
            data.append(preOverflow_y[index]-tenOverflow)
            ADF_asDict[histology_view][index] = preOverflow_y[index]-tenOverflow
            tenOverflow += 0.0001
        else:
            data.append(preOverflow_y[index])
    postOverflow_y = pd.Series(data=data,index=preOverflow_y.index)
    y = postOverflow_y    
    x = np.random.normal(i + 1, 0.04, len(y))

test1 = pd.DataFrame(x,y).iloc[:,0].to_dict()

global coords_toData_dict
coords_toData_dict = dict()
for key,val in ADF_asDict.items():
    for index, value in val.items():
        coords = tuple((test1[value],value))
        coords_toData_dict[coords] = DrugHistology_SubsetDict[drug_view][histology_view].iloc[[index]]


scatter = plt.scatter(x, y)


# Step 2. Create Annotation Object
annotation = ax.annotate(
    text='',
    xy=(0, 0),
    xytext=(15, 15), # distance from x, y
    textcoords='offset points',
    bbox={'boxstyle': 'round', 'fc': 'w'},
    arrowprops={'arrowstyle': '->'}
)
annotation.set_visible(False)

# Step 3. Implement the hover event to display annotations
def motion_hover(event):
    annotation_visbility = annotation.get_visible()
    if event.inaxes == ax:
        is_contained, annotation_index = scatter.contains(event)
        if is_contained:
            data_point_location = scatter.get_offsets()[annotation_index['ind'][0]]
            annotation.xy = data_point_location
            coords_lookup = tuple(data_point_location)
            try:
                printData_dict = coords_toData_dict.get(coords_lookup).to_dict()

                #{'ExperimentID': {12: 15630}, 'ControlID': {12: 4020}, 'TreatmentBarcode': {12: 'AB075133'}, 'Treatment.position': {12: 'C5-6'}, 
                # 'Staff_ID': {12: 'Bryant'}, 'Cell_Line': {12: 'SUDHL6'}, 'SetupDate': {12: '3/14/2023'}, 'Drug_ID_1': {12: 'IMGN853'}, 
                # 'Day1Barcode': {12: 'AB078358'}, 'Day1Location': {12: 7}, 'Day7Barcode': {12: 'AB078359'}, 'Day7Location': {12: 7}, 
                # 'Cell_Line_ID': {12: 'LM054'}, 'IC50g': {12: 3.41085026079571}, 'QC_check': {12: nan}, 'TORClass': {12: 'Lymphoma'}}
                
                thisName = list(printData_dict["Cell_Line"].values())[0]
                thisIC50g = list(printData_dict["IC50g"].values())[0]
                thisStaff = list(printData_dict["Staff_ID"].values())[0]
                thisCellLineID = list(printData_dict["Cell_Line_ID"].values())[0]
                thisQC_Check = list(printData_dict["QC_check"].values())[0]
                text_label = f'Name: {thisName}\nIC50: {thisIC50g}\nID: {thisCellLineID}\nStaff: {thisStaff}\nQC Check: {thisQC_Check}'
            except AttributeError:
                text_label = "The program failed to find this data point: "+str(data_point_location)
                print("Check here:")
                print(coords_toData_dict)
                print("\tLook for: ",str(data_point_location))
            annotation.set_text(text_label)

            annotation.set_alpha(1.0)

            annotation.set_visible(True)
            fig.canvas.draw_idle()
        else:
            if annotation_visbility:
                annotation.set_visible(False)
                fig.canvas.draw_idle()

fig.canvas.mpl_connect('motion_notify_event', motion_hover)
plot_title = str(drug_view)
fig.canvas.manager.set_window_title('Test')
plt.savefig('figure.png')
plt.title(drug_view)
plt.show()
