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


if __name__ == "__main__":
    evaluator = ComprehensiveEvaluator()
    results = evaluator.run_all_evaluators()
    if results:
        print(f"{results['personality_results'].shape}")
        print(f"{results['similarity_results'].shape}")
        print(f"{results['naturalness_results'].shape}")
