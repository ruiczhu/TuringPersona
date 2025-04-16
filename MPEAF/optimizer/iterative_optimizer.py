'''
多轮迭代优化策略模块
实现基于Project Outline中描述的多轮迭代优化策略:
1. 自我改进（Self-Improvement）
2. 可逐步调整的增量修改
3. 基于观察的修复
4. 渐进式目标强化
'''
import json
import time
import random

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from framework.personality_framework import PersonalityFramework

class IterativeOptimizer:
    def __init__(self, api_key, personality_framework=None):
        """初始化迭代优化器
        
        Args:
            api_key: LLM API的密钥
            personality_framework: 人格框架对象
        """
        self.api_key = api_key
        self.personality_framework = personality_framework or PersonalityFramework()
        self.headers = {
            "Content-Type": "application/json",
            "api-key": api_key,
        }
        self.endpoint = "https://genai-jp.openai.azure.com/openai/deployments/ln-gpt40/chat/completions?api-version=2024-02-15-preview"
        
    def generate_response(self, messages, temperature=0.7, max_tokens=1000):
        """调用LLM API生成响应"""
        import requests
        
        payload = {
            "messages": messages,
            "temperature": temperature,
            "top_p": 0.95,
            "max_tokens": max_tokens
        }
        
        try:
            # 添加重试机制
            max_retries = 3
            retry_count = 0
            
            while retry_count < max_retries:
                try:
                    response = requests.post(self.endpoint, headers=self.headers, json=payload)
                    response.raise_for_status()
                    return response.json()['choices'][0]['message']['content']
                except requests.RequestException as e:
                    print(f"API请求错误: {e}")
                    print(f"重试 {retry_count + 1}/{max_retries}...")
                    retry_count += 1
                    time.sleep(2 + retry_count)  # 指数退避
            
            print("所有重试失败")
            return None
        except Exception as e:
            print(f"响应解析错误: {e}")
            return None
            
    def self_improvement(self, dialogue, trait_profile, iterations=2):
        """自我改进优化策略
        
        基于Madaan等人和Wang等人的研究，通过自我批评不断改进生成结果
        
        Args:
            dialogue: 转换后的对话内容
            trait_profile: 目标人格特质配置
            iterations: 迭代改进次数
        
        Returns:
            优化后的对话内容
        """
        # 格式化对话内容为字符串
        dialogue_str = "\n".join([f"{'user' if turn['role'] == 'user' else 'computer'}: {turn['content']}" for turn in dialogue])
        current_dialogue = dialogue_str
        
        # 格式化人格特质配置
        trait_descriptions = []
        for dimension in ["O", "C", "E", "A", "N"]:
            dim_name = self.personality_framework.big_five_dimensions[dimension]
            dim_score = trait_profile.get(dimension, 0.5)
            trait_descriptions.append(f"- {dim_name} ({dimension}): {dim_score:.2f}/1.0")
            
        trait_profile_str = "\n".join(trait_descriptions)
        
        # 进行多轮自我改进
        for i in range(iterations):
            # 创建自我批评提示
            messages = [
                {"role": "system", "content": f"""You are a professional dialogue quality assessment and improvement assistant, specializing in evaluating and enhancing personality expression in dialogues.

Task Description:
Please evaluate the following dialogue based on the given personality trait configuration and provide specific improvement suggestions. First identify where personality expressions are inaccurate or insufficient, then propose detailed improvement plans.

Target Personality Configuration:
{trait_profile_str}

Evaluation Steps:
1. Analyze whether personality trait expressions in the dialogue align with the target configuration
2. Identify parts where expressions are unclear or mismatched with traits
3. Provide specific improvement suggestions, explaining how to better demonstrate target personality traits
4. Pay special attention to any unnatural or overly stereotypical expressions

Please provide detailed critical analysis and specific improvement suggestions for the next modification step."""},
                {"role": "user", "content": f"请评估并提供改进建议：\n\n{current_dialogue}"}
            ]
            
            # 获取自我批评
            critique = self.generate_response(messages)
            if not critique:
                return current_dialogue
            
            # 基于自我批评进行改进
            messages = [
                {"role": "system", "content": f"""As a dialogue optimization expert, your task is to improve the dialogue based on assessment feedback, making it express specific personality traits more accurately.

Target Personality Configuration:
{trait_profile_str}

Improvement Requirements:
1. Address all personality expression issues pointed out in the assessment
2. Maintain the dialogue's natural flow and semantic integrity
3. Avoid overly stereotypical personality expressions
4. Ensure the modified dialogue displays consistent personality traits

Output Format:
Only provide the complete modified dialogue, maintaining the original speaker labels (user: and computer:)."""},
                {"role": "user", "content": f"原始对话：\n\n{current_dialogue}\n\n评估反馈：\n\n{critique}\n\n请根据评估反馈修改对话："}
            ]
            
            # 获取改进后的对话
            improved_dialogue = self.generate_response(messages)
            if improved_dialogue:
                current_dialogue = improved_dialogue
                
            # 添加一些延迟以避免API限制
            time.sleep(1)
            
        return current_dialogue
    
    def incremental_modification(self, dialogue, trait_profile):
        """可逐步调整的增量修改策略
        
        采用Kim等人的增量式文本编辑方法，将复杂转换分解为小步骤
        
        Args:
            dialogue: 转换后的对话内容
            trait_profile: 目标人格特质配置
            
        Returns:
            优化后的对话内容
        """
        # 格式化对话内容为字符串
        dialogue_str = "\n".join([f"{'user' if turn['role'] == 'user' else 'computer'}: {turn['content']}" for turn in dialogue])
        
        # 格式化人格特质配置
        trait_descriptions = []
        for dimension in ["O", "C", "E", "A", "N"]:
            dim_name = self.personality_framework.big_five_dimensions[dimension]
            dim_score = trait_profile.get(dimension, 0.5)
            trait_descriptions.append(f"- {dim_name} ({dimension}): {dim_score:.2f}/1.0")
            
        trait_profile_str = "\n".join(trait_descriptions)
        
        # 创建增量修改提示
        messages = [
            {"role": "system", "content": f"""As a dialogue optimization expert, your task is to improve personality expression in dialogues through an incremental modification strategy.

Target Personality Configuration:
{trait_profile_str}

Incremental Modification Steps:
1. First adjust keywords and expression styles:
   - Identify keywords that can be replaced
   - Adjust emotional expression intensity
   - Modify tone and manner of expression

2. Then optimize sentence structure:
   - Restructure complex expressions
   - Adjust sentence length and complexity
   - Add or remove details as necessary

3. Finally optimize overall coherence:
   - Ensure consistent personality expression
   - Adjust dialogue flow
   - Enhance natural flow

Output Format:
Only provide the final optimized complete dialogue, maintaining the original speaker labels (user: and computer:)."""},
            {"role": "user", "content": f"请对以下对话进行增量修改优化：\n\n{dialogue_str}"}
        ]
        
        # 获取增量修改后的对话
        modified_dialogue = self.generate_response(messages)
        return modified_dialogue or dialogue_str
    
    def observation_based_repair(self, dialogue, trait_profile, observations):
        """基于观察的修复策略
        
        整合Welleck等人的自然语言反馈框架，利用外部观察精确指导修正
        
        Args:
            dialogue: 转换后的对话内容
            trait_profile: 目标人格特质配置
            observations: 外部评估者提供的观察反馈列表
            
        Returns:
            修复后的对话内容
        """
        # 格式化对话内容为字符串
        dialogue_str = "\n".join([f"{'user' if turn['role'] == 'user' else 'computer'}: {turn['content']}" for turn in dialogue])
        
        # 格式化人格特质配置
        trait_descriptions = []
        for dimension in ["O", "C", "E", "A", "N"]:
            dim_name = self.personality_framework.big_five_dimensions[dimension]
            dim_score = trait_profile.get(dimension, 0.5)
            trait_descriptions.append(f"- {dim_name} ({dimension}): {dim_score:.2f}/1.0")
            
        trait_profile_str = "\n".join(trait_descriptions)
        
        # 格式化外部观察反馈
        observations_str = "\n".join([f"- {obs}" for obs in observations])
        
        # 创建基于观察的修复提示
        messages = [
            {"role": "system", "content": f"""As a dialogue optimization expert, your task is to repair personality expression issues in dialogues based on specific observational feedback provided by external evaluators.

Target Personality Configuration:
{trait_profile_str}

External Observation Feedback:
{observations_str}

Repair Requirements:
1. Address each observation feedback with targeted fixes
2. Maintain the dialogue's natural flow and semantic integrity
3. Ensure the repaired dialogue more accurately demonstrates the target personality traits
4. Avoid introducing new unnatural expressions or stereotypes

Output Format:
Only provide the complete repaired dialogue, maintaining the original speaker labels (user: and computer:)."""},
            {"role": "user", "content": f"请修复以下对话：\n\n{dialogue_str}"}
        ]
        
        # 获取修复后的对话
        repaired_dialogue = self.generate_response(messages)
        return repaired_dialogue or dialogue_str
    
    def progressive_enhancement(self, dialogue, trait_profile, enhancement_levels=3):
        """渐进式目标强化策略
        
        基于Stiennon等人的研究，采用渐进增强策略逐步提高人格表达准确度
        
        Args:
            dialogue: 转换后的对话内容
            trait_profile: 目标人格特质配置
            enhancement_levels: 增强级别数量
            
        Returns:
            强化后的对话内容
        """
        # 格式化对话内容为字符串
        dialogue_str = "\n".join([f"{'user' if turn['role'] == 'user' else 'computer'}: {turn['content']}" for turn in dialogue])
        current_dialogue = dialogue_str
        
        # 格式化人格特质配置
        trait_descriptions = []
        for dimension in ["O", "C", "E", "A", "N"]:
            dim_name = self.personality_framework.big_five_dimensions[dimension]
            dim_score = trait_profile.get(dimension, 0.5)
            trait_descriptions.append(f"- {dim_name} ({dimension}): {dim_score:.2f}/1.0")
            
        trait_profile_str = "\n".join(trait_descriptions)
        
        # 定义不同级别的增强要求
        enhancement_requirements = [
            "确保基本语义保留，同时开始展现人格特质的基本表达",  # 基础级别
            "在保持语义的前提下，进一步加强人格特质的明显表达，重点关注主要维度",  # 中级强化
            "全面优化人格表达，确保每个回复都精确反映目标人格特质，同时保持对话自然流畅"  # 高级强化
        ]
        
        # 进行渐进式增强
        for level in range(min(enhancement_levels, len(enhancement_requirements))):
            requirement = enhancement_requirements[level]
            
            # 创建渐进式增强提示
            messages = [
                {"role": "system", "content": f"""As a dialogue optimization expert, your task is to optimize personality expressions in dialogues using a progressive enhancement strategy.

Target Personality Configuration:
{trait_profile_str}

Current Optimization Level ({level + 1}/{len(enhancement_requirements)}):
{requirement}

Optimization Requirements:
1. Adjust the dialogue according to the current optimization level requirements
2. Maintain the dialogue's natural flow and semantic integrity
3. Progressively enhance the accuracy of personality trait expressions
4. Avoid overly stereotypical personality expressions

Output Format:
Only provide the optimized complete dialogue, maintaining the original speaker labels (user: and computer:)."""},
                {"role": "user", "content": f"请对以下对话进行第{level + 1}级优化：\n\n{current_dialogue}"}
            ]
            
            # 获取强化后的对话
            enhanced_dialogue = self.generate_response(messages)
            if enhanced_dialogue:
                current_dialogue = enhanced_dialogue
                
            # 添加一些延迟以避免API限制
            time.sleep(1)
            
        return current_dialogue
    
    def extract_dialogue_turns(self, dialogue_text):
        """提取对话轮次
        
        Args:
            dialogue_text: 对话文本字符串
            
        Returns:
            对话轮次列表
        """
        lines = dialogue_text.strip().split('\n')
        turns = []
        
        for line in lines:
            if ':' in line:
                parts = line.split(':', 1)
                if len(parts) == 2:
                    role = parts[0].strip().lower()
                    content = parts[1].strip()
                    
                    # 标准化角色名称
                    if role in ['user']:
                        role = 'user'
                    elif role in ['assistant', 'ai', 'computer']:
                        role = 'assistant'
                    else:
                        continue  # 跳过未识别的角色
                        
                    turns.append({
                        'role': role,
                        'content': content
                    })
                    
        return turns
    
    def optimize_dialogue(self, dialogue, trait_profile, observations=None, strategy='all'):
        """综合优化对话
        
        使用一种或多种优化策略对对话进行优化
        
        Args:
            dialogue: 转换后的对话内容
            trait_profile: 目标人格特质配置
            observations: 外部观察反馈列表
            strategy: 优化策略，可以是'self_improvement', 'incremental', 'observation', 'progressive'或'all'
            
        Returns:
            优化后的对话轮次列表
        """
        if strategy == 'self_improvement':
            optimized_dialogue = self.self_improvement(dialogue, trait_profile)
            return self.extract_dialogue_turns(optimized_dialogue)
        
        elif strategy == 'incremental':
            optimized_dialogue = self.incremental_modification(dialogue, trait_profile)
            return self.extract_dialogue_turns(optimized_dialogue)
        
        elif strategy == 'observation' and observations:
            optimized_dialogue = self.observation_based_repair(dialogue, trait_profile, observations)
            return self.extract_dialogue_turns(optimized_dialogue)
        
        elif strategy == 'progressive':
            optimized_dialogue = self.progressive_enhancement(dialogue, trait_profile)
            return self.extract_dialogue_turns(optimized_dialogue)
        
        elif strategy == 'all':
            # 应用所有策略进行优化
            dialogue_str = self.incremental_modification(dialogue, trait_profile)
            dialogue_turns = self.extract_dialogue_turns(dialogue_str)
            
            dialogue_str = self.self_improvement(dialogue_turns, trait_profile)
            dialogue_turns = self.extract_dialogue_turns(dialogue_str)
            
            if observations:
                dialogue_str = self.observation_based_repair(dialogue_turns, trait_profile, observations)
                dialogue_turns = self.extract_dialogue_turns(dialogue_str)
            
            dialogue_str = self.progressive_enhancement(dialogue_turns, trait_profile)
            return self.extract_dialogue_turns(dialogue_str)
        
        else:
            # 默认返回原始对话
            return dialogue
