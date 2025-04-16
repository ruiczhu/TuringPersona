# Related Work

## 现有的对话类数据集

| DataSet         | Type | PersenalityTag     | Dialogues | Domain           | Source           | Language        | Availability | Link                                                                              |
|-----------------|------|--------------------|-----------|------------------|------------------|-----------------|--------------|-----------------------------------------------------------------------------------|
| Persena-chat    | HHD  | None               | 10,907    | general domain   | Real             | English         | Yes          | [Link](https://github.com/facebookresearch/ParlAI/tree/main/projects/personachat) |
| MultiWOZ        | HHD  | None               | 113,556   | Task Orientation | Real             | English         | Yes          | [Link](https://github.com/budzianowski/multiwoz)                                  |
| DailyDialog     | HHD  | None(emotions)     | 13,118    | general domain   | Real(socalmedia) | English         | Yes          | [Link](https://hf-mirror.com/datasets/ConvLab/dailydialog)                        |
| CPED            | HHD  | Big Five           | 12,000    | general domain   | Real(tvshows)    | Chinese         | Yes          | [Link](https://github.com/scutcyr/CPED)                                           |
| PSYDIAL         | HHD  | Big Five           | 2,932     | general domain   | LLM-generation   | Korean          | Yes          | [Link](https://github.com/jiSilverH/psydial)                                      |
| PersonalityEvd  | HHD  | Big Five           | 1,924     | general domain   | Real+LLMtagging  | Chinese         | Yes          | [Link](https://github.com/Lei-Sun-RUC/PersonalityEvd)                             |
| FriendsPersona  | HHD  | Big Five           | 711       | general domain   | Real(tvshows)    | English         | Yes          | [Link](https://github.com/emorynlp/personality-detection)                         |
| CharacterLLM    | HCD  | None               | 118,800   | role-specific    | LLM-generation   | Chinese         | Yes          | [Link](https://huggingface.co/datasets/fnlp/character-llm-data)                   |
| LLM-Roleplaying | HCD  | None(role-based)   | N/A       | role-specific    | LLM-generation   | English&Chinese | N/A          | [Link](https://github.com/Neph0s/awesome-llm-role-playing-with-persona)           |
| HundredCV-Chat  | HCD  | None(topic_based)  | 24,750    | general domain   | LLM-generation   | Chinese         | Yes          | [Link](https://huggingface.co/datasets/Jax-dan/HundredCV-Chat)                    |
| SGD             | HCD  | None(intent_based) | 16,142    | general domain   | Real             | English         | Yes          | [Link](https://github.com/google-research-datasets/dstc8-schema-guided-dialogue)  |
| PersenalLLM     | HCD  | Big Five           | N/A       | general domain   | LLM-generation   | English         | No           | [Link](https://github.com/hjian42/PersonaLLM)                                     |
| LMSYS-CHAT-1M   | HCD  | None               | 1,000,000 | general domain   | Real             | Multiple        | Yes          | [Link](https://huggingface.co/datasets/lmsys/lmsys-chat-1m)                       |
| LUCID           | HCD  | None               | 4,276     | general domain   | LLM-generation   | English         | Yes          | [Link](https://github.com/apple/ml-lucid-datagen)                                 |

### 人格标注对话数据集现状

**文献搜索关键词**：

- personality-annotated dialogue datasets
- personality-labeled conversation corpus
- personality traits in dialogue data
- Big Five personality in dialogue corpus
- MBTI dialogue dataset

**重点关注内容**：

- 现有数据集的规模、来源和质量
- 标注方式和标注精度
- 数据集中人格特征的多样性和分布
- 数据集的局限性（如非自然对话、过度刻板化等）

现有的人格标注对话数据集主要可分为三类：基于真人交互的自然对话数据集、基于虚构内容（如电视剧、电影）的对话数据集，以及近期基于大语言模型生成的合成对话数据集。这些数据集在人格标注的精确度、对话自然度以及场景真实性方面存在显著差异。其中，Jiang等人[**18**]的Friends Persona和Chen等人[**19**]的CPED等基于电视剧的数据集虽然包含丰富的性格特征，但对话风格常常夸张化；而如Zhang等人[**9**]的PersonaChat等数据集虽然专为对话系统设计，但缺乏精细的人格标注。近期的如Shao等人[**14**]提出的Character-LLM虽然规模可观，但由于LLM生成过程中的不确定性，其中人格表达的准确性和一致性仍存在挑战，这与Huang等人[**17**]指出的大语言模型幻觉问题密切相关。此外，Dinan等人[**36**]的Wizard of Wikipedia和Li等人[**37**]的DailyDialog等虽是高质量的多回合对话数据集，但缺乏人格标注，这正是我们研究需要填补的空白。同时，Rashkin等人[**47**]提出的共情对话数据集为情感表达研究提供了重要参考。

### 人格感知AI系统研究进展

**文献搜索关键词**：

- personality-aware AI systems
- personality detection in dialogue
- personality recognition algorithms
- personality-based user modeling
- personality-adaptive conversational agents

**重点关注内容**：

- 当前人格感知模型的方法论
- 人格特征识别的准确率和挑战
- 基于人格特征的对话生成技术
- 系统评估方法和性能指标

人格感知AI系统的研究可追溯至Vinciarelli和Mohammadi[**20**]早期的性格计算研究，发展至今主要分为两个方向：基于规则的方法和基于数据驱动的方法。基于规则的方法通常依赖心理学理论构建特定语言特征与人格特质的映射关系，如Mairesse等人[**21**]的语言线索识别研究；而基于数据驱动的方法则使用机器学习技术从大规模语言数据中学习人格特征，如Liu等人[**22**]提出的语言独立和组合模型。近年来，随着大型语言模型的发展，Guo等人[**8**]提出的基于预训练模型的人格特征识别和生成方法显示出显著优势，但系统在图灵测试场景的表现仍存在明显差距，特别是在识别微妙人格差异和生成自然且符合特定人格特质的对话内容方面。这一领域，Han等人[**23**]最近提出的PSYDIAL框架通过使用大语言模型生成基于心理学的合成对话，为解决人格一致性问题提供了新思路。Jiang等人[**16**]的PersonaLLM研究也探索了大型语言模型表达人格特质的能力，为这一领域提供了重要实证支持。

### 图灵测试场景下的人机交互研究

**文献搜索关键词**：

- Turing test scenario interactions
- human-AI conversation without disclosure
- blind human-machine interaction
- deception in human-AI interaction
- user behavior in Turing test

**重点关注内容**：

- 用户在不知道对话对象身份时的行为模式
- 图灵测试场景与明确身份场景的交互差异
- 用户对AI身份的察觉线索和影响因素
- 图灵测试场景下的伦理考量

研究表明，当用户知道其交互对象是AI系统时，会调整其沟通行为[**10**],[**11**]，包括简化语言结构、减少礼貌用语和情感表达、增加指令式交流等。与此相反，在图灵测试场景下，用户表现出更接近人际交流的自然行为模式。Mou & Xu[**11**]的研究表明，在图灵测试场景下，人类与AI的初始交互质量与人类间交互更为相似。Go与Sundar[**12**]进一步研究了视觉、身份和会话线索对用户感知人性化程度的影响，这对于理解图灵测试场景下的交互尤为重要。尽管如此，关于图灵测试场景下人格特征自然呈现的专门研究仍然有限，特别是缺乏对特定人格特质在此场景下如何影响语言表达和交互策略的深入分析。这方面的研究缺口为我们的工作提供了重要机会。

### 人格特征转换与增强技术

**文献搜索关键词**：

- personality transfer in text
- personality style transformation
- controllable personality generation
- character style adaptation
- personality-specific language generation

**重点关注内容**：

- 文本人格风格转换的技术路线
- 语义保留与人格特征注入的平衡策略
- 特定人格特质的语言学标记
- 人格特征转换的自然度和可控性评估

在人格特征转换技术方面，现有方法主要依赖于风格迁移和控制文本生成技术。传统方法如Li等人[**24**]提出的删除-检索-生成模式能够实现特定人格的简单模拟，但缺乏灵活性和深度理解。近期基于深度学习的方法如John等人[**25**]提出的条件变分自编码器和Keskar等人[**26**]的基于Transformer的CTRL模型能够在保持原始语义的同时注入特定人格特征，但仍面临转换后文本不自然、人格特征过度刻板化等问题。最新的研究通过引入Fu等人[**27**]提出的多任务学习和Christian等人[**28**]的对比学习等技术，在提高转换自然度和准确性方面取得了进展，但在图灵测试场景下的有效性尚未得到充分验证。

### 多维度人格标注体系

**文献搜索关键词**：

- multi-dimensional personality annotation
- personality trait measurement in dialogue
- linguistic markers of personality
- personality taxonomy for NLP
- dialogue-based personality assessment

**重点关注内容**：

- 现有心理学人格理论在NLP中的应用
- 对话中人格特征的标注粒度和层次
- 标注一致性和可靠性的评估方法
- 适合对话分析的人格特征操作化定义

人格标注体系研究主要基于心理学领域的主要人格理论，包括大五人格模型[**29**]、MBTI[**30**]和HEXACO[**31**]等。在NLP领域，大五人格因其在心理测量学上的稳健性成为最常用的框架[**32**]。然而，现有标注体系存在两个主要局限：一方面，标注通常仅限于特质水平，缺乏更细粒度的行为指标层面的标注；另一方面，标注往往依赖自我报告问卷或整体评估，而非直接从对话内容中提取。近期研究开始探索将语言学标记与具体人格特质关联的精细标注方法[**33**]，以及利用对话中的特定交互模式推断人格特质的动态评估框架[**34**]，但尚未形成统一且广泛适用的标注体系。

通过上述文献综述，我们可以看到虽然人格感知AI领域已有广泛研究，但针对图灵测试场景下的人格标注对话数据集构建仍存在明显研究空白。现有数据集要么缺乏精确人格标注，要么缺乏自然对话特性，特别是缺乏在用户不知情条件下的真实人机交互数据。本研究旨在填补这一空白，通过创新性的数据收集和标注方法，构建一个兼具人格精确标注和对话自然度的高质量数据集，为人格感知AI系统研究提供重要资源。