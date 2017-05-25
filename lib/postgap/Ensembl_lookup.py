#! /usr/bin/env python

from __future__ import absolute_import

"""

Copyright [1999-2016] EMBL-European Bioinformatics Institute

Licensed under the Apache License, Version 2.0 (the "License")
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

		 http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

"""

"""

	Please email comments or questions to the public Ensembl
	developers list at <http://lists.ensembl.org/mailman/listinfo/dev>.

	Questions may also be sent to the Ensembl help desk at
	<http://www.ensembl.org/Help/Contact>.

"""

import postgap.REST
from postgap.DataModel import *
import postgap.Globals
from postgap.Utils import *

ENSEMBL_REST_SERVER = "http://grch37.rest.ensembl.org"
known_genes = {}

def get_gene(gene_name):
	"""

		Get gene details from name
		* string
		Returntype: Gene

	"""
	if gene_name not in known_genes:
		if gene_name[:4] != 'ENSG':
			known_genes[gene_name] = fetch_gene(gene_name)
		else:
			known_genes[gene_name] = fetch_gene_id(gene_name)
	return known_genes[gene_name]

def fetch_gene(gene_name):
	"""

		Get gene details from name
		* string
		Returntype: Gene

	"""
	server = ENSEMBL_REST_SERVER
	ext = "/lookup/symbol/%s/%s?content-type=application/json" % (postgap.Globals.SPECIES, gene_name)
	try:
		hash = postgap.REST.get(server, ext)
		return Gene(
			name = gene_name,
			id = hash['id'],
			chrom = hash['seq_region_name'],
			tss = int(hash['start']) if hash['strand'] > 0 else int(hash['end']),
			biotype = hash['biotype']
			)
	except:
		return None

def fetch_gene_id(gene_id):
	"""

		Get gene details from name
		* string
		Returntype: Gene

	"""
	server = ENSEMBL_REST_SERVER
	ext = "/lookup/id/%s?content-type=application/json" % (gene_id)
	try:
		hash = postgap.REST.get(server, ext)
		return Gene(
			name = hash['display_name'],
			id = hash['id'],
			chrom = hash['seq_region_name'],
			tss = int(hash['start']) if hash['strand'] > 0 else int(hash['end']),
			biotype = hash['biotype']
			)
	except:
		return None


def get_ensembl_gene(ensembl_id):
	"""

		Get gene details from name
		* string
		Returntype: Gene

	"""
	if ensembl_id not in known_genes:
		known_genes[ensembl_id] = fetch_ensembl_gene(ensembl_id)
	return known_genes[ensembl_id]

def fetch_ensembl_gene(ensembl_id):
	"""

		Get gene details from name
		* string
		Returntype: Gene

	"""
	server = ENSEMBL_REST_SERVER
	ext = "/lookup/id/%s?content-type=application/json" % (ensembl_id)
	hash = postgap.REST.get(server, ext)
	return Gene(
		name = hash['display_name'],
		id = ensembl_id,
		chrom = hash['seq_region_name'],
		tss = int(hash['start']) if hash['strand'] > 0 else int(hash['end']),
		biotype = hash['biotype']
		)

def get_snp_locations(rsIDs):
	"""

		Get SNP details from rsID
		* [ string ]
		Returntype: [ SNP ]

	"""
	if len(rsIDs) == 0:
		return []

	res = get_snp_locations_simple(rsIDs) 

	if len(res) == 0:
		if len(rsIDs) == 1:
			return []
		else:
			return get_snp_locations(rsIDs[:len(rsIDs)/2]) + get_snp_locations(rsIDs[len(rsIDs)/2:])
	else:
		return res
	


def get_snp_locations_simple(rsIDs):
	"""

		Get SNP details from rsID
		* [ string ]
		Returntype: [ SNP ]

	"""

	server = ENSEMBL_REST_SERVER
	ext = "/variation/%s?content-type=application/json" % (postgap.Globals.SPECIES)
	hash = concatenate_hashes(postgap.REST.get(server, ext, data={'ids':chunk}) for chunk in chunks(rsIDs, 999))
	for record in hash.values():
		for synonym in record["synonyms"]:
			hash[synonym] = record

	'''
		Example response:
		{
			"rs56116432": {
				"source": "Variants (including SNPs and indels) imported from dbSNP",
				"mappings": [
					{
						"location": "9:133256042-133256042",
						"assembly_name": "GRCh38",
						"end": 133256042,
						"seq_region_name": "9",
						"strand": 1,
						"coord_system": "chromosome",
						"allele_string": "C/T",
						"start": 133256042
					},
				],
				"name": "rs56116432",
				"MAF": "0.00259585",
				"ambiguity": "Y",
				"var_class": "SNP",
				"synonyms": [],
				"evidence": [
					"Multiple_observations",
					"Frequency",
					"1000Genomes",
					"ESP",
					"ExAC"
				],
				"ancestral_allele": "C",
				"minor_allele": "T",
				"most_severe_consequence": "missense_variant"
			}
		}
	'''
	results = []
	for rsID in rsIDs:
		if rsID in hash:
			for mapping in hash[rsID]['mappings']:
				results.append(
					SNP(
						rsID = rsID,
						chrom = mapping['seq_region_name'],
						pos = (int(mapping['start']) + int(mapping['end'])) / 2
					)
				)
	return results

