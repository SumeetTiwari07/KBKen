#!/usr/bin/env python3

#from matplotlib import colors
import pandas as pd
import argparse
import numpy as np

"""
Parse multiple samples summary kraken reports.
Renaming the samples with actual sample names.
Add taxonomy for each species within the report
optional: Discarding a Domain/species.

Expected output file:
1) Filtered summary with taxonomy.
2) Separate "taxonomy.tsv" file.
"""

def read_file(summary_file):
    """
    Checking the file existance.
    Extracting the number of samples and increment it by 2
    """
    try:
        with open(summary_file) as f:
            sample_names={}
            for i, line in enumerate(f):
                if line.startswith("#Number of Samples:"):
                    firstline=line.rstrip()
                    n_sample=int(firstline.split(': ')[1])
                    n_sample=n_sample+2 # geting number of samples which can be used as header name for parsing file using pandas.
                if line.startswith("#Total number of Reads:"):
                    pass
                if i>1 and i<n_sample:
                    line=line.strip()
                    s_id,s_name=line.split('\t')
                    ids=s_id.split('#S')[1]
                    all_names=s_name.split('/')[-1]
                    names=all_names.split('.report')[0]
                    sample_names[f'{ids}_lvl']=f'{names}_lvl'
                    sample_names[f'{ids}_all']=f'{names}_all'

    except IOError:
        print ("File not accessible or information is missing")
    
    finally:
        f.close()
    
    return n_sample,sample_names

def kraken_report(summary_file,header_row):
    # Parsing the file
    kraken_summary=pd.read_csv(summary_file,header=header_row,sep="\t")

    # Removing leading and trailing spaces from names of taxa
    kraken_summary['name']=kraken_summary['name'].str.strip()

    # Droping columns #perc #tot_all #tot_lvl #taxid
    kraken_summary.drop(columns=['#perc','tot_all','tot_lvl','taxid'],inplace=True)

    # Keeping reads mapped to specific clade
    kraken_summary=kraken_summary.filter(regex=f'_lvl$|name|lvl_type',axis=1)
 
    # Renaming columns with actual sample names
    kraken_summary.rename(columns=sample_names,inplace=True)

    kraken_summary['lvl_type']=kraken_summary['lvl_type'].str.casefold() # ranks in lower case
    kraken_summary['taxonomy'] = kraken_summary['lvl_type']+"__"+kraken_summary['name'] # combine ranks with names
    kraken_summary.columns=kraken_summary.columns.str.replace('_lvl','', regex=True)

    return kraken_summary

def generate_taxonomy(kreport):
    '''
    Generate the taxonomy for each taxa rank.
    '''
    for idx, row in kreport.iterrows():
        # get unclassified
        if row['lvl_type'] == "u":
            ranks = ['d','p','c','o','f','g','s']
            u = ["__".join([i, "unclassified"]) for i in ranks]
            kreport.loc[idx, 'taxonomy'] = ";".join(u)
        # get domain              
        elif row['lvl_type'] == "d":
            domain = row['taxonomy']
            kreport.loc[idx, 'taxonomy'] = domain
        # get phylym 
        elif row['lvl_type'] == "p":
            phylum = row['taxonomy']
            kreport.loc[idx, 'taxonomy'] = ";".join([domain, phylum])
        # get class
        elif row['lvl_type'] == "c":
            clas = row['taxonomy']
            kreport.loc[idx, 'taxonomy'] = ";".join([domain, phylum, clas])
        # get order
        elif row['lvl_type'] == "o":
            order = row['taxonomy']
            kreport.loc[idx, 'taxonomy'] = ";".join([domain, phylum, clas, order])
        # get family
        elif row['lvl_type'] == "f":
            family = row['taxonomy']
            kreport.loc[idx, 'taxonomy'] = ";".join([domain, phylum, clas, order, family])
        # get genus
        elif row['lvl_type'] == "g":
            genus = row['taxonomy']
            kreport.loc[idx, 'taxonomy'] = ";".join([domain, phylum, clas, order, family, genus])
        # get species
        elif row['lvl_type'] == "s":
            species = row['taxonomy']
            kreport.loc[idx, 'taxonomy'] = ";".join([domain, phylum, clas, order, family, genus, species])
        else:
            na = "na"
            kreport.loc[idx, 'taxonomy'] = ";".join([na,na,na,na,na,na,na]) 

    return kreport

if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__ , formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('-i','--input',type=str, required=True, help="Combined table of kraken report generated by: https://github.com/jenniferlu717/KrakenTools#combine_kreportspy")
    parser.add_argument('-dn','--dname',action='append', help="Domains to remove from the kraken summary for eg: '-dn Eukaryota -dn Viruses'")
    parser.add_argument('-sn','--sname',action='append', help="Complete Species names to reomove from summary eg: '-sn Homo sapiens -sn xyz")
    parser.add_argument('-o','--output',type=str, help="Output file (.tsv)")
    args = parser.parse_args()


    #Reading input file and returing the number of samples:
    header_row,sample_names=read_file(args.input)
    
    #Extracting the kraken_report and domains found in report with their index value
    summary=kraken_report(args.input,header_row)

    # Add taxonomy
    taxonomy_df = generate_taxonomy(summary)

    #Removal of domains
    if args.dname:
        #Removing domains:
        domains = ["__".join(["d", i]) for i in args.dname]
        for d in domains:
            taxonomy_df=taxonomy_df[~taxonomy_df['taxonomy'].str.contains(d)]
        # Save output
        taxonomy_df.to_csv(args.output, sep="\t", index=False)      
    #Removal of species
    elif args.sname:
        species = ["__".join(["s", i]) for i in args.sname]
        for s in species:
           taxonomy_df=taxonomy_df[~taxonomy_df['taxonomy'].str.contains(s)]
        # Save output
        taxonomy_df.to_csv(args.output, sep="\t", index=False)
    else: 
        # Save output
        taxonomy_df.to_csv(args.output,index=False,sep="\t")

    # Write only taxonomy
    #onlytaxonomy = taxonomy_df.filter(regex=f'name|lvl_type|taxonomy',axis=1)
    #onlytaxonomy.to_csv("taxonomy.tsv",sep="\t",index=False)

