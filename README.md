# Introduction 
KBKen is pipeline to run [Kraken2](https://github.com/DerrickWood/kraken2) and [Bracken](https://github.com/jenniferlu717/Bracken) to estimate the taxnomic abubdance of species at `Genus` and `Species` level.

## Installation:
**Kraken2:**

```
conda install -c bioconda kraken2=2.1.2
conda install -c bioconda krakentools=1.2
```
**Bracken:** 
```
# Installation from scatch
wget https://github.com/jenniferlu717/Bracken/archive/refs/tags/v2.8.tar.gz
tar -xzvf v2.8.tar.gz
cd Bracken-2.8
bash install_bracken.sh
OR
# One command installation
conda install -c bioconda bracken=2.8
```

## Singularity image:
```
Bootstrap: docker
From: centos:centos7.6.1810

%environment
    export PATH=$PATH:/opt/software/conda/bin
    source /opt/software/conda/bin/activate /opt/software/conenv


%post
    yum -y install epel-release wget which nano curl zlib-devel git
    yum -y groupinstall "Development Tools"

    mkdir -p /opt/software
    cd /opt/software

    #Downloading miniconda3
    wget -c https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
    
    #Installing miniconda3
    
    sh ./Miniconda3-latest-Linux-x86_64.sh -p /opt/software/conda -b
    
    /opt/software/conda/bin/conda config --add channels defaults
    /opt/software/conda/bin/conda config --add channels bioconda
    /opt/software/conda/bin/conda config --add channels conda-forge

    /opt/software/conda/bin/conda create -y -p /opt/software/conenv -c bioconda kraken2=2.1.2
    
    source /opt/software/conda/bin/activate /opt/software/conenv
    
    # Installing Bracken
    wget https://github.com/jenniferlu717/Bracken/archive/refs/tags/v2.8.tar.gz
    tar -xzvf v2.8.tar.gz
    cd Bracken-2.8
    bash install_bracken.sh

    ln -s /opt/software/Bracken-2.8/bracken /opt/software/conenv/bin/bracken
    chmod ugo+x /opt/software/conenv/bin/bracken
    
    cd /opt/software
    
    /opt/software/conda/bin/conda clean -y --all
%runscript
    exec Kraken2 "$@"
```

## Running Kraken2 and Braken

### Kraken2
```
kraken2
    --db DB
    --threads 30 
    --output SampleA.output 
    --report SampleA.report 
    --memory-mapping 
    --paired 
    SampleA_R1.fastq.gz SampleA_R2.fastq.gz"
```
**Note:** 
* DB in final pipeline:
`DB="/qib/platforms/Informatics/transfer/outgoing/databases/kraken2/benlangmead/k2_pluspfp_20220607/`

* DB for test:
`DB="/qib/platforms/Informatics/transfer/outgoing/databases/kraken2/benlangmead/20210127_plusPF/"`

### Bracken

```
bracken 
    -d DB
    -i SampleA.report" 
    -o SampleA.braken.report" 
    -w SampleA".braken.newreport" 
    -r 300 
    -l S
```


## Bactch script to run the Kraken and Bracken
```
# Classification.sh

#!/bin/bash -e
#SBATCH -p qib-medium,nbi-medium
#SBATCH -t 1-20:00
#SBATCH -c 10
#SBATCH -n 1
#SBATCH --mem=160000
#SBATCH -N 1
#SBATCH --mail-type=ALL
#SBATCH --mail-user=tiwari@nbi.ac.uk
#SBATCH -o /qib/research-projects/cami/tiwari/meta_mock/logs/run_000.%j.out
#SBATCH -e /qib/research-projects/cami/tiwari/meta_mock/logs/run_000.%j.err
#SBATCH --array=0-10%1
#THIS_JOB_TAGS: 
#cd "/qib/platforms/Informatics/GMH/2022-yasir/microbio/cleaned_reads/reads/"
# See: $SLURM_SUBMIT_DIR
export THREADS=$SLURM_CPUS_ON_NODE

IMG="/qib/research-projects/cami/tiwari/meta_mock" # Image location
CLASSIFICATION="singularity exec $IMG/classification.simg" 
INPUTREADS="$IMG/test-reads" # Toy-reads
DB="/qib/platforms/Informatics/transfer/outgoing/databases/kraken2/benlangmead/20210127_plusPF/" # For testing only
REPORT="$IMG/report" # Output directory to store kraken2 and braken reports

## Create input list
ls $INPUTREADS/*"_R1"* | xargs -n 1 basename | awk -F"_R1" '{print $1}' >$INPUTREADS/list.txt
mapfile -t INPUTS < $INPUTREADS/list.txt

## Run kraken2
mkdir -p $REPORT

srun $CLASSIFICATION kraken2 --db $DB \
--threads 8 \
--report $REPORT/${INPUTS[${SLURM_ARRAY_TASK_ID}]}".report" \
--output $REPORT/${INPUTS[${SLURM_ARRAY_TASK_ID}]}".output" \
--paired $INPUTREADS/${INPUTS[${SLURM_ARRAY_TASK_ID}]}"_R1.fq.gz" $INPUTREADS/${INPUTS[${SLURM_ARRAY_TASK_ID}]}"_R2.fq.gz"

## Run bracken
srun $CLASSIFICATION bracken -d $DB \
-i $REPORT/${INPUTS[${SLURM_ARRAY_TASK_ID}]}".report" \
-o $REPORT/${INPUTS[${SLURM_ARRAY_TASK_ID}]}".bracken.report" \
-w $REPORT/${INPUTS[${SLURM_ARRAY_TASK_ID}]}".bracken.newreport" \
-r 300 \
-l S
```
## Merging reports.
a) Kraken
    Kraken reports of multiple samples can be merged by using [combine_kreports.py](https://github.com/jenniferlu717/KrakenTools#combine_kreportspy).

```
combine_kreports.py -r /qib/research-projects/cami/tiwari/meta_mock/report/*.report -o /qib/research-projects/cami/tiwari/meta_mock/report/merged_kreports.txt
```
b) Bracken
    Bracken reports of multiple samples can be merged using [combine_bracken_outputs.py](https://github.com/jenniferlu717/Bracken/tree/master/analysis_scripts/)
```
combine_bracken_outputs.py --files /qib/research-projects/cami/tiwari/meta_mock/report/*.bracken.report -o /qib/research-projects/cami/tiwari/meta_mock/report/bracken_estimates.txt
```
## Extracting genus and species level mapping with kraken ouptut
#
Filter data using extract_report.py
```
python3 /qib/research-projects/cami/tiwari/meta_mock/scripts/extract_report.py \
-i /qib/research-projects/cami/tiwari/meta_mock/report/merged_kreports.txt \
-o /qib/research-projects/cami/tiwari/meta_mock/report/filtered_kreports.txt
```

