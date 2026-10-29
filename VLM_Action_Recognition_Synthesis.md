# CLIP/VLM 零样本与少样本动作识别综合笔记 (2024-2026)
# Synthesis Note: CLIP/VLM Zero-Shot and Few-Shot Action Recognition (2024-2026)

## 概述 | Overview

本文档综合分析了 2024-2026 年间基于 CLIP 和视觉-语言模型（VLM）的零样本、少样本及开放词汇动作识别研究进展，重点关注技术路线分类、静态偏差问题及未来研究方向。

This document synthesizes recent advances in CLIP/VLM-based zero-shot, few-shot, and open-vocabulary action recognition (2024-2026), focusing on technical taxonomy, static bias challenges, and future research directions.

---

## 1. 技术路线分类 | Technical Taxonomy

### 1.1 方法分类表 | Method Classification Table

| 方法 Method | 类型 Type | 核心机制 Core Mechanism | 静态偏差缓解 Static Bias Mitigation | 时空建模 Spatiotemporal Modeling |
|-------------|-----------|------------------------|-----------------------------------|----------------------------------|
| **GBC** (TCSVT 2024) | Graph-based | 区域级别图结构化描述 Region-level graph captioning | ✓ 多区域关系建模 Multi-region relations | △ 有限时序聚合 Limited temporal |
| **EPK-CLIP** (ESWA 2024) | Knowledge Transfer | 预训练知识探索与蒸馏 Pre-trained knowledge exploration | ✓ 外部知识注入 External knowledge injection | ○ 主要依赖CLIP Main reliance on CLIP |
| **SC-CLIP** (2024) | Prompt Engineering | 语义组合式提示学习 Semantic composition prompts | ✓✓ 动词-名词解耦 Verb-noun decomposition | △ 帧级聚合 Frame-level aggregation |
| **VEDA** (2024) | Adapter + Enhancement | 视觉-语言增强网络 Vision-language enhancement | ✓ 跨模态对齐强化 Cross-modal alignment | ✓ 适配器时序融合 Adapter temporal fusion |
| **DiST** (2024) | Decoupled Compensator | 时空解耦知识补偿 Spatio-temporal decoupled compensation | ✓✓ 显式时空分离 Explicit spatiotemporal separation | ✓✓ 专用时序补偿器 Dedicated temporal compensator |
| **SceneVLP** (2024) | Scene-aware Pre-training | 场景感知预训练 Scene-aware VLP | ✓ 场景上下文建模 Scene context modeling | ✓ 视频级预训练 Video-level pre-training |
| **MoveNet** (2024) | Motion Modulation | 运动感知调制机制 Motion-aware modulation | ✓✓✓ 运动显式建模 Explicit motion modeling | ✓✓✓ 光流/运动特征 Optical flow/motion features |
| **CoOp/CoCoOp** (2022) | Prompt Learning | 可学习提示向量 Learnable prompt vectors | ○ 无针对性设计 No specific design | ○ 图像级方法 Image-level method |

**图例 Legend:**
- ✓✓✓ = 强 Strong | ✓✓ = 中等 Moderate | ✓ = 弱 Weak | △ = 间接 Indirect | ○ = 无/最小 None/Minimal

---

## 2. 静态偏差问题分析 | Static Bias Analysis

### 2.1 问题定义 | Problem Definition

**静态偏差（Static Bias）**指基于 CLIP 的动作识别模型过度依赖视频关键帧中的静态视觉线索（物体、场景、人物姿态），而忽略动作的时序动态特征（运动轨迹、速度变化、时序上下文）的现象。

**Static bias** refers to the phenomenon where CLIP-based action recognition models over-rely on static visual cues (objects, scenes, human poses) in key frames while neglecting temporal dynamic features of actions (motion trajectories, velocity changes, temporal context).

### 2.2 各方法应对策略 | Mitigation Strategies by Method

#### **GBC (Graph-Based Captioning)**
- **策略 Strategy:** 通过区域间关系图捕获空间关联
- **效果 Effectiveness:** 部分缓解，但仍缺乏显式时序建模
- **局限 Limitation:** 图结构主要针对单帧或少量帧，时序关系隐式

#### **EPK-CLIP**
- **策略 Strategy:** 引入外部预训练知识库
- **效果 Effectiveness:** 知识迁移可补充动作概念，但未直接处理时序
- **局限 Limitation:** 依赖外部数据质量，动态特征仍欠缺

#### **SC-CLIP (Semantic Composition)**
- **策略 Strategy:** 动词-名词语义解耦，强调动作动词
- **效果 Effectiveness:** **较强**，通过组合语义减少对静态物体的依赖
- **局限 Limitation:** 仍依赖帧级特征聚合，未建模帧间运动

#### **VEDA (Vision-Language Enhancement)**
- **策略 Strategy:** 适配器网络增强跨模态对齐
- **效果 Effectiveness:** 中等，适配器可学习时序模式但未显式设计
- **局限 Limitation:** 黑盒式增强，缺乏可解释的时序分解

#### **DiST (Decoupled Compensator)**
- **策略 Strategy:** **显式时空解耦** + 知识补偿器
- **效果 Effectiveness:** **强**，专用时序分支减少静态线索主导
- **局限 Limitation:** 补偿器设计复杂度高，可能引入额外超参数

#### **SceneVLP**
- **策略 Strategy:** 场景级预训练增强上下文理解
- **效果 Effectiveness:** 中等，场景理解有助于动作语义但不直接建模运动
- **局限 Limitation:** 预训练成本高，静态场景仍可能主导

#### **MoveNet (Motion Modulation)**
- **策略 Strategy:** **运动特征显式调制**（光流、运动边界）
- **效果 Effectiveness:** **最强**，直接建模运动动态
- **局限 Limitation:** 需额外光流提取，计算开销增加

### 2.3 静态偏差缓解效果排名 | Ranking by Static Bias Mitigation

1. **MoveNet** (运动显式建模)
2. **DiST** (时空解耦补偿)
3. **SC-CLIP** (语义组合解耦)
4. **VEDA** (适配器增强)
5. **GBC** (区域图关系)
6. **SceneVLP** (场景预训练)
7. **EPK-CLIP** (知识迁移)
8. **CoOp/CoCoOp** (无针对性设计)

---

## 3. 稀疏融合空白 | Open Gaps for Sparse Fusion

### 3.1 现有方法的局限 | Limitations of Existing Methods

#### 3.1.1 单一模态主导 | Single Modality Dominance
- 多数方法仍以 **视觉特征为主导**，文本提示作为辅助
- **语言侧稀疏信号**（动作动词、时序副词）未充分利用
- 跨模态融合通常是**密集加权**或**全局注意力**，缺乏稀疏选择性

#### 3.1.2 时序建模粗粒度 | Coarse Temporal Modeling
- 帧级聚合（平均池化、Transformer）忽略**关键时刻**（动作起始、峰值、结束）
- 缺乏**稀疏时序锚点**选择机制
- 运动建模（光流）与语义理解**解耦不充分**

#### 3.1.3 异构线索融合简单 | Simplistic Heterogeneous Cue Fusion
- 静态外观、运动动态、语言语义通常**直接拼接或加权**
- 缺乏**任务驱动的稀疏路由**（如动作类别自适应选择关键线索）
- 未考虑**线索冗余性**和**互补性**的权衡

---

### 3.2 BD-SPF 风格稀疏融合机会 | BD-SPF-Style Sparse Fusion Opportunities

**BD-SPF (Basis-Decomposed Sparse Prototype Fusion)** 是一种假设性的稀疏融合范式，受基函数分解和原型学习启发，适用于异构多模态线索融合。

#### 3.2.1 核心思想 | Core Idea
1. **基函数分解 Basis Decomposition:**
   - 将视频表征分解为 $\mathbf{V} = \sum_{k=1}^K w_k \mathbf{B}_k$，其中 $\mathbf{B}_k$ 为可学习基（静态、运动、场景、文本引导）
   - 稀疏权重 $w_k$ 通过 L1 正则化或 Gumbel-Softmax 学习

2. **原型驱动路由 Prototype-Driven Routing:**
   - 为每个动作类别学习多个原型（静态原型、运动原型、文本原型）
   - 输入视频与原型相似度决定**稀疏融合权重**

3. **时序锚点选择 Temporal Anchor Selection:**
   - 利用 **可学习的稀疏注意力** 选择关键帧（如动作开始、峰值时刻）
   - 避免密集时序建模，减少计算冗余

#### 3.2.2 优势 | Advantages
- **可解释性强:** 稀疏权重揭示哪些线索对特定动作重要
- **计算高效:** 仅激活关键基函数和时序锚点
- **动态自适应:** 不同动作类别自动选择不同融合策略（如"跳跃"侧重运动，"阅读"侧重静态）

#### 3.2.3 技术挑战 | Technical Challenges
- 如何设计**可微分的稀疏选择机制**（避免梯度消失）
- 基函数的**初始化和正交性**保证
- 原型学习与少样本泛化的**平衡**

---

## 4. 研究机会与建议 | Research Opportunities and Recommendations

### 4.1 关键研究方向 | Key Research Directions

#### 4.1.1 稀疏多模态融合 | Sparse Multimodal Fusion
- **目标:** 设计轻量级、可解释的异构线索融合模块
- **方法建议:**
  - 基于**门控稀疏专家**（Sparse MoE）的跨模态路由
  - **对比学习引导的基函数学习**（静态-运动对比原型）
  - **时序稀疏采样**（可学习的关键帧选择网络）

#### 4.1.2 显式运动-语义解耦 | Explicit Motion-Semantic Decoupling
- **目标:** 构建独立的运动分支和语义分支，通过稀疏融合整合
- **方法建议:**
  - 双流架构：一支建模光流/运动边界，一支建模CLIP静态特征
  - **运动条件的文本提示**（如"快速跑"vs"慢速跑"）
  - **解耦损失函数**（运动损失 + 语义损失 + 融合损失）

#### 4.1.3 少样本场景下的知识注入 | Knowledge Injection for Few-Shot
- **目标:** 在有限标注下最大化外部知识利用
- **方法建议:**
  - **知识图谱引导的原型初始化**（从 ConceptNet/WordNet 提取动作关系）
  - **跨数据集元学习**（预训练在大规模数据集，微调在目标数据集）
  - **半监督伪标签 + 稀疏融合**（置信度低的样本仅使用部分线索）

#### 4.1.4 开放词汇泛化 | Open-Vocabulary Generalization
- **目标:** 提升对未见动作类别的泛化能力
- **方法建议:**
  - **组合泛化**（将复杂动作分解为基本动作组合）
  - **零样本推理链**（如"投篮" = "举起手臂" + "快速释放"）
  - **大语言模型辅助描述生成**（LLM生成多样化动作描述作为文本输入）

---

### 4.2 适合 2026 年顶会投稿的研究方向 | Promising Directions for 2026 Top-Tier Conferences

| 方向 Direction | 创新点 Innovation | 技术难度 Difficulty | 实验成本 Experimental Cost | 投稿目标 Target Venue |
|----------------|------------------|--------------------|--------------------------|-----------------------|
| **稀疏原型融合网络** Sparse Prototype Fusion Network | 首次将稀疏基分解用于动作识别 | 中高 | 2 A40 × 2 周 | **CVPR / ICCV** |
| **运动引导的文本提示学习** Motion-Guided Text Prompt Learning | 动态生成运动感知提示 | 中 | 2 A40 × 1.5 周 | **ECCV / NeurIPS** |
| **知识图谱增强的少样本动作识别** KG-Enhanced Few-Shot Action Recognition | 外部知识图谱 + 元学习 | 中高 | 需外部知识库 + 2 A40 × 2 周 | **CVPR / ACM MM** |
| **时序稀疏注意力 + 双流融合** Temporal Sparse Attention + Dual-Stream Fusion | 可学习关键帧选择 + 运动-静态融合 | 高 | 2 A40 × 3 周（需光流预处理） | **ICCV / CVPR** |
| **大模型辅助的开放词汇动作推理** LLM-Assisted Open-Vocabulary Action Reasoning | LLM生成描述 + 推理链 | 中 | 需 LLM API + 2 A40 × 1 周 | **NeurIPS / AAAI** |

**推荐优先级 Recommended Priority:**
1. **稀疏原型融合网络** (高创新性 + 可行性强)
2. **运动引导的文本提示学习** (轻量级 + 容易验证)
3. **时序稀疏注意力 + 双流融合** (扎实技术路线 + 充分消融)

---

## 5. 实验检查清单 (2周 / 1-2 A40) | Experiment Checklist (2 Weeks / 1-2 A40s)

### 5.1 数据集选择 | Dataset Selection
- **必选 Must-Have:**
  - **Kinetics-400/600** (标准基准)
  - **UCF-101** (少样本评估)
  - **HMDB-51** (小规模验证)
- **可选 Optional:**
  - **ActivityNet** (开放词汇评估)
  - **Something-Something V2** (时序敏感性测试)

### 5.2 实验配置 | Experimental Setup
```yaml
# 基础配置 Base Configuration
backbone: CLIP (ViT-B/16 or ViT-L/14)
batch_size: 64 (per GPU)
learning_rate: 1e-4 (prompt) / 1e-5 (full model)
optimizer: AdamW
weight_decay: 0.01
epochs: 50 (few-shot) / 100 (full)
frame_sampling: 8 or 16 frames (uniform or sparse)

# 稀疏融合配置 Sparse Fusion Configuration
num_bases: 4-8 (static, motion, scene, text-guided)
sparsity_lambda: 0.01-0.1 (L1 regularization)
prototype_per_class: 2-4
temporal_anchors: 3-5 key frames
```

### 5.3 消融实验 | Ablation Studies
1. **基函数数量的影响** (K = 2, 4, 8, 16)
2. **稀疏性约束强度** (λ = 0, 0.01, 0.05, 0.1)
3. **时序锚点数量** (T = 1, 3, 5, 全帧)
4. **运动特征类型** (光流 vs RGB差分 vs 3D卷积)
5. **文本提示策略** (手工设计 vs 可学习 vs LLM生成)

### 5.4 评估指标 | Evaluation Metrics
- **零样本 Zero-Shot:** Top-1 / Top-5 准确率
- **少样本 Few-Shot:** 1-shot / 5-shot / 10-shot 准确率
- **开放词汇 Open-Vocabulary:** Base / Novel / Harmonic Mean
- **效率 Efficiency:** FLOPs, 参数量, 推理速度 (FPS)
- **可解释性 Interpretability:** 基函数激活可视化, 时序注意力热图

### 5.5 时间估算 | Time Estimation
| 任务 Task | 时间 Time | GPU需求 GPU |
|----------|----------|------------|
| 数据预处理 Data Preprocessing | 2天 | CPU |
| 基线复现 Baseline Reproduction | 3天 | 1-2 A40 |
| 方法开发 Method Development | 4天 | 1-2 A40 |
| 消融实验 Ablation Studies | 4天 | 2 A40 |
| 可视化与分析 Visualization | 1天 | CPU |
| **总计 Total** | **14天** | **1-2 A40** |

---

## 6. 总结与展望 | Summary and Outlook

### 6.1 关键结论 | Key Conclusions
1. **静态偏差是核心挑战:** 现有方法虽有改进但仍未完全解决
2. **稀疏融合潜力巨大:** 异构线索的任务驱动稀疏选择是未来方向
3. **运动建模不可或缺:** 显式建模运动动态（如MoveNet、DiST）效果最佳
4. **少样本与开放词汇是热点:** 知识迁移和组合泛化是关键

### 6.2 未来研究建议 | Future Research Suggestions
- **技术层面 Technical:**
  - 更强的稀疏融合机制（可微分、可解释、高效）
  - 运动-语义联合表征学习
  - 大模型辅助的动作推理

- **应用层面 Application:**
  - 长视频理解（电影、监控）
  - 多模态融合（音频 + 视频 + 文本）
  - 实时动作识别系统

- **理论层面 Theoretical:**
  - 静态偏差的数学建模
  - 稀疏融合的泛化理论
  - 零样本动作识别的可学习性分析

---

## 参考文献 | References

1. **GBC** - Graph-Based Captioning, IEEE TCSVT 2024, DOI: 10.1109/tcsvt.2024.3390133
2. **EPK-CLIP** - Expert Systems with Applications 2024, DOI: 10.1016/j.eswa.2024.124183
3. **SC-CLIP** - Semantic Composition for Zero-Shot Action Recognition, arXiv 2024
4. **VEDA** - Vision-Language Enhancement Network, arXiv 2024
5. **DiST** - Spatio-temporal Decoupled Knowledge Compensator, arXiv 2024
6. **SceneVLP** - Scene-Aware Vision-Language Pre-training, arXiv 2024
7. **MoveNet** - Motion-Aware Visual-Language Representation, arXiv 2024
8. **CoOp/CoCoOp** - IJCV 2022 / CVPR 2022
9. **CLIP** - Learning Transferable Visual Models, ICML 2021

---

**文档版本 Document Version:** 1.0  
**更新日期 Last Updated:** 2026-10-29  
**维护者 Maintainer:** Paper Database Contributors
