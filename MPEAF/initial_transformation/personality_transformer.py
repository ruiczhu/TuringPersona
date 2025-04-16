import requests
import json
import time
import random

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from MPEAF.framework.personality_framework import PersonalityFramework


class PersonalityTransformer:
    def __init__(self, api_key):
        """Initialize personality transformer"""
        self.api_key = api_key
        self.headers = {
            "Content-Type": "application/json",
            "api-key": api_key,
        }
        self.endpoint = "https://genai-jp.openai.azure.com/openai/deployments/ln-gpt40/chat/completions?api-version=2024-02-15-preview"
        # self.endpoint = "https://genai-jp.openai.azure.com/openai/deployments/ln-gpt35-turbo/chat/completions?api-version=2023-03-15-preview"
        self.personality_framework = PersonalityFramework()
        
    def generate_response(self, messages, temperature=0.7, max_tokens=800):
        """Call LLM API to generate response"""
        payload = {
            "messages": messages,
            "temperature": temperature,
            "top_p": 0.95,
            "max_tokens": max_tokens
        }
        
        try:
            # 添加重试机制
            max_retries = 1
            retry_count = 0
            
            while retry_count < max_retries:
                try:
                    response = requests.post(self.endpoint, headers=self.headers, json=payload)
                    response.raise_for_status()
                    return response.json()['choices'][0]['message']['content']
                except requests.RequestException as e:
                    print(f"API request error: {e}")
                    print(f"Retry {retry_count + 1}/{max_retries}...")
                    retry_count += 1
                    time.sleep(2 + retry_count)  # 指数退避
            
            print("All retries failed.")
            return None
        except (KeyError, json.JSONDecodeError) as e:
            print(f"Response parsing error: {e}")
            return None
            
    def create_personality_prompt(self, target_trait_profile):
        """Create prompt template for complete personality profile transformation
        
        Args:
            target_trait_profile (dict): Dictionary containing O,C,E,A,N dimension scores 
                                        and their sub-traits scores
        """
        traits = self.personality_framework.get_all_traits_with_markers()
        
        # 构建人格特质描述
        trait_descriptions = []
        
        # 为每个维度生成描述
        for dimension in ["O", "C", "E", "A", "N"]:
            dim_name = self.personality_framework.big_five_dimensions[dimension]
            dim_score = target_trait_profile.get(dimension, 0.5)
            trait_descriptions.append(f"- {dim_name} ({dimension}): {dim_score:.2f}/1.0")
            
            # 添加子特质描述
            sub_traits = [t for t in traits.keys() if t.startswith(dimension)]
            for sub_trait in sub_traits:
                sub_score = target_trait_profile.get(sub_trait, 0.5)
                sub_name = traits[sub_trait]['name']
                sub_markers = traits[sub_trait]['markers']
                marker_text = "; ".join(sub_markers[:2])  # 限制标记数量，避免提示词过长
                trait_descriptions.append(f"  - {sub_trait} ({sub_name}): {sub_score:.2f}/1.0 - {marker_text}")
        
        # 英文提示模板
        prompt = f"""You are a professional dialogue style transformer, skilled at converting ordinary conversations into ones that exhibit specific personality traits.

Task Description:
Your task is to transform the provided dialogue to express the following personality profile:

{chr(10).join(trait_descriptions)}

Transformation Steps:
1. First, understand the core semantics and intent of the original dialogue
2. Identify key points in the dialogue where personality traits can be enhanced
3. Design a transformation strategy to infuse the above personality profile while preserving original semantics
4. Execute the transformation, ensuring the language remains natural and fluid
5. Check that the transformed content retains the original semantics

Constraints:
- Maintain the basic semantics and functional intent of the original dialogue
- Avoid stereotypes or exaggerated expressions
- Ensure the transformed dialogue remains natural and fluid, like real human communication
- Adjust the dialogue style within reasonable limits, avoiding over-transformation

Output Format:
Please provide only the transformed dialogue text directly.

Please begin the dialogue transformation now.
"""
        return prompt
    
    def generate_target_trait_profile(self, trait_adjustments=None, realistic_distribution=False):
        """Generate a complete trait profile based on trait adjustments
        
        Args:
            trait_adjustments (dict, optional): Dictionary mapping trait codes to desired scores
                                              (e.g., {"E1": 0.8, "N": 0.3})
            realistic_distribution (bool): Use realistic personality distributions instead of random
        
        Returns:
            dict: Complete trait profile with scores for all dimensions and sub-traits
        """
        # 初始化基础性格特质配置文件
        profile = {}
        
        if realistic_distribution:
            # 使用符合现实分布的初始值
            # 大五人格维度分数通常呈正态分布，均值约为0.5，标准差约为0.15
            for dim in ["O", "C", "E", "A", "N"]:
                profile[dim] = max(0.1, min(0.9, random.gauss(0.5, 0.15),2))
                
            # 子特质通常与其所属维度相关，但有一定变异
            for trait_code in self.personality_framework.traits.keys():
                dimension = trait_code[0]
                # 子特质与维度得分相关，添加少量随机变异
                profile[trait_code] = max(0.1, min(0.9, profile[dimension] + random.uniform(-0.2, 0.2),2))
        else:
            # 使用随机初始值
            for dim in ["O", "C", "E", "A", "N"]:
                profile[dim] = round(random.uniform(0.3, 0.7), 2)
                
            # 添加所有子特质的随机初始值
            for trait_code in self.personality_framework.traits.keys():
                profile[trait_code] = round(random.uniform(0.3, 0.7), 2)
        
        # 如果提供了特定特质调整，应用这些设置
        if trait_adjustments:
            for trait_code, score in trait_adjustments.items():
                if trait_code in profile:
                    # 确保值在合理范围内
                    profile[trait_code] = round(max(0.1, min(0.9, score)), 2)
                    
                    # 如果调整的是维度，则相应地调整其子特质（除非子特质也有明确设置）
                    if len(trait_code) == 1:  # 是维度
                        dimension = trait_code
                        for sub_code in self.personality_framework.traits.keys():
                            if sub_code.startswith(dimension) and sub_code not in trait_adjustments:
                                # 调整子特质，但保持一定的随机性
                                adjustment = random.uniform(-0.15, 0.15)
                                profile[sub_code] = round(max(0.1, min(0.9, profile[dimension] + adjustment)), 2)
                
                # 如果调整的是子特质，则调整其所属维度的整体得分
                elif len(trait_code) == 2:
                    dimension = trait_code[0]
                    # 重新计算维度得分为所有子特质的平均值
                    sub_traits = [t for t in profile.keys() if t.startswith(dimension) and len(t) == 2]
                    if sub_traits:
                        profile[dimension] = round(sum(profile[t] for t in sub_traits) / len(sub_traits), 2)
            
            # 应用维度间的相关性
            dim_correlations = {
                "O": {"E": 0.2, "A": 0.1, "C": 0.1, "N": -0.1},
                "C": {"O": 0.1, "A": 0.2, "E": 0.0, "N": -0.2},
                "E": {"O": 0.2, "A": 0.1, "C": 0.0, "N": -0.3},
                "A": {"O": 0.1, "E": 0.1, "C": 0.2, "N": -0.3},
                "N": {"O": -0.1, "E": -0.3, "A": -0.3, "C": -0.2}
            }
            
            # 查找在trait_adjustments中明确设置的维度
            adjusted_dims = [d for d in ["O", "C", "E", "A", "N"] if d in trait_adjustments]
            
            # 基于这些设置的维度调整其他维度
            for dim in adjusted_dims:
                for other_dim, correlation in dim_correlations[dim].items():
                    # 只调整未明确设置的维度
                    if other_dim not in trait_adjustments and abs(correlation) > 0.05:
                        # 计算调整量，保留两位小数
                        adjustment = round((profile[dim] - 0.5) * correlation, 2)
                        profile[other_dim] = round(max(0.1, min(0.9, profile[other_dim] + adjustment)), 2)
                        
                        # 相应调整该维度的子特质
                        other_sub_traits = [t for t in profile.keys() if t.startswith(other_dim) and len(t) == 2 and t not in trait_adjustments]
                        for trait in other_sub_traits:
                            # 添加随机变化
                            random_factor = round(random.uniform(-0.1, 0.1), 2)
                            profile[trait] = round(max(0.1, min(0.9, profile[other_dim] + random_factor)), 2)
        
        return profile
    
    def transform_dialogue(self, dialogue, trait_adjustments=None, realistic_distribution=False):
        """Transform dialogue to exhibit specific personality traits
        
        Args:
            dialogue: List of dialogue turns
            trait_adjustments (dict, optional): Dictionary mapping trait codes to desired scores
                                              (e.g., {"E1": 0.8, "N": 0.3})
            realistic_distribution (bool): Whether to use realistic personality distributions
        
        Returns:
            tuple: (transformed_dialogue, trait_profile)
        """
        # 生成目标特质配置文件
        target_trait_profile = self.generate_target_trait_profile(
            trait_adjustments=trait_adjustments, 
            realistic_distribution=realistic_distribution
        )
        
        # 创建提示词
        prompt = self.create_personality_prompt(target_trait_profile)
        
        # 格式化对话内容
        dialogue_text = "\n".join([f"{'computer' if turn['role'] == 'assistant' else turn['role']}: {turn['content']}" for turn in dialogue])
        
        # 设置消息
        messages = [
            {"role": "system", "content": prompt},
            {"role": "user", "content": f"Please transform the following dialogue to exhibit the personality profile described above:\n\n{dialogue_text}"}
        ]
        
        # 获取LLM响应
        transformed_text = self.generate_response(messages)
        
        if not transformed_text:
            return None, None
        
        return transformed_text, target_trait_profile
        
    def transform_dialogue_with_multi_traits(self, dialogue, trait_configs, realistic_distribution=False):
        """Apply multiple personality trait transformations to the same dialogue
        
        Args:
            dialogue: List of dialogue turns
            trait_configs: List of trait adjustment dictionaries
                         or integer specifying number of random trait profiles to generate
                         or dictionary of trait adjustments to use as base for multiple profiles
            realistic_distribution: Whether to use realistic personality distributions
            
        Returns:
            dict: Dictionary of transformation results indexed by profile ID
        """
        results = {}
        
        # 处理不同的trait_configs类型
        if isinstance(trait_configs, int):
            # 如果是整数，生成指定数量的完全随机特质配置
            num_profiles = trait_configs
            trait_configs = [None] * num_profiles  # 创建N个None元素的列表
        elif isinstance(trait_configs, dict):
            # 如果是字典，将其作为基础配置，生成多个变体
            base_config = trait_configs
            num_profiles = base_config.pop('num_profiles', 1) if isinstance(base_config.get('num_profiles'), int) else 1
            
            # 创建多个基于base_config的变体配置
            trait_configs = []
            for i in range(num_profiles):
                # 复制基础配置
                variant_config = base_config.copy()
                
                # 为未设置的特质添加一些随机变化
                if i > 0:  # 第一个配置保持原样，后续配置添加随机变化
                    for dim in ["O", "C", "E", "A", "N"]:
                        # 仅为未明确设置的维度添加变化
                        if dim not in base_config:
                            variant_config[dim] = round(random.uniform(0.3, 0.7), 2)
                
                trait_configs.append(variant_config)
        
        # 处理每个特质配置
        for i, trait_config in enumerate(trait_configs):
            profile_id = f"profile_{i+1}"
            print(f"Transforming dialogue with {profile_id}...")
            
            try:
                transformed_text, trait_profile = self.transform_dialogue(
                    dialogue, 
                    trait_adjustments=trait_config,
                    realistic_distribution=realistic_distribution
                )
                
                if transformed_text and trait_profile:
                    # 提取转换后的对话轮次
                    transformed_turns = self.extract_dialogue_turns(transformed_text)
                    
                    # 记录结果
                    results[profile_id] = {
                        "transformed": transformed_turns,
                        "trait_profile": trait_profile
                    }
                    print(f"Successfully transformed dialogue with {profile_id}")
                else:
                    print(f"Warning: Transformation failed for {profile_id}")
            except Exception as e:
                print(f"Error in transformation {profile_id}: {e}")
            
            # 避免API速率限制
            time.sleep(2)
        
        return results
        
    def extract_dialogue_turns(self, transformed_text):
        """Extract dialogue turns from transformed text"""
        lines = transformed_text.strip().split('\n')
        turns = []
        
        for line in lines:
            if ':' in line:
                parts = line.split(':', 1)
                if len(parts) == 2:
                    role = parts[0].strip().lower()
                    content = parts[1].strip()
                    
                    # Normalize role names
                    if role in ['user']:
                        role = 'user'
                    elif role in ['assistant', 'ai', 'computer']:  # 添加 'computer' 角色的处理
                        role = 'assistant'
                    else:
                        continue  # Skip unrecognized roles
                        
                    turns.append({
                        'role': role,
                        'content': content
                    })
                    
        return turns
