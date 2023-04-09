from sys import exit


"""# Anonymization parameters #"""
k = 45           # K-anonymity
l = 2           # L-closeness
t = 0           # T-diversity
epsilon = 0.5   # Epsilon for Differential Privacy
delta = 0.001   # Delta for Differential Privacy






#
# Load Dataset
# ------------

import numpy as np
import pandas as pd


# Load the dataset into memory
dataset_path = "adult.sample.csv" #input("Input Dataset Path: ") 
df = pd.read_csv(dataset_path, sep=",", engine="python");

print(" Total number of rows in dataset: ", len(df))


# Check if the dataset is parsed properly
print (df.head())

stepCheck = input ("\nQ> Is your dataset parsed properly? (y/n): ")
if (stepCheck == "n" or stepCheck == "N"):
    print("[Error] Dataset parsing is wrong!")
    exit(0) 

#Data Preprocessing
df.dropna(axis=0, inplace=True)
print(" Total number of rows after pre-processing: ", len(df))




# 
# Collect Attribute Details
# -------------------------

attributes = dict()
for col in df.columns:
    print ("\nAttribute : '%s'" % col)

    while True:
        print ("\n\t1. Identifier\n\t2. Quasi-identifier\n\t3. Sensitive\n\t4. Insensitive")
        ch = int(input ("Q> Please select the attribute type: "))
        if ch not in [1, 2, 3, 4]:
            print("[Error] Please enter a value 1,2,3 or 4!")
        else:
            break
    
    attributes[col] = {
        'dataType': df[col].dtype, 
        'attributeType': ["Identifier", "Quasi-identifier", "Sensitive", "Insensitive"][ch-1]
    }
    
    if (df[col].dtype.name == "object"):
        df[col] = df[col].astype("category")



# Making a copy of the dataset for the DP stats calculation
OrigDF = df.copy()



# Some datastructures for computational easiness
qi_index = list()
feature_columns = list()
sensitive_column = list()

for attribute in attributes:
    if attributes[attribute]['attributeType'] == "Quasi-identifier":
        feature_columns.append(attribute)
        qi_index.append(list(OrigDF.columns).index(attribute))
    elif attributes[attribute]['attributeType'] == "Sensitive":
        sensitive_column.append(attribute)

feature_columns =  feature_columns if (len(feature_columns) > 0) else None
sensitive_column = sensitive_column[0] if (len(sensitive_column) > 0) else None









# ----------------------------------------------------------- Anonymization ------------------------------------------------------- #

#
# Supress direct identifiers with '*'
# -----------------------------------

for attribute in attributes:
    if attributes[attribute]['attributeType'] == "Identifier":
        df[attribute] = '*'



#
# Generalizing quasi-identifiers with k-anonymity
# -----------------------------------------------

from algorithms.anonymizer import Anonymizer


# Check if there are any quasi-identifiers
quasi = False
for attribute in attributes:
    if attributes[attribute]['attributeType'] == "Quasi-identifier":
        quasi = True


assert quasi, "No Quasi-identifier found! At least 1 quasi-identifier is required."

anon = Anonymizer(df, attributes)
anonymizedDF = anon.anonymize(k, l, t)


#
# Insenstitive attributes are left unchanged
# ------------------------------------------


#TBD



# Utility Measure
#TBD



#
# Exporting data
# --------------


ch = input("Do you want to export the anonymized dataset (y/n): ")
if not (ch == 'y' or ch == ''):
    exit(0)


export_path = "AnonymizedData"
print("\nExporting anonymized dataset ... ")
anonymizedDF.to_csv(export_path+'.csv', index=False)

# Create a Pandas Excel writer object using XlsxWriter as the engine.
writer = pd.ExcelWriter(export_path + '.xlsx')


qi_index = list()
for attribute in attributes:
    if attributes[attribute]['attributeType'] == "Quasi-identifier":
        qi_index.append(list(OrigDF.columns).index(attribute))


def paint_bg(v, color):
    ret = [f"background-color: {color[0]};" for i in v]
    return ret

anonymizedDF = anonymizedDF.style.hide_index().apply(paint_bg, color=['gainsboro', 'ivory'], axis=1) 


# Write a dataframe to the worksheet.
anonymizedDF.to_excel(writer, sheet_name ='Data', index=False)


# Close the Pandas Excel writer object and output the Excel file.
writer.save()


