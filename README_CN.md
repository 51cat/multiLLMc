# MultiLLMc

多LLM协作的单细胞RNA-seq细胞类型注释工具

一个利用多个大语言模型协作讨论来注释单细胞RNA测序数据中细胞类型的框架。

## 注释流程

MultiLLMc 采用三阶段协作流程来实现高质量的细胞类型注释：

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Seminar   │ ──► │   Reviewer  │ ──► │  Harmonizer │
│  多模型讨论  │     │   质量审核   │     │   共识整合   │
└─────────────┘     └─────────────┘     └─────────────┘
```

### 阶段1：Seminar（多模型讨论）

多个LLM模型独立分析每个聚类的标记基因，给出各自的细胞类型判断：

- 每个模型基于标记基因、log2FC、表达比例等指标独立判断
- 输出包括主要细胞类型、亚型和详细推理依据
- 支持识别"低质量细胞"和"双细胞(Doublet)"

### 阶段2：Reviewer（质量审核）

对每个模型的注释结果进行专家级审核：

- **基因忠实度检查**：验证模型是否使用了实际提供的标记基因，检测"幻觉基因"
- **生物学有效性检查**：判断注释是否符合组织特异性生物学背景
- **可靠性评分**：综合给出0-100分的可信度评分
- **自动纠错**：对未通过审核的注释，要求模型重新注释（最多3次）

### 阶段3：Harmonizer（共识整合）

综合所有模型的审核结果，达成最终共识：

- 分析各模型间的意见一致性
- 合并同义命名（如"T细胞"和"T淋巴细胞"）
- 计算共识比例和熵值
- 输出统一的细胞类型结论

## 安装

```bash
pip install multillmc
```

或从源码安装：

```bash
git clone https://github.com/51cat/multiLLMc.git
cd multiLLMc
pip install -e .
```

## 快速开始

```python
from mllmcelltype import Seminar, Reviewer, Harmonizer

# 定义每个聚类的标记基因
marker_genes = {
    "cluster_0": ["CD3D", "CD3E", "CD3G", "IL7R", "TCF7"],  # T细胞
    "cluster_1": ["CD79A", "CD79B", "MS4A1", "IGHM", "IGKC"],  # B细胞
    "cluster_2": ["CD14", "LYZ", "S100A8", "S100A9", "FCN1"],  # 单核细胞
}

# 第一步：初始化并运行多模型讨论
seminar = Seminar(
    marker_dict=marker_genes,
    species='human',
    tissue='PBMC'
)

seminar.set_api("your-api-key")
seminar.set_model_list(['gpt-4o', 'claude-3-sonnet', 'gemini-pro'])
seminar.set_provider('openrouter')
seminar.make_init_ann_promopt('major_celltype')
seminar.start()

# 获取初步结果
cluster_results = seminar.get_cluster_results()

# 第二步：质量审核（可选）
reviewer = Reviewer(seminar)
reviewer.set_api("your-api-key")
reviewer.set_provider('openrouter')
reviewer.get_seminar_results()
reviewer.review()
seminar = reviewer.add_review_results_to_seminar()

# 第三步：共识整合（可选）
harmonizer = Harmonizer(seminar)
harmonizer.set_api("your-api-key")
harmonizer.set_provider('openrouter')
harmonizer.get_seminar_results()
harmonizer.check()
consensus = harmonizer.get_check_result()

# 输出最终结果
for cluster, result in consensus.items():
    print(f"{cluster}: {result['consensus_cell_type']}")
```

## 命令行使用

```bash
# 查看帮助
multillmc --help

# 列出可用的API提供者
multillmc providers

# 执行注释
multillmc annotate \
    --markers markers.json \
    --api-key YOUR_API_KEY \
    --provider openrouter \
    --models gpt-4o,claude-3-sonnet \
    --species human \
    --tissue PBMC \
    --output results.json
```

## API提供者

支持的API提供者：
- `n1n`: N1N API Gateway
- `openrouter`: OpenRouter统一API接口

## 输入数据格式

标记基因JSON文件格式：

```json
{
    "cluster_0": ["GENE1", "GENE2", "GENE3"],
    "cluster_1": ["GENE4", "GENE5", "GENE6"],
    "cluster_2": ["GENE7", "GENE8", "GENE9"]
}
```

## 依赖要求

- Python >= 3.10
- langchain >= 0.2.0
- langchain-openai >= 0.1.0
- pydantic >= 2.0.0
- jinja2 >= 3.1.0

## 许可证

MIT License

## 作者

51cat
