from transformers import BertForSequenceClassification, BertTokenizer
import torch


class PersonalityDetector():
    def __init__(self, model_path: str = "E:\Project\TuringPersona\Model\Bert_personality", num_labels: int = 5, do_lower_case: bool = True):
        self.model = BertForSequenceClassification.from_pretrained(model_path, num_labels=num_labels)
        self.tokenizer = BertTokenizer.from_pretrained(model_path, do_lower_case=do_lower_case)
        self._configure_labels()

    def _configure_labels(self):
        self.model.config.label2id = {
            "Extroversion": 0,
            "Neuroticism": 1,
            "Agreeableness": 2,
            "Conscientiousness": 3,
            "Openness": 4,
        }
        self.model.config.id2label = {
            "0": "Extroversion",
            "1": "Neuroticism",
            "2": "Agreeableness",
            "3": "Conscientiousness",
            "4": "Openness",
        }

    def personality_detection(self, model_input: str) -> dict:
        if len(model_input) == 0:
            return {
                "Extroversion": float(0),
                "Neuroticism": float(0),
                "Agreeableness": float(0),
                "Conscientiousness": float(0),
                "Openness": float(0),
            }
        dict_custom = {}

        preprocess_part1 = model_input[:len(model_input)]
        dict1 = self.tokenizer.encode_plus(
            preprocess_part1,
            max_length=1024,
            padding=True,
            truncation=True
        )
        dict_custom['input_ids'] = [dict1['input_ids'], dict1['input_ids']]
        dict_custom['token_type_ids'] = [dict1['token_type_ids'], dict1['token_type_ids']]
        dict_custom['attention_mask'] = [dict1['attention_mask'], dict1['attention_mask']]

        self.model.eval()
        with torch.no_grad():
            outs = self.model(
                torch.tensor(dict_custom['input_ids']),
                token_type_ids=None,
                attention_mask=torch.tensor(dict_custom['attention_mask'])
            )

        b_logit_pred = outs[0]
        pred_label = torch.sigmoid(b_logit_pred)
        return {
            "Extroversion": float(pred_label[0][0]),  # 外向性概率
            "Neuroticism": float(pred_label[0][1]),  # 神经质概率
            "Agreeableness": float(pred_label[0][2]),  # 亲和性概率
            "Conscientiousness": float(pred_label[0][3]),  # 尽责性概率
            "Openness": float(pred_label[0][4]),  # 开放性概率
        }

