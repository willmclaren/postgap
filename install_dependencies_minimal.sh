#!/bin/bash

mkdir -p bin

## Tabix, bgzip
git clone https://github.com/samtools/htslib.git
cd htslib
git checkout 1.3.2
make
cp tabix bgzip ../bin
cd ..

# pybedtools v0.7.8, requests, pandas
pip install pybedtools==0.7.4 requests pandas flask cherrypy

# ld_vcf from ensembl-variation
gcc -Wall -O3 C/ld_vcf.c -I htslib/htslib -o bin/ld_vcf -Lhtslib -Wl,-rpath,htslib -lhts -lm
