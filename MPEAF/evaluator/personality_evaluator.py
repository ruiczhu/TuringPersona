import os
import pandas as pd
import ast
import numpy as np
from bert_personality import PersonalityDetector


class PersonalityEvaluator:
    def __init__(self, model_path="E:\\Project\\TuringPersona\\Model\\Bert_personality"):
        # 初始化 PersonalityDetector 模型，现在就这个是本地的
        self.personality_detector = PersonalityDetector(model_path=model_path)
        self.data = None
        self.grouped_dialogues = None

    def load_data(self, file_path):
        self.data = pd.read_csv(file_path)
        self._group_data()

    def load_specific_data(self, file_path="sgd_dialogues_train_1744818072.csv"):
        # 加载特定数据集
        pre_path = "../dataset/transformed_data/" + file_path
        self.data = pd.read_csv(pre_path)
        self._group_data()

    def _group_data(self):
        # 同相似度，分组加平均值
        self.grouped_dialogues = self.data.groupby(['conversation_id', 'profile_id']).apply(
            lambda x: x.sort_values(['turn', 'position']),
            include_groups=False
        ).reset_index()

    def _parse_ocean_list(self, ocean_str):
        # 读取的列表是字符串的，解析
        try:
            return ast.literal_eval(ocean_str)
        except (ValueError, SyntaxError):
            return []

    def _compute_ocean_averages(self, group):
        # 计算OCEAN五个维度的平均值
        ocean_values = {
            'O': [],
            'C': [],
            'E': [],
            'A': [],
            'N': []
        }
        # 遍历组内的每一行，解析OCEAN值
        for _, row in group.iterrows():
            for dim in ocean_values.keys():
                values = self._parse_ocean_list(row[dim])
                if values:
                    ocean_values[dim].extend(values)
        # 计算每个维度的平均值
        averages = {}
        for dim, values in ocean_values.items():
            averages[dim] = np.mean(values) if values else 0.0
        return averages

    def _compute_personality_scores(self, text):
        # 使用PersonalityDetector预测人格分数
        return self.personality_detector.personality_detection(text)

    def _compute_absolute_difference(self, predicted, actual):
        # 计算绝对差值，这里后续想办法咋搞吧。
        # 因为指标不一样，计算百分比的话无论以哪个作为分母效果都很差劲
        #
        return abs(predicted - actual)

    def evaluate_and_compare(self):
        # 评估人格并与OCEAN平均值对比
        if self.data is None or self.grouped_dialogues is None:
            raise ValueError("Data not loaded. Please load data first.")

        results = []

        # 分组
        for (conv_id, prof_id), group in self.grouped_dialogues.groupby(['conversation_id', 'profile_id']):
            # 合并为长文本，同相似度
            combined_content = " ".join(group['content'].astype(str))
            combined_original_content = " ".join(group['original_content'].astype(str))
            combined_text = combined_content + " " + combined_original_content

            # 计算数据中的各个列的OCEAN平均值
            ocean_averages = self._compute_ocean_averages(group)

            # 使用模型预测人格分数
            predicted_scores = self._compute_personality_scores(combined_text)

            # 计算绝对差值
            absolute_diffs = {
                'Extroversion_diff': self._compute_absolute_difference(predicted_scores['Extroversion'],
                                                                       ocean_averages['E']),
                'Neuroticism_diff': self._compute_absolute_difference(predicted_scores['Neuroticism'],
                                                                      ocean_averages['N']),
                'Agreeableness_diff': self._compute_absolute_difference(predicted_scores['Agreeableness'],
                                                                        ocean_averages['A']),
                'Conscientiousness_diff': self._compute_absolute_difference(predicted_scores['Conscientiousness'],
                                                                            ocean_averages['C']),
                'Openness_diff': self._compute_absolute_difference(predicted_scores['Openness'], ocean_averages['O'])
            }

            # 收集结果
            results.append({
                'conversation_id': conv_id,
                'profile_id': prof_id,
                'combined_content': combined_content,
                'combined_original_content': combined_original_content,
                # OCEAN平均值
                'avg_Openness': ocean_averages['O'],
                'avg_Conscientiousness': ocean_averages['C'],
                'avg_Extroversion': ocean_averages['E'],
                'avg_Agreeableness': ocean_averages['A'],
                'avg_Neuroticism': ocean_averages['N'],
                # 模型预测值
                'pred_Extroversion': predicted_scores['Extroversion'],
                'pred_Neuroticism': predicted_scores['Neuroticism'],
                'pred_Agreeableness': predicted_scores['Agreeableness'],
                'pred_Conscientiousness': predicted_scores['Conscientiousness'],
                'pred_Openness': predicted_scores['Openness'],
                # 绝对差值
                'Extroversion_absolute_diff': absolute_diffs['Extroversion_diff'],
                'Neuroticism_absolute_diff': absolute_diffs['Neuroticism_diff'],
                'Agreeableness_absolute_diff': absolute_diffs['Agreeableness_diff'],
                'Conscientiousness_absolute_diff': absolute_diffs['Conscientiousness_diff'],
                'Openness_absolute_diff': absolute_diffs['Openness_diff']
            })

        return pd.DataFrame(results)


# if __name__ == "__main__":
#     evaluator = PersonalityEvaluator()
#     evaluator.load_specific_data()
#     comparison_results = evaluator.evaluate_and_compare()
#     output_file = "../results/personality_results.csv"
#     comparison_results.to_csv(output_file, index=False)
#     print(f"Results saved to {output_file}")
#     print(comparison_results)
