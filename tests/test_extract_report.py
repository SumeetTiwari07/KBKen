#!/usr/bin/env python3

#from matplotlib import colors
import pandas as pd
import numpy as np
import sys
import extract_report as ep

class DataType():
    datatype = ''   
    def __init__(self, expected, estimated) -> None:
        self.x = expected
        self.y = estimated
        pass

    def getDataType(self):
        if isinstance(self.x, int) and isinstance(self.y, int):
            self.datatype = 'int'
        if isinstance(self.x, dict) and isinstance(self.y, dict):
            self.datatype = 'dict'
        if isinstance(self.x, pd.DataFrame) and isinstance(self.y, pd.DataFrame):
            self.datatype = 'DataFrame'
        if isinstance(self.x, list) and isinstance(self.x, list):
            self.datatype = 'list'        
        return self.datatype
    
class writeLog():
    def __init__(self, val) -> None:
        self.x = val.x
        self.y = val.y
        self.datatype = val.datatype
        pass

    def message(self):    
        dtype="int dict list"
        if self.datatype in dtype:
            print(self.datatype)
            if self.x == self.y:
                sys.stdout.write(f"   \u2705YES: {self.x}\n")
            else:
                sys.stdout.write(f"   \u274CNO\n")
                sys.stdout.write(f"   Expected result:\n{self.x}\n")
                sys.stdout.write(f"   Estimated result:\n{self.y}\n")
        
        if self.datatype == 'DataFrame':
            if self.x.equals(self.y):
                sys.stdout.write(f"   \u2705YES\n")
            else:
                sys.stdout.write(f"   \u274CNO\n")
        return

def expectedResult():
    number_of_samples=5
    sample_names={
        '1_lvl': 'SRR9214437_lvl',
        '1_all': 'SRR9214437_all',
        '2_lvl': 'SRR9214438_lvl',
        '2_all': 'SRR9214438_all',
        '3_lvl': 'SRR9214439_lvl',
        '3_all': 'SRR9214439_all'}
    kreport = pd.read_table("./combined-reports/filtered_kreport.tsv", header=0, sep="\t")
    #kreport.drop(columns={'taxonomy'}, inplace=True)
    colnames=list(kreport.columns.values)
    taxonomy=pd.read_table("sample_taxonomy.tsv",header = 0)
    taxonomy_list=taxonomy['taxonomy'].tolist()
    finalresult=pd.read_table("./result/kreports_final.tsv", header=0)
    return number_of_samples, sample_names, colnames, kreport, taxonomy_list, finalresult

def callClasess(VAR1, var):
    obj1=DataType(VAR1, var)
    obj1.getDataType()
    obj2=writeLog(obj1)
    obj2.message()
    return

"""
Test script to test functions extract_report.py.
"""
if __name__ == '__main__':
    # Generate expected results
    NSAMPLES, SAMPLENAMES, COLNAMES, FILTERED_KREPORT, TAXONOMYLIST, FINAL_RESULT=expectedResult()
    # Test 1
    print("\033[1m"+"a) Testing read_file() ...!!!"+"\033[0;0m")
    ## Esimtate
    input='./combined-reports/combined_kreports.txt'
    nsamples, samplenames = ep.read_file(input)
    ## Compare input and expected output
    print(f'  a.1) Are number of samples are same???')
    callClasess(NSAMPLES, nsamples)
    print(f'  a.2) Did the sample names matched???')
    callClasess(SAMPLENAMES, samplenames)

    # Test 2
    print("\033[1m"+"b) Testing kraken_report() ...!!!"+"\033[0;0m")
    ## Estimate
    filtered_kreport=ep.kraken_report(input, nsamples, samplenames)
    #filtered_kreport.drop(columns={'taxonomy'}, inplace=True)
    ## Expected output
    print("  b.1) Does both have the same column headers")
    colnames=list(filtered_kreport.columns.values)
    callClasess(COLNAMES, colnames)
    print("  b.2) Does both Kraken Summary are same?")
    callClasess(FILTERED_KREPORT, filtered_kreport)

    # Test 3
    print("\033[1m"+"c) Testing generate_taxonomy() ...!!!"+"\033[0;0m")
     ## Estimate
    final_result = ep.generate_taxonomy(filtered_kreport) 
    print("  c.1)If the final output is same?")
    callClasess(FINAL_RESULT, final_result)
    print("  c.1)Expected taxonomy were dected?")
    taxonomylist=final_result['taxonomy'].tolist()
    check =  all(item in taxonomylist for item in TAXONOMYLIST)
    if check is True:
        print("   \u2705All taxonomy detected")
    else:
        print("   \u274CMissing taxonomy")    
    





