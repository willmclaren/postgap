from __future__ import absolute_import
from postgap.DataModel import *
from postgap.Globals import BLACKLISTED_REGIONS

def region_filter(clusters):
	return [cluster for cluster in clusters if not cluster_overlap_regions(cluster, BLACKLISTED_REGIONS)]

def cluster_overlap_regions(cluster, regions):
	return not any(cluster_overlap_region(cluster, region) for region in regions)

def cluster_overlap_region(cluster, region):
	return not any(snp_overlap_region(snp, region) for snp in cluster.ld_snps)

def snp_overlap_region(snp, region):
	return snp.chrom == region.chrom and snp.pos >= region.start and snp.pos < region.end
