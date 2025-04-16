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