"""
Comprehensive marker genes dataset for testing
Format matches the expected input for MultiLLMc annotation
"""

MARKER_GENES_PBMC = {
    "cluster_0": ["CD3D", "CD3E", "CD3G", "IL7R", "TCF7", "CCR7", "LEF1", "MALAT1"],
    "cluster_1": ["CD79A", "CD79B", "MS4A1", "IGHM", "IGKC", "CD19", "PAX5", "EBF1"],
    "cluster_2": ["CD14", "LYZ", "S100A8", "S100A9", "FCN1", "CSF1R", "ITGAM", "CST3"],
    "cluster_3": ["FCGR3A", "NCR1", "KLRD1", "GNLY", "PRF1", "GZMB", "NCAM1", "KLRC1"],
    "cluster_4": ["PPBP", "PF4", "TUBB1", "GP9", "ITGA2B", "GP1BA", "SELP", "THPO"],
    "cluster_5": ["HBB", "HBA1", "HBA2", "ALAS2", "GATA1", "KLF1", "SLC4A1", "AHSP"],
    "cluster_6": ["CD4", "IL7R", "CCR7", "TCF7", "LEF1", "MALAT1", "S100A4", "ANXA1"],
    "cluster_7": ["CD8A", "CD8B", "GZMK", "GZMA", "CCL5", "NKG7", "CST7", "PRF1"]
}

MARKER_GENES_OVARIAN = {
    "cluster_1": ["PCP2", "PLXNB1", "CFAP47", "MAPK15", "PVT1"],
    "cluster_2": ["COL11A1", "COL10A1", "INHBA", "MMP11", "CTHRC1"],
    "cluster_3": ["MYH11", "CNN1", "SYNM", "PLN", "SYNPO2"],
    "cluster_4": ["DACH1", "SOX9", "BMP6", "CCND1", "ITGB6"],
    "cluster_5": ["CD163", "MRC1", "CD14", "CSF1R", "C1QC", "FCGR2A"],
    "cluster_6": ["MYH11", "CNN1", "MYLK", "CASQ2", "ADCY2"],
    "cluster_7": ["RAD54L", "AURKB", "TYMS", "KIF18B", "CDK1"],
    "cluster_8": ["MUC16", "H19", "LCN2", "CP", "F2"]
}

MARKER_GENES_DOUBLET_EXAMPLE = {
    "cluster_doublet": ["CD3D", "CD79A", "CD14", "MS4A1", "CD3E", "CD19"],
    "cluster_low_quality": ["MT-ND1", "MT-ND2", "MT-CO1", "MT-CO2", "MT-ATP6"],
    "cluster_normal": ["CD3D", "CD3E", "CD3G", "IL7R", "TCF7"]
}
