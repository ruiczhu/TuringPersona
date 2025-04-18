from MPEAF.evaluator.natural_evaluator import NaturalnessEvaluator
from MPEAF.evaluator.personality_evaluator import PersonalityEvaluator
from MPEAF.evaluator.semantic_evaluator import DialogueSimilarityEvaluator
import pandas as pd
import os
import nltk
import warnings

warnings.filterwarnings("ignore")
nltk.download('punkt')
nltk.download('punkt_tab')


class ComprehensiveEvaluator:
    def __init__(self):
        self.input_path = "../dataset/transformed_data/"
        self.output_path = ""
        self.p_eval = PersonalityEvaluator()
        self.s_eval = DialogueSimilarityEvaluator()
        self.n_eval = NaturalnessEvaluator()

    def set_input_file(self, filename="sgd_dialogues_train_1744818072.csv"):
        self.input_path = os.path.join(self.input_path, filename)

    def run_all_evaluators(self, filename="sgd_dialogues_train_1744818072.csv"):
        # 最后返回的是str：df的词典
        self.set_input_file(filename)

        try:
            self.p_eval.load_specific_data(filename)
            self.s_eval.load_specific_data(filename)
            self.n_eval.load_specific_data(filename)
        except FileNotFoundError:
            print(f"Error: Input file {self.input_path} not found.")
            return None

        # Run evaluations
        print("Running Personality Evaluator...")
        personality_results = self.p_eval.evaluate_and_compare()
        output_file = "../dataset/results/personality_results.csv"
        personality_results.to_csv(output_file, index=False)
        print("Running Dialogue Similarity Evaluator...")
        similarity_results = self.s_eval.analyze_dialogue_similarity()
        output_file = "../dataset/results/similarity_results.csv"
        similarity_results.to_csv(output_file, index=False)
        print("Running Naturalness Evaluator...")
        naturalness_results = self.n_eval.evaluate_naturalness()
        output_file = "../dataset/results/naturalness_results.csv"
        naturalness_results.to_csv(output_file, index=False)

        return {
            'personality_results': personality_results,
            'similarity_results': similarity_results,
            'naturalness_results': naturalness_results
        }

    def print_comprehensive_results(self, filename="sgd_dialogues_train_1744818072.csv"):
        # 打印以conversation_id和profile_id为主键的综合结果
        # 仅包含指标列（不包括对话内容）
        results = self.run_all_evaluators(filename)
        if not results:
            print("Failed to generate results.")
            return None

        # Extract results
        personality_results = results['personality_results']
        similarity_results = results['similarity_results']
        naturalness_results = results['naturalness_results']

        # Select only metric columns (exclude combined_content and combined_original_content)
        select_p = personality_results[['conversation_id', 'profile_id',
                                        'Extroversion_absolute_diff', 'Neuroticism_absolute_diff',
                                        'Agreeableness_absolute_diff', 'Conscientiousness_absolute_diff',
                                        'Openness_absolute_diff']]
        select_s = similarity_results[['conversation_id', 'profile_id',
                                       'tfidf_cosine_similarity', 'sbert_similarity',
                                       'jaccard_similarity', 'edit_distance', 'bleu_score']]
        select_n = naturalness_results[['conversation_id', 'profile_id',
                                        'content_perplexity', 'original_content_perplexity',
                                        'content_coherence', 'original_content_coherence',
                                        'content_diversity', 'original_content_diversity',
                                        'sentiment_shift']]
        comprehensive_df = pd.merge(
            pd.merge(select_p, select_s, on=['conversation_id', 'profile_id'], how='inner'),
            select_n, on=['conversation_id', 'profile_id'], how='inner'
        )
        output_file = "../dataset/results/comprehensive_metrics.csv"
        comprehensive_df.to_csv(output_file, index=False)
        print(f"\nResults saved to {output_file}")
        return comprehensive_df


# if __name__ == "__main__":
#     evaluator = ComprehensiveEvaluator()
#     evaluator.print_comprehensive_results()
