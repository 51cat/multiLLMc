from seminar import Seminar
from harmonizer import Harmonizer
from reviewer import Reviewer

import json   

def write_json(dict, out):
        json_str = json.dumps(dict, indent=4)
        with open(out,"w") as fd:
            fd.write(json_str)

def main():
    api = "sk-VW019xQdJlI0EJKpESIj8UcUYWTMyBop78hsJQ2W5P8ppe3D"
    models = ['gemini-3-pro-preview']

    all_marker_genes = '{"cluster_1": {"cluster_name": "1", "cluster_pct": "8.97%", "marker_gene": ["PCP2", "PLXNB1", "CFAP47", "MAPK15", "EPOR", "RGL3", "KCNC3", "KCNK15", "PVT1", "POTEF"], "marker_gene_log2fc": [3.269, 2.581, 2.575, 2.569, 2.546, 2.468, 2.459, 2.348, 2.26, 2.17], "marker_gene_exp_pct": [14.04, 88.22, 5.56, 14.6, 23.45, 56.88, 33.81, 16.91, 67.32, 18.94]}, "cluster_2": {"cluster_name": "2", "cluster_pct": "8.53%", "marker_gene": ["COL11A1", "INHBA", "COL10A1", "MMP11", "CTHRC1", "ADAMTS14", "ADAM12", "CDH11", "COL5A1", "SCG2"], "marker_gene_log2fc": [5.289, 4.942, 4.886, 4.817, 4.783, 4.657, 4.519, 4.483, 4.471, 4.448], "marker_gene_exp_pct": [45.93, 36.97, 26.73, 25.8, 67.89, 31.19, 24.68, 45.53, 87.15, 6.48]}, "cluster_3": {"cluster_name": "3", "cluster_pct": "7.63%", "marker_gene": ["MYH11", "CNN1", "C11orf96", "PLN", "CACNA1H", "SYNM", "LDB3", "GRIA2", "AOC3", "JPH2"], "marker_gene_log2fc": [5.356, 4.918, 4.338, 4.317, 4.185, 4.05, 3.988, 3.973, 3.84, 3.812], "marker_gene_exp_pct": [94.37, 69.51, 70.56, 20.52, 5.69, 10.7, 2.56, 8.04, 22.3, 9.24]}, "cluster_4": {"cluster_name": "4", "cluster_pct": "6.98%", "marker_gene": ["DACH1", "FAM107A", "BMP6", "SERPINA5", "SOX9", "KCNK15", "ITGB6", "CCND1", "TMEM123", "FST"], "marker_gene_log2fc": [1.988, 1.966, 1.934, 1.904, 1.823, 1.714, 1.695, 1.687, 1.65, 1.643], "marker_gene_exp_pct": [5.39, 15.15, 4.6, 2.22, 20.42, 10.03, 4.01, 17.15, 42.83, 2.36]}, "cluster_5": {"cluster_name": "5", "cluster_pct": "6.94%", "marker_gene": ["CD163", "MRC1", "C1QC", "CD14", "CSF1R", "FCGR2A", "MS4A6A", "C5AR1", "F13A1", "LILRB5"], "marker_gene_log2fc": [5.912, 5.718, 5.654, 5.525, 5.477, 5.399, 5.397, 5.381, 5.375, 5.359], "marker_gene_exp_pct": [18.85, 14.99, 74.75, 31.13, 13.93, 40.78, 47.07, 21.95, 15.81, 3.5]}, "cluster_6": {"cluster_name": "6", "cluster_pct": "6.72%", "marker_gene": ["MYH11", "CNN1", "C11orf96", "GRIA2", "PLN", "SYNPO2", "MYLK", "MAOB", "PDE5A", "SYNM"], "marker_gene_log2fc": [4.65, 3.263, 2.754, 2.592, 2.464, 2.216, 2.18, 2.176, 2.048, 1.889], "marker_gene_exp_pct": [76.25, 36.29, 34.6, 3.05, 6.68, 6.72, 20.89, 3.35, 3.22, 2.81]}, "cluster_7": {"cluster_name": "7", "cluster_pct": "6.76%", "marker_gene": ["RAD54L", "KIF18B", "CDCA3", "AURKB", "TYMS", "MYBL2", "CDK1", "CIP2A", "E2F1", "FANCA"], "marker_gene_log2fc": [3.659, 3.324, 3.306, 3.075, 3.063, 3.033, 3.03, 2.94, 2.909, 2.903], "marker_gene_exp_pct": [22.93, 29.53, 21.68, 30.51, 44.74, 49.16, 41.3, 43.37, 20.64, 5.23]}, "cluster_8": {"cluster_name": "8", "cluster_pct": "6.22%", "marker_gene": ["H19", "LCN2", "MUC16", "CP", "POU2F3", "CYP4B1", "MAPK15", "CD47", "LAPTM4B", "PLXNB1"], "marker_gene_log2fc": [2.163, 1.901, 1.898, 1.817, 1.816, 1.797, 1.787, 1.778, 1.741, 1.701], "marker_gene_exp_pct": [97.0, 57.84, 61.49, 74.96, 3.93, 47.14, 14.71, 93.81, 91.37, 87.03]}, "cluster_9": {"cluster_name": "9", "cluster_pct": "6.13%", "marker_gene": ["ABCA10", "C7", "FAIM2", "TNXB", "ABCA8", "PI16", "DPT", "SRPX", "COL4A4", "PAMR1"], "marker_gene_log2fc": [5.878, 5.762, 4.823, 4.808, 4.733, 4.579, 4.343, 4.311, 4.048, 4.047], "marker_gene_exp_pct": [38.38, 78.62, 2.62, 21.25, 30.3, 3.6, 10.59, 14.85, 1.24, 15.35]}, "cluster_10": {"cluster_name": "10", "cluster_pct": "5.38%", "marker_gene": ["MYBL2", "H19", "CCNE1", "CENPF", "UCHL1", "MCM4", "LAPTM4B", "MCM2", "HMGA1", "SMC4"], "marker_gene_log2fc": [1.911, 1.878, 1.828, 1.785, 1.753, 1.721, 1.696, 1.672, 1.651, 1.636], "marker_gene_exp_pct": [26.75, 91.85, 27.72, 22.76, 62.31, 24.23, 82.75, 23.72, 56.52, 44.47]}, "cluster_11": {"cluster_name": "11", "cluster_pct": "2.95%", "marker_gene": ["SFRP4", "SFRP1", "SMAP2", "DCN", "NDRG2", "SOX2-OT", "TFPI", "ECM1", "NAMPT", "APCDD1"], "marker_gene_log2fc": [1.581, 0.623, 0.62, 0.517, 0.446, 0.42, 0.42, 0.272, 0.244, 0.168], "marker_gene_exp_pct": [6.64, 2.0, 1.16, 16.05, 1.3, 17.31, 1.27, 1.7, 10.24, 1.31]}, "cluster_12": {"cluster_name": "12", "cluster_pct": "4.72%", "marker_gene": ["SLC2A1", "TFPI2", "CYP24A1", "NMB", "NDRG1", "TNFRSF11B", "VEGFA", "ALDOA", "BNIP3", "LAMC2"], "marker_gene_log2fc": [3.956, 3.877, 3.865, 3.337, 3.053, 2.933, 2.931, 2.667, 2.642, 2.603], "marker_gene_exp_pct": [51.83, 66.01, 11.14, 12.58, 75.91, 15.02, 57.19, 42.49, 19.01, 7.7]}, "cluster_13": {"cluster_name": "13", "cluster_pct": "4.60%", "marker_gene": ["CCL14", "SELP", "CLDN5", "EGFL7", "TEK", "PTPRB", "NOSTRIN", "NRN1", "FLT4", "MMRN2"], "marker_gene_log2fc": [6.81, 6.771, 6.762, 5.626, 5.613, 5.57, 5.512, 5.426, 5.397, 5.388], "marker_gene_exp_pct": [20.34, 8.85, 19.44, 19.27, 8.89, 30.1, 11.76, 12.13, 9.19, 11.72]}, "cluster_14": {"cluster_name": "14", "cluster_pct": "4.30%", "marker_gene": ["TOP2A", "NEK2", "CDC20", "CDCA2", "BUB1", "CCNB1", "CENPA", "UBE2C", "TPX2", "ASPM"], "marker_gene_log2fc": [3.744, 3.608, 3.557, 3.467, 3.423, 3.368, 3.366, 3.354, 3.347, 3.342], "marker_gene_exp_pct": [65.83, 28.76, 37.78, 39.36, 32.91, 39.94, 27.77, 42.39, 65.41, 27.84]}, "cluster_15": {"cluster_name": "15", "cluster_pct": "2.75%", "marker_gene": ["SFRP4", "COMP", "LUM", "NRK", "BGN", "CCN2", "SERPINE1", "ELN", "MEG3", "COL10A1"], "marker_gene_log2fc": [3.157, 3.145, 3.094, 2.847, 2.758, 2.748, 2.672, 2.667, 2.619, 2.592], "marker_gene_exp_pct": [23.39, 4.88, 53.64, 2.57, 56.99, 29.3, 12.79, 4.72, 16.34, 8.02]}, "cluster_16": {"cluster_name": "16", "cluster_pct": "2.30%", "marker_gene": ["CD8A", "TRBC1", "GZMA", "CD2", "TRAC", "GZMK", "CD3E", "GZMH", "SH2D1A", "GPR174"], "marker_gene_log2fc": [7.603, 7.448, 7.337, 7.142, 7.064, 6.953, 6.919, 6.858, 6.638, 6.599], "marker_gene_exp_pct": [30.89, 27.73, 10.59, 17.41, 43.32, 5.83, 19.71, 10.33, 7.85, 7.29]}, "cluster_17": {"cluster_name": "17", "cluster_pct": "1.87%", "marker_gene": ["HDC", "MS4A2", "ADCYAP1", "CTSG", "SLC18A2", "KIT", "DUX4", "HNF4A", "SOX2-OT", "LPA"], "marker_gene_log2fc": [5.241, 5.042, 4.946, 4.813, 4.637, 4.393, 3.944, 3.773, 3.684, 3.663], "marker_gene_exp_pct": [1.84, 1.72, 1.84, 1.72, 1.86, 2.37, 11.68, 2.15, 76.61, 3.51]}, "cluster_18": {"cluster_name": "18", "cluster_pct": "1.43%", "marker_gene": ["FCGBP", "CLEC5A", "TREM2", "CX3CR1", "OLR1", "HAVCR2", "C1QC", "ADORA3", "KCNK13", "LILRB4"], "marker_gene_log2fc": [4.337, 4.246, 3.988, 3.645, 3.588, 3.463, 3.408, 3.401, 3.383, 3.341], "marker_gene_exp_pct": [49.67, 27.12, 13.91, 15.65, 6.67, 12.57, 81.41, 9.74, 5.61, 9.13]}, "cluster_19": {"cluster_name": "19", "cluster_pct": "1.28%", "marker_gene": ["ENPEP", "AVPR1A", "COL4A1", "MMP9", "RGS5", "GJC1", "CCDC102B", "PGF", "HEYL", "TBX2"], "marker_gene_log2fc": [5.612, 5.427, 5.133, 4.941, 4.93, 4.907, 4.843, 4.542, 4.535, 4.48], "marker_gene_exp_pct": [37.18, 35.13, 90.25, 12.47, 28.22, 13.98, 26.87, 17.56, 61.07, 32.52]}, "cluster_20": {"cluster_name": "20", "cluster_pct": "0.97%", "marker_gene": ["PAX2", "WDR72", "ERP27", "CD22", "LGR5", "HNF1B", "CDH16", "SLITRK5", "NXF3", "AC007906.2"], "marker_gene_log2fc": [6.192, 5.381, 4.968, 4.894, 4.793, 4.461, 4.351, 4.341, 4.012, 3.964], "marker_gene_exp_pct": [9.27, 6.47, 14.61, 13.65, 9.07, 4.71, 3.5, 4.48, 3.53, 42.14]}, "cluster_21": {"cluster_name": "21", "cluster_pct": "0.73%", "marker_gene": ["STEAP4", "CNR1", "CCL19", "ADAMTS4", "SSTR2", "COL25A1", "CCDC102B", "RASD1", "TINAGL1", "KCNJ8"], "marker_gene_log2fc": [5.93, 5.694, 5.262, 5.145, 4.899, 4.757, 4.505, 4.355, 4.303, 4.268], "marker_gene_exp_pct": [32.66, 6.99, 12.78, 36.31, 5.82, 3.72, 15.64, 9.99, 29.04, 12.47]}, "cluster_22": {"cluster_name": "22", "cluster_pct": "0.70%", "marker_gene": ["ESM1", "FLT1", "PLVAP", "GABRD", "FOLH1", "PCDH17", "ANGPT2", "KDR", "NOTCH4", "APLNR"], "marker_gene_log2fc": [7.755, 6.497, 6.297, 5.929, 5.816, 5.619, 5.47, 5.407, 5.4, 5.343], "marker_gene_exp_pct": [60.56, 91.59, 81.14, 20.33, 21.76, 34.79, 23.44, 62.53, 46.92, 26.63]}, "cluster_23": {"cluster_name": "23", "cluster_pct": "0.51%", "marker_gene": ["PRG4", "CPA4", "CALB2", "BNC1", "ANXA8", "UPK3B", "RGS4", "PROCR", "AQP9", "PTGER3"], "marker_gene_log2fc": [8.183, 6.844, 6.79, 6.156, 5.486, 5.307, 5.301, 5.068, 5.022, 4.908], "marker_gene_exp_pct": [54.39, 31.56, 48.34, 43.57, 31.91, 10.42, 47.99, 64.67, 9.68, 30.32]}, "cluster_24": {"cluster_name": "24", "cluster_pct": "0.48%", "marker_gene": ["TNS4", "GABRP", "FGFR3", "TRIM29", "ANXA8", "AGR2", "MUC4", "DSG3", "CYP3A5", "NECTIN1"], "marker_gene_log2fc": [7.48, 6.546, 6.083, 6.057, 6.014, 5.947, 5.859, 5.648, 5.145, 5.124], "marker_gene_exp_pct": [49.77, 13.1, 26.05, 57.1, 28.19, 16.33, 5.36, 8.79, 10.24, 16.22]}, "cluster_25": {"cluster_name": "25", "cluster_pct": "0.14%", "marker_gene": ["C20orf85", "CDHR4", "CFAP100", "FAM216B", "DNAH11", "TEKT1", "LDLRAD1", "ERICH3", "FAM183A", "DNAH10"], "marker_gene_log2fc": [8.384, 7.713, 7.535, 7.332, 7.112, 7.101, 7.011, 6.84, 6.802, 6.689], "marker_gene_exp_pct": [86.4, 73.35, 89.8, 58.86, 45.44, 61.9, 57.96, 61.18, 72.27, 40.25]}}'


    celltype_seminar = Seminar(
        all_marker_genes, tissue='ovarian cancer tissue sample', tissue_desc='with partial inclusion of adjacent fallopian tube tissue', species='human'
    )

    celltype_seminar.set_api(api)
    celltype_seminar.set_model_list(models)
    celltype_seminar.set_provider('n1n')
    celltype_seminar.make_init_ann_promopt2(
         'new',
         spec='human',
         tissue='ovarian cancer tissue sample',
         tissue_desc='with partial inclusion of adjacent fallopian tube tissue',
         markers=all_marker_genes
         )
    
    
    print(celltype_seminar.promopt)
    celltype_seminar.start()

    write_json(celltype_seminar.response_final_dict, '../init2.json')
    '''
    rev = Reviewer(celltype_seminar)
    rev.set_api(api)
    rev.set_provider('n1n')
    rev.get_seminar_results()
    rev.review()
    celltype_seminar = rev.add_review_results_to_seminar()
    write_json(celltype_seminar.final_review_results, '../review.json')

    reconciler = Harmonizer(celltype_seminar)
    reconciler.set_api(api)
    reconciler.set_provider('n1n')
    reconciler.get_seminar_results()
    reconciler.check()
    write_json(reconciler.get_check_result(), '../check.json')
    '''
if __name__ == '__main__':
    main()


