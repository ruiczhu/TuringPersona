'''
多轮迭代优化数据处理脚本
用于对已转换的数据集进行多轮迭代优化
'''
import pandas as pd
import os
import time
import random
import argparse
import csv
from iterative_optimizer import IterativeOptimizer

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.config import API_KEY

def load_transformed_data(file_path):
    """加载转换后的数据"""
    df = pd.read_csv(file_path)
    return df

def group_transformed_data(df):
    """按对话ID和配置ID分组数据"""
    grouped_data = {}
    for _, row in df.iterrows():
        conv_id = row['conversation_id']
        profile_id = row['profile_id']
        
        if conv_id not in grouped_data:
            grouped_data[conv_id] = {}
            
        if profile_id not in grouped_data[conv_id]:
            grouped_data[conv_id][profile_id] = {
                'turns': [],
                'trait_profile': {}
            }
            
        # 添加对话轮次
        grouped_data[conv_id][profile_id]['turns'].append({
            'role': row['role'],
            'content': row['content'],
            'turn': row['turn'],
            'position': row['position']
        })
        
        # 解析人格特质配置（如果尚未添加）
        if not grouped_data[conv_id][profile_id]['trait_profile']:
            trait_profile = {}
            # 解析大五维度数据
            for dimension in ["O", "C", "E", "A", "N"]:
                dim_data = row[dimension]
                if isinstance(dim_data, str) and '{' in dim_data:
                    # 尝试解析格式为 "{维度得分:[子特质1,子特质2,...,子特质6]}" 的字符串
                    try:
                        # 提取维度得分
                        dim_score = float(dim_data.split('{')[1].split(':')[0].strip().replace('}', ''))
                        trait_profile[dimension] = dim_score
                        
                        # 提取子特质得分
                        sub_traits_str = dim_data.split('[')[1].split(']')[0]
                        sub_traits = [float(x.strip()) for x in sub_traits_str.split(',')]
                        
                        # 添加子特质得分
                        for i, score in enumerate(sub_traits):
                            trait_profile[f"{dimension}{i+1}"] = score
                    except:
                        # 如果解析失败，使用默认值
                        trait_profile[dimension] = 0.5
                        for i in range(1, 7):
                            trait_profile[f"{dimension}{i}"] = 0.5
                else:
                    # 如果没有维度数据，使用默认值
                    trait_profile[dimension] = 0.5
                    for i in range(1, 7):
                        trait_profile[f"{dimension}{i}"] = 0.5
                        
            grouped_data[conv_id][profile_id]['trait_profile'] = trait_profile
    
    # 按照对话轮次排序
    for conv_id in grouped_data:
        for profile_id in grouped_data[conv_id]:
            grouped_data[conv_id][profile_id]['turns'].sort(key=lambda x: (x['turn'], x['position']))
    
    return grouped_data

def apply_iterative_optimization(grouped_data, optimizer, sample_size=None, strategy='all', observations=None):
    """对转换后的对话应用迭代优化
    
    Args:
        grouped_data: 按对话ID和配置ID分组的数据
        optimizer: IterativeOptimizer实例
        sample_size: 处理的对话样本数量
        strategy: 优化策略
        observations: 外部观察反馈列表，用于observation策略
        
    Returns:
        优化后的结果字典
    """
    results = {}
    
    # 如果没有提供观察反馈且策略是observation，则提示用户需要提供观察反馈文件
    if strategy == 'observation' and not observations:
        print(f"错误: 使用'observation'策略时必须提供观察反馈文件。请使用--observations_path参数指定观察反馈文件路径。")
        return {}
    
    # 限制处理的对话数量
    conv_ids = list(grouped_data.keys())
    if sample_size and sample_size < len(conv_ids):
        conv_ids = random.sample(conv_ids, sample_size)
    
    for conv_id in conv_ids:
        results[conv_id] = {}
        
        for profile_id, data in grouped_data[conv_id].items():
            print(f"优化对话 {conv_id} 配置 {profile_id}...")
            
            # 准备对话轮次数据
            dialogue_turns = []
            for turn in data['turns']:
                dialogue_turns.append({
                    'role': turn['role'],
                    'content': turn['content']
                })
            
            try:
                # 应用优化策略
                optimized_turns = optimizer.optimize_dialogue(
                    dialogue_turns,
                    data['trait_profile'],
                    observations=observations,
                    strategy=strategy
                )
                
                if optimized_turns:
                    # 保存优化结果
                    results[conv_id][profile_id] = {
                        'original': data['turns'],
                        'optimized': [],
                        'trait_profile': data['trait_profile']
                    }
                    
                    # 合并优化后的内容和原始对话的元数据
                    for i, opt_turn in enumerate(optimized_turns):
                        if i < len(data['turns']):
                            turn_data = data['turns'][i].copy()
                            turn_data['content'] = opt_turn['content']
                            results[conv_id][profile_id]['optimized'].append(turn_data)
                        else:
                            # 如果优化后的轮次多于原始轮次，使用最后一个原始轮次的元数据
                            turn_data = data['turns'][-1].copy()
                            turn_data['content'] = opt_turn['content']
                            turn_data['turn'] = data['turns'][-1]['turn'] + (i - len(data['turns']) + 1)
                            results[conv_id][profile_id]['optimized'].append(turn_data)
                    
                    print(f"成功优化对话 {conv_id} 配置 {profile_id}")
                else:
                    print(f"警告：对话 {conv_id} 配置 {profile_id} 的优化失败")
            
            except Exception as e:
                print(f"优化对话 {conv_id} 配置 {profile_id} 时出错: {e}")
            
            # 避免API速率限制
            time.sleep(2)
    
    return results

def save_optimized_conversations(results, output_path):
    """保存优化后的对话
    
    Args:
        results: 优化结果字典
        output_path: 输出文件路径
    """
    with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
        # 创建表头行
        header = ['conversation_id', 'profile_id', 'role', 'content', 'turn', 'position', 
                  'O', 'C', 'E', 'A', 'N']
        
        writer = csv.writer(csvfile)
        writer.writerow(header)
        
        # 只写入优化后的对话数据
        for conv_id, profiles in results.items():
            for profile_id, data in profiles.items():
                # 写入优化后的对话行
                for turn in data['optimized']:
                    # 构建维度数据字段
                    dim_fields = []
                    for dimension in ["O", "C", "E", "A", "N"]:
                        dim_score = data['trait_profile'].get(dimension, 0.5)
                        sub_traits = []
                        for j in range(1, 7):
                            trait_code = f"{dimension}{j}"
                            sub_traits.append(data['trait_profile'].get(trait_code, 0.5))
                        
                        # 创建格式化字符串
                        dim_data = f"{{{dim_score}:{sub_traits}}}"
                        dim_fields.append(dim_data)
                    
                    # 构建完整行并写入
                    row = [
                        conv_id,
                        profile_id,
                        turn['role'],
                        turn['content'],
                        turn['turn'],
                        turn['position']
                    ] + dim_fields
                    writer.writerow(row)
    
    print(f"优化后的对话已保存至 {output_path}")

def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='对转换后的数据集应用多轮迭代优化策略')
    
    parser.add_argument('--input_path', type=str, required=True,
                        help='转换后数据CSV文件的路径')
    
    parser.add_argument('--output_dir', type=str,
                        default="MPEAF/dataset/optimized_data",
                        help='输出目录路径')
    
    parser.add_argument('--sample_size', type=int, default=3,
                        help='处理的对话样本数量')
    
    parser.add_argument('--random_seed', type=int, default=42,
                        help='随机种子，用于可重复性')
    
    parser.add_argument('--strategy', type=str, 
                        choices=['self_improvement', 'incremental', 'observation', 'progressive', 'all'], 
                        default='all',
                        help='使用的优化策略')
    
    parser.add_argument('--observations_path', type=str,
                        help='外部观察反馈文件路径（一行一个观察）')
    
    return parser.parse_args()

def main():
    # 解析参数
    args = parse_arguments()
    
    # 设置随机种子以确保可重现性
    random.seed(args.random_seed)
    
    # 配置
    input_path = args.input_path
    output_dir = args.output_dir
    sample_size = args.sample_size
    strategy = args.strategy
    observations_path = args.observations_path
    
    # 从文件中读取观察反馈（如果提供了文件路径）
    observations = None
    if observations_path and os.path.isfile(observations_path):
        try:
            with open(observations_path, 'r', encoding='utf-8') as f:
                observations = [line.strip() for line in f if line.strip()]
            print(f"已从{observations_path}加载{len(observations)}条观察反馈")
        except Exception as e:
            print(f"读取观察反馈文件时出错: {e}")
    
    # API密钥
    api_key = API_KEY
    
    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)
    
    # 初始化优化器
    optimizer = IterativeOptimizer(api_key)
    
    try:
        # 加载转换后的数据
        print("加载转换后的数据...")
        df = load_transformed_data(input_path)
        
        # 分组数据
        print("按对话ID和配置ID分组数据...")
        grouped_data = group_transformed_data(df)
        print(f"已加载 {len(grouped_data)} 个对话")
        
        # 应用迭代优化
        print(f"应用{strategy}优化策略...")
        results = apply_iterative_optimization(
            grouped_data, 
            optimizer, 
            sample_size=sample_size,
            strategy=strategy,
            observations=observations
        )
        
        # 保存结果
        timestamp = int(time.time())
        output_filename = f"optimized_data_{strategy}_{timestamp}.csv"
        output_path = os.path.join(output_dir, output_filename)
        print(f"保存结果至 {output_path}...")
        save_optimized_conversations(results, output_path)
        
        print("处理完成!")
        
    except Exception as e:
        print(f"发生错误: {e}")

if __name__ == "__main__":
    main()

# 使用示例:

# python MPEAF/optimizer/optimize_transformed_data.py --input_path MPEAF/dataset/transformed_data/sgd_dialogues_train_1744712149.csv --output_dir MPEAF/dataset/optimized_data --sample_size 3 --strategy all --observations_path MPEAF/optimizer/feedback/observation_feedback.txt

