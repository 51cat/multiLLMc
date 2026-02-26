import scanpy as sc
import json
import pandas as pd
import numpy as np

def run_and_export_markers_json_strict(adata_path, topn=10, groupby='leiden', method='wilcoxon'):
    # 1. 加载数据
    adata = sc.read_h5ad(adata_path)
    
    # 2. 跑差异分析 (计算所有基因，确保能选出足够的 topn)
    print(f"喵！五一正在进行显著性差异分析（P < 0.05）...")
    sc.tl.rank_genes_groups(adata, groupby=groupby, method=method, n_genes=adata.n_vars) 

    result_dict = {}
    clusters = sorted(adata.obs[groupby].unique())
    
    for cluster in clusters:
        # 3. 计算 Cluster 占比
        cluster_cell_count = (adata.obs[groupby] == cluster).sum()
        cluster_pct = f"{(cluster_cell_count / adata.n_obs * 100):.2f}%"

        # 4. 获取差异分析结果并严格过滤
        df = sc.get.rank_genes_groups_df(adata, group=str(cluster))
        
        # 严格过滤：1. log2fc > 0  2. pvals_adj < 0.05 (校正后P值更靠谱喵)
        # 然后按 log2fc 从大到小排序
        df_filtered = df[(df['logfoldchanges'] > 0) & (df['pvals_adj'] < 0.05)]
        df_top = df_filtered.sort_values('logfoldchanges', ascending=False).head(topn)
        
        marker_genes = df_top['names'].tolist()
        log2fcs = [round(float(x), 3) for x in df_top['logfoldchanges'].tolist()]
        
        # 5. 计算在该 cluster 内的表达比例
        if len(marker_genes) > 0:
            cluster_mask = adata.obs[groupby] == cluster
            # 定位基因索引
            gene_indices = [adata.var_names.get_loc(g) for g in marker_genes]
            sub_matrix = adata[cluster_mask, :].X[:, gene_indices]
            
            if hasattr(sub_matrix, "toarray"):
                sub_matrix = sub_matrix.toarray()
            
            # 计算非零表达比例
            exp_pcts = [round(float((sub_matrix[:, i] > 0).mean() * 100), 2) for i in range(len(marker_genes))]
        else:
            # 如果这个 cluster 一个显著基因都没有，就给空列表喵
            exp_pcts = []

        # 6. 拼装
        result_dict[f"cluster_{cluster}"] = {
            "cluster_name": str(cluster),
            "cluster_pct": cluster_pct,
            "marker_gene": marker_genes,
            "marker_gene_log2fc": log2fcs,
            "marker_gene_exp_pct": exp_pcts
        }

    # 7. 打印紧凑型 JSON
    print(json.dumps(result_dict, ensure_ascii=False))

# 使用方法：
# run_and_export_markers_json_strict('data.h5ad', topn=10, groupby='leiden')

# 使用示例：
run_and_export_markers_json_strict('input2.h5ad', topn=10, groupby='leiden')