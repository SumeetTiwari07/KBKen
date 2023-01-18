#!/usr/bin/env python3

#from matplotlib import colors
import pandas as pd
import argparse
import numpy as np

"""
Genrate taxanomy from combine Kranken reports.
"""

def generate_taxonomy(kreport):
    '''
    Generate the taxonomy for each taxa rank.
    '''
    for idx, row in kreport.iterrows():
        # get unclassified
        if row['lvl_type'] == "u":
            ranks = ['d','p','c','o','f','g','s']
            u = ["__".join([i, "unclassified"]) for i in ranks]
            kreport.loc[idx, 'taxanomy'] = ";".join(u)
        # get domain              
        elif row['lvl_type'] == "d":
            domain = row['taxanomy']
            kreport.loc[idx, 'taxanomy'] = domain
        # get phylym 
        elif row['lvl_type'] == "p":
            phylum = row['taxanomy']
            kreport.loc[idx, 'taxanomy'] = ";".join([domain, phylum])
        # get class
        elif row['lvl_type'] == "c":
            clas = row['taxanomy']
            kreport.loc[idx, 'taxanomy'] = ";".join([domain, phylum, clas])
        # get order
        elif row['lvl_type'] == "o":
            order = row['taxanomy']
            kreport.loc[idx, 'taxanomy'] = ";".join([domain, phylum, clas, order])
        # get family
        elif row['lvl_type'] == "f":
            family = row['taxanomy']
            kreport.loc[idx, 'taxanomy'] = ";".join([domain, phylum, clas, order, family])
        # get genus
        elif row['lvl_type'] == "g":
            genus = row['taxanomy']
            kreport.loc[idx, 'taxanomy'] = ";".join([domain, phylum, clas, order, family, genus])
        # get species
        elif row['lvl_type'] == "s":
            species = row['taxanomy']
            kreport.loc[idx, 'taxanomy'] = ";".join([domain, phylum, clas, order, family, genus, species])
        else:
            na = "na"
            kreport.loc[idx, 'taxanomy'] = ";".join([na,na,na,na,na,na,na]) 

    return kreport

if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__ , formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('-i','--input',type=str, required=True, help="Combined table of kraken report after filteration")
    parser.add_argument('-o','--output',type=str, help="Output file")
    args = parser.parse_args()

    # Parse input file
    report = pd.read_table(args.input, header=0, sep="\t")
    report['lvl_type']=report['lvl_type'].str.casefold() # lower case the ranks
    report['taxanomy'] = report['lvl_type']+"__"+report['name'] # combine ranks with names
    
    # Add taxanomic ranks to report
    taxanomy_df=generate_taxonomy(report)
    taxanomy_df.to_csv("taxanomy.tsv", sep="\t", header=True, index=False)



