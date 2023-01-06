#!/usr/bin/env python3

#from matplotlib import colors
import pandas as pd
import argparse
import numpy as np

"""
Parse multiple samples summary kraken reports.
Renaming the samples with actual sample names.
Filtering the all the species beloning to particular Domains.
Filtering species based on their name.
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

    # Droping reads specific to a clade.
    kraken_summary=kraken_summary.filter(regex=f'_all$|name|lvl_type',axis=1)

    # Renaming columns with actual sample names
    kraken_summary.rename(columns=sample_names,inplace=True)
    
    return kraken_summary

def add_domain(summary_df):
    names_with_domain=pd.DataFrame(0,index=np.arange(len(summary_df)),columns=["name"])
    #Get Domains index
    domains=summary_df[summary_df['lvl_type']=="D"]['name']
    domains=domains.to_frame()
    idx=domains.index.tolist()

    for index, row in summary_df.iterrows():
        d1=['U','R']
        d2=['K','P','C','O','F','G','S','D']
        
        if set(d1) & set(row['lvl_type']):
            names_with_domain.loc[index,'name']=row['name']
            continue
        
        if row['lvl_type']=="D":
            names_with_domain.loc[index,'name']=row['name']
            continue

        if set(d2) & set(row['lvl_type']):
            if len(idx)==4:
                if index > idx[0] and index < idx[1]:
                    names_with_domain.loc[index,'name']=domains.loc[idx[0],'name']
                    #names_with_domain.loc[index,'name']=domains.loc[idx[0],'name']+";"+row['name']
                elif index > idx[1] and index < idx[2]:
                    names_with_domain.loc[index,'name']=domains.loc[idx[1],'name']
                    #names_with_domain.loc[index,'name']=domains.loc[idx[1],'name']+";"+row['name']
                elif index > idx[2] and index < idx[3]:
                    names_with_domain.loc[index,'name']=domains.loc[idx[2],'name']
                    #names_with_domain.loc[index,'name']=domains.loc[idx[2],'name']+";"+row['name']
                elif index > idx[3]:
                    names_with_domain.loc[index,'name']=domains.loc[idx[3],'name']
                    #names_with_domain.loc[index,'name']=domains.loc[idx[3],'name']+";"+row['name']
                else:
                    pass
            
            if len(idx)==3:
                if index > idx[0] and index < idx[1]:
                    names_with_domain.loc[index,'name']=domains.loc[idx[0],'name']
                    #names_with_domain.loc[index,'name']=domains.loc[idx[0],'name']+";"+row['name']
                elif index > idx[1] and index < idx[2]:
                    names_with_domain.loc[index,'name']=domains.loc[idx[1],'name']
                    #names_with_domain.loc[index,'name']=domains.loc[idx[1],'name']+";"+row['name']
                elif index > idx[2]:
                    names_with_domain.loc[index,'name']=domains.loc[idx[2],'name']
                    #names_with_domain.loc[index,'name']=domains.loc[idx[3],'name']+";"+row['name']
                else:
                    pass
            
            if len(idx)==2:
                if index > idx[0] and index < idx[1]:
                    names_with_domain.loc[index,'name']=domains.loc[idx[0],'name']
                    #names_with_domain.loc[index,'name']=domains.loc[idx[0],'name']+";"+row['name']
                elif index > idx[1]:
                    names_with_domain.loc[index,'name']=domains.loc[idx[1],'name']
                    #names_with_domain.loc[index,'name']=domains.loc[idx[1],'name']+";"+row['name']
                else:
                    pass
 
    summary_df['domain_names']=names_with_domain['name']
    
    return summary_df


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__ , formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('-i','--input',type=str, required=True, help="Combined table of kraken report generated by: https://github.com/jenniferlu717/KrakenTools#combine_kreportspy")
    parser.add_argument('-d','--domain',action='append', help="Domains to remove from the kraken summary for eg '-d Eukaryota -d Viruses'")
    parser.add_argument('-n','--name',action='append', help="Complete species names to reomove from summary")
    parser.add_argument('-o','--output',type=str, help="Output file")
    args = parser.parse_args()


    #Reading input file and returing the number of samples:
    header_row,sample_names=read_file(args.input)
    
    #Extracting the kraken_report and domains found in report with their index value
    summary=kraken_report(args.input,header_row)

    #Removal of domains
    if args.domain:
        #Adding domain of each species.
        summary_with_domains=add_domain(summary)
        #Removing domains:
        for i in args.domain:
            summary_with_domains=summary_with_domains[summary_with_domains['domain_names']!=i]
        summary_with_domains.reset_index(inplace=True)
        summary_with_domains.drop(columns=['index','domain_names'],inplace=True)       
        summary_with_domains.to_csv(args.output,index=False,sep="\t")
    
    if args.name:
        for s in args.name:
            summary=summary[summary['name']!=s]
        summary.reset_index(inplace=True)
        summary.drop(columns=['index'],inplace=True)
        summary.to_csv(args.output,index=False,sep="\t")

    
    if not args.name: 
        if not args.domain:
            summary.to_csv(args.output,index=False,sep="\t")

