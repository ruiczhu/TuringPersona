
import pandas as pd
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.metrics.distance import jaccard_distance, edit_distance
from nltk.translate.bleu_score import sentence_bleu
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer, util


class DialogueSimilarityEvaluator:
    def __init__(self):
        self.data = None
        self.grouped_dialogues = None
        # sklearn的TF-IDF
        self.tfidf_vectorizer = TfidfVectorizer()
        # Sentence-BERT模型，这个不用大的那个，针对于语句级别的，大的文档级的效果不好
        self.sbert_model = SentenceTransformer('all-MiniLM-L6-v2')

    def load_data(self, file_path):
        # 读CSV
        self.data = pd.read_csv(file_path)
        self._group_data()

    def load_specific_data(self, file_path="sgd_dialogues_train_1744818072.csv"):
        # 固定的加载路径，传参传文件名就行
        pre_path = "../dataset/transformed_data/" + file_path
        self.data = pd.read_csv(pre_path)
        self._group_data()

    def _group_data(self):
        # 按conversation_id和profile_id分组
        self.grouped_dialogues = self.data.groupby(['conversation_id', 'profile_id']).apply(
            # 并按 turn 和 position 排序
            lambda x: x.sort_values(['turn', 'position']),
            include_groups=False
        ).reset_index()

    def _preprocess_text(self, text):
        # 先转换成小写，再分词
        if not isinstance(text, str):
            return []
        return word_tokenize(text.lower())

    def compute_tfidf_cosine_similarity(self, text1, text2):
        # TfidfVectorizer计算余弦相似度
        # nltk原生的效果差劲，好几次结果为0，先用这个吧
        if not isinstance(text1, str) or not isinstance(text2, str):
            return 0.0
        # 将文本转换为TF-IDF向量
        tfidf_matrix = self.tfidf_vectorizer.fit_transform([text1, text2])
        # 计算余弦相似度
        sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        return sim

    def compute_sbert_similarity(self, text1, text2):
        # Sentence-BERT计算语义相似度
        if not isinstance(text1, str) or not isinstance(text2, str):
            return 0.0
        # 生成句子的嵌入向量
        embedding1 = self.sbert_model.encode(text1, convert_to_tensor=True)
        embedding2 = self.sbert_model.encode(text2, convert_to_tensor=True)
        # 计算余弦相似度
        sim = util.cos_sim(embedding1, embedding2).item()
        return sim

    def compute_jaccard_similarity(self, text1, text2):
        # 计算Jaccard相似度
        set1 = set(self._preprocess_text(text1))
        set2 = set(self._preprocess_text(text2))
        if not set1 or not set2:
            return 0.0
        distance = jaccard_distance(set1, set2)
        return 1.0 - distance

    def compute_edit_distance(self, text1, text2):
        # 计算编辑距离（直接使用原始字符串）
        # 参考意义感觉没想象的高，不好评判，后续可以删除
        if not isinstance(text1, str) or not isinstance(text2, str):
            return float('inf')
        return edit_distance(text1, text2)

    def compute_bleu_score(self, text1, text2):
        # 计算BLEU分数
        tokens1 = self._preprocess_text(text1)
        tokens2 = self._preprocess_text(text2)
        if not tokens1 or not tokens2:
            return 0.0
        reference = [tokens1]
        candidate = tokens2
        return sentence_bleu(reference, candidate, weights=(0.25, 0.25, 0.25, 0.25))

    def compute_semantic_naturalness(self, text):
        print("先不用这个！")
        # 计算语义自然度：基于句间语义相似度的平均值
        # 这个语义自然度需要编码句子，也就是个列表，针对的句子级别的
        # 先聚合了文本然后再分割计算，不太靠谱，后期可以去掉。
        # if not isinstance(text, str) or len(text.strip()) == 0:
        #     return 0.0  # 如果文本为空，返回 0
        # # 分割句子
        # sentences = sent_tokenize(text)
        # if len(sentences) < 2:
        #     return 0.0  # 如果少于2句话，无法计算句间相似度
        # # 编码句子
        # embeddings = self.sbert_model.encode(sentences, convert_to_tensor=True)
        # # 计算相邻句子之间的余弦相似度
        # similarities = []
        # for i in range(len(embeddings) - 1):
        #     sim = util.cos_sim(embeddings[i], embeddings[i + 1]).item()
        #     similarities.append(sim)
        # # 返回平均相似度作为语义自然度
        # return np.mean(similarities) if similarities else 0.0

    def analyze_dialogue_similarity(self):
        # 分析每轮对话的content和original_content的相似度
        # 单独对应轮次每句话对应的话结果很差尤其是bleu，句子太短，合并为长文本计算
        if self.data is None or self.grouped_dialogues is None:
            raise ValueError("Data not loaded. Please load data first.")

        results = []

        # 按conversation_id和profile_id分组
        for (conv_id, prof_id), group in self.grouped_dialogues.groupby(['conversation_id', 'profile_id']):
            # 按 turn 和 position 排序后合并 content 和 original_content
            group = group.sort_values(['turn', 'position'])
            combined_content = " ".join(group['content'].astype(str))
            combined_original_content = " ".join(group['original_content'].astype(str))

            # 计算合并后的长文本的相似度指标
            tfidf_cosine_sim = self.compute_tfidf_cosine_similarity(combined_content, combined_original_content)
            sbert_sim = self.compute_sbert_similarity(combined_content, combined_original_content)
            jaccard_sim = self.compute_jaccard_similarity(combined_content, combined_original_content)
            edit_dist = self.compute_edit_distance(combined_content, combined_original_content)
            bleu_score = self.compute_bleu_score(combined_content, combined_original_content)

            # 计算语义自然度（感觉不太靠谱，看函数）
            # content_semantic_naturalness = self.compute_semantic_naturalness(combined_content)
            # original_content_semantic_naturalness = self.compute_semantic_naturalness(combined_original_content)

            results.append({
                'conversation_id': conv_id,
                'profile_id': prof_id,
                'combined_content': combined_content,
                'combined_original_content': combined_original_content,
                'tfidf_cosine_similarity': tfidf_cosine_sim,
                'sbert_similarity': sbert_sim,
                'jaccard_similarity': jaccard_sim,
                'edit_distance': edit_dist,
                'bleu_score': bleu_score,
                # 'content_semantic_naturalness': content_semantic_naturalness,
                # 'original_content_semantic_naturalness': original_content_semantic_naturalness
            })
        # 保存操作都放在最上级的class里吧
        return pd.DataFrame(results)


# if __name__ == "__main__":
#     analyzer = DialogueSimilarityEvaluator()
#     analyzer.load_specific_data()
#     similarity_results = analyzer.analyze_dialogue_similarity()
#     output_file = "../results/similarity_results.csv"
#     similarity_results.to_csv(output_file, index=False)
#     print(f"Results saved to {output_file}")
#     print(similarity_results)
