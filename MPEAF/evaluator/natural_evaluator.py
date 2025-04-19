import os
import pandas as pd
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.util import ngrams
import numpy as np
from sentence_transformers import SentenceTransformer, util
import torch
from transformers import GPT2LMHeadModel, GPT2Tokenizer
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer


class NaturalnessEvaluator:
    def __init__(self):
        self.data = None
        self.grouped_dialogues = None
        # 初始化 Sentence-BERT 模型用于连贯性
        self.sbert_model = SentenceTransformer('all-MiniLM-L6-v2')
        # 初始化 GPT-2 模型和分词器用于计算 perplexity
        self.gpt2_tokenizer = GPT2Tokenizer.from_pretrained('gpt2')
        self.gpt2_model = GPT2LMHeadModel.from_pretrained('gpt2')
        self.gpt2_model.eval()
        # 初始化 VADER 情感分析器
        self.sentiment_analyzer = SentimentIntensityAnalyzer()

    def load_data(self, file_path):
        self.data = pd.read_csv(file_path)
        self._group_data()

    def load_specific_data(self, file_path="sgd_dialogues_train_1744818072.csv"):
        pre_path = "../dataset/transformed_data/" + file_path
        self.data = pd.read_csv(pre_path)
        self._group_data()

    def _group_data(self):
        self.grouped_dialogues = self.data.groupby(['conversation_id', 'profile_id']).apply(
            lambda x: x.sort_values(['turn', 'position']),
            include_groups=False
        ).reset_index()

    def _preprocess_text(self, text):
        if not isinstance(text, str):
            return []
        return word_tokenize(text.lower())

    def compute_perplexity(self, text):
        # 计算文本的 perplexity
        if not isinstance(text, str) or len(text.strip()) == 0:
            return float('inf')  # 如果文本为空，返回无穷大

        # 编码文本
        encodings = self.gpt2_tokenizer(text, return_tensors='pt', truncation=True, max_length=1024)
        input_ids = encodings['input_ids']
        attention_mask = encodings['attention_mask']

        # 计算交叉熵损失
        with torch.no_grad():
            outputs = self.gpt2_model(input_ids, attention_mask=attention_mask, labels=input_ids)
            loss = outputs.loss

        # 通过 exp(loss) 计算 perplexity
        return torch.exp(loss).item()

    def compute_coherence(self, text):
        # 计算连贯性：基于句间语义相似度的平均值
        if not isinstance(text, str) or len(text.strip()) == 0:
            return 0.0  # 如果文本为空，返回 0

        # 按句子分割
        sentences = sent_tokenize(text)
        if len(sentences) < 2:
            return 0.0  # 如果少于 2 句话，无法计算句间相似度

        # 使用 Sentence-BERT 编码句子
        embeddings = self.sbert_model.encode(sentences, convert_to_tensor=True)

        # 计算相邻句子之间的余弦相似度
        similarities = []
        for i in range(len(embeddings) - 1):
            sim = util.cos_sim(embeddings[i], embeddings[i + 1]).item()
            similarities.append(sim)

        # 返回平均相似度作为连贯性
        return np.mean(similarities) if similarities else 0.0

    def compute_diversity(self, text, n=2):
        # 计算多样性：基于唯一 N-gram 的比例
        tokens = self._preprocess_text(text)
        if len(tokens) < n:
            return 0.0
        n_grams = list(ngrams(tokens, n))
        unique_n_grams = len(set(n_grams))
        total_n_grams = len(n_grams)
        return unique_n_grams / total_n_grams if total_n_grams > 0 else 0.0

    def compute_sentiment_shift(self, text1, text2):
        # 计算情感偏移
        if not isinstance(text1, str) or not isinstance(text2, str):
            return 0.0
        score1 = self.sentiment_analyzer.polarity_scores(text1)['compound']
        score2 = self.sentiment_analyzer.polarity_scores(text2)['compound']
        return abs(score1 - score2)

    def evaluate_naturalness(self):
        # 评估对话的自然度指标
        if self.data is None or self.grouped_dialogues is None:
            raise ValueError("Data not loaded. Please load data first.")

        results = []

        # 按 conversation_id 和 profile_id 分组
        for (conv_id, prof_id), group in self.grouped_dialogues.groupby(['conversation_id', 'profile_id']):
            # 合并 content 和 original_content
            combined_content = " ".join(group['content'].astype(str))
            combined_original_content = " ".join(group['original_content'].astype(str))

            # 计算 perplexity
            content_perplexity = self.compute_perplexity(combined_content)
            original_content_perplexity = self.compute_perplexity(combined_original_content)

            # 计算 coherence
            content_coherence = self.compute_coherence(combined_content)
            original_content_coherence = self.compute_coherence(combined_original_content)

            # 计算 diversity
            content_diversity = self.compute_diversity(combined_content)
            original_content_diversity = self.compute_diversity(combined_original_content)

            # 计算 sentiment shift
            sentiment_shift = self.compute_sentiment_shift(combined_content, combined_original_content)

            # 收集结果
            results.append({
                'conversation_id': conv_id,
                'profile_id': prof_id,
                'combined_content': combined_content,
                'combined_original_content': combined_original_content,
                'content_perplexity': content_perplexity,
                'original_content_perplexity': original_content_perplexity,
                'content_coherence': content_coherence,
                'original_content_coherence': original_content_coherence,
                'content_diversity': content_diversity,
                'original_content_diversity': original_content_diversity,
                'sentiment_shift': sentiment_shift
            })

        return pd.DataFrame(results)


# if __name__ == "__main__":
#     print(f"Current working directory: {os.getcwd()}")
#     evaluator = NaturalnessEvaluator()
#     evaluator.load_specific_data()
#     naturalness_results = evaluator.evaluate_naturalness()
#     output_file = "../results/naturalness_results.csv"
#     naturalness_results.to_csv(output_file, index=False)
#     print(f"Results saved to {output_file}")
#     print(naturalness_results)
