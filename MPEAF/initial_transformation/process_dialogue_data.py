'''
对话数据处理与人格标注模块
用于处理各类对话数据集并应用人格特质转换
'''
import pandas as pd
import csv
import os
import time
import random
import argparse
import json

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from framework.personality_framework import PersonalityFramework
from config.config import API_KEY
from personality_transformer import PersonalityTransformer

def load_dialogue_data(file_path):
    """加载对话数据集
    
    Args:
        file_path: 对话数据CSV文件路径
        
    Returns:
        DataFrame: 加载的对话数据
    """
    df = pd.read_csv(file_path)
    return df

def group_conversations(df):
    """按对话ID分组数据
    
    Args:
        df: 对话数据DataFrame
        
    Returns:
        dict: 按对话ID分组的对话数据
    """
    conversations = {}
    for _, row in df.iterrows():
        conv_id = row['conversation_id']
        if conv_id not in conversations:
            conversations[conv_id] = []
        conversations[conv_id].append({
            'role': row['role'],
            'content': row['content'],
            'turn': row['turn'],
            'position': row['position']
        })
    return conversations

def apply_personality_traits(conversations, transformer, trait_sample, trait_adjustments=None, num_profiles=1, realistic_distribution=False):
    """应用人格特质转换，并为每个对话生成指定数量的人格配置
    
    Args:
        conversations: 按对话ID分组的对话数据字典
        transformer: PersonalityTransformer实例
        trait_sample: 要处理的对话数量
        trait_adjustments: 特质调整字典或特质调整字典列表
        num_profiles: 当未指定trait_adjustments时，为每个对话生成的人格配置文件数量
        realistic_distribution: 是否使用符合现实分布的人格特质
    
    Returns:
        dict: 转换结果字典
    """
    framework = PersonalityFramework()
    results = {}
    
    # 限制处理的对话数量
    if trait_sample >= len(conversations):
        conv_sample = conversations
    else:
        # 随机抽取对话ID
        sampled_ids = random.sample(list(conversations.keys()), trait_sample)
        conv_sample = {k: conversations[k] for k in sampled_ids}
    
    print(f"处理 {len(conv_sample)} 个对话，共 {len(conversations)} 个")
    
    for conv_id, turns in conv_sample.items():
        print(f"处理对话 {conv_id}...")
        
        # 确保对话中的 assistant 角色被替换为 computer，以与转换器保持一致
        formatted_turns = []
        for turn in turns:
            formatted_turn = turn.copy()
            if formatted_turn['role'] == 'assistant':
                formatted_turn['role'] = 'computer'
            formatted_turns.append(formatted_turn)
        
        # 确定要应用的特质配置
        if trait_adjustments:
            if isinstance(trait_adjustments, dict):
                # 当提供了特质配置且需要多个配置文件时
                if num_profiles > 1:
                    # 将dictionary类型的trait_adjustments和num_profiles合并为一个字典传递给transformer
                    # 这样transformer可以基于这个配置生成多个变体
                    trait_config = trait_adjustments.copy()
                    trait_config['num_profiles'] = num_profiles
                    trait_configs = trait_config
                else:
                    # 单个特质配置应用于所有对话
                    trait_configs = [trait_adjustments]
            else:
                # 多个特质配置
                trait_configs = trait_adjustments
        else:
            # 未指定特质配置，为每个对话生成指定数量的随机配置
            trait_configs = num_profiles
            
        try:
            # 应用多个性格转换
            transformation_results = transformer.transform_dialogue_with_multi_traits(
                formatted_turns, 
                trait_configs, 
                realistic_distribution
            )
            
            if transformation_results:
                # 保存转换结果
                results[conv_id] = {
                    'original': turns,
                    'transformed': transformation_results
                }
                print(f"成功转换对话 {conv_id}，生成 {len(transformation_results)} 个人格配置")
            else:
                print(f"警告：对话 {conv_id} 的所有转换均失败")
        
        except Exception as e:
            print(f"处理对话 {conv_id} 时出错: {e}")
        
        # 避免API速率限制
        time.sleep(1)
    
    return results

def save_transformed_conversations(results, output_path):
    """保存带有人格配置的转换后对话
    
    Args:
        results: 转换结果字典
        output_path: 保存转换后对话的文件路径
    """
    framework = PersonalityFramework()
    
    with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
        # 创建表头行 - 只保留基础信息和五个维度
        header = ['conversation_id', 'profile_id', 'role', 'content', 'turn', 'position', 
                  'O', 'C', 'E', 'A', 'N']
        
        writer = csv.writer(csvfile)
        writer.writerow(header)
        
        # 写入数据行
        for conv_id, data in results.items():
            original_turns = data['original']
            
            for profile_id, profile_data in data['transformed'].items():
                transformed_turns = profile_data['transformed']
                trait_profile = profile_data['trait_profile']
                
                for i, turn in enumerate(transformed_turns):
                    if i >= len(original_turns):
                        print(f"警告：对话 {conv_id} 的转换后轮次多于原始轮次")
                        continue
                        
                    # 创建基础行数据
                    row = [
                        conv_id,
                        profile_id,
                        turn['role'],
                        turn['content'],
                        original_turns[i]['turn'],
                        original_turns[i]['position']
                    ]
                    
                    # 为每个维度创建包含子特质的JSON格式
                    for dimension in ["O", "C", "E", "A", "N"]:
                        # 获取子特质分数
                        sub_traits = []
                        for j in range(1, 7):
                            trait_code = f"{dimension}{j}"
                            sub_traits.append(trait_profile.get(trait_code, 0.5))
                        
                        # 创建要求格式的字符串表示: "{维度得分:[子特质1,子特质2,...,子特质6]}"
                        dim_score = trait_profile.get(dimension, 0.5)
                        dim_data = f"{{{dim_score}:{sub_traits}}}"
                        row.append(dim_data)
                    
                    writer.writerow(row)
    
    print(f"转换后的对话已保存至 {output_path}")

def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='处理对话数据并应用人格特质标注')
    
    parser.add_argument('--data_path', type=str, 
                        default="MPEAF/dataset/cleaned_data/sgd_processed.csv",
                        help='对话数据CSV文件的路径')
    
    parser.add_argument('--output_dir', type=str,
                        default="MPEAF/dataset/transformed_data",
                        help='保存输出文件的目录')
    
    parser.add_argument('--sample_size', type=int, default=10,
                        help='处理的对话数量')
    
    parser.add_argument('--random_seed', type=int, default=42,
                        help='随机种子，用于可重复性')
    
    parser.add_argument('--split', type=str, choices=['train', 'test', 'val', 'all'], default='all',
                        help='要处理的数据集划分(train/test/val/all)')
    
    parser.add_argument('--split_ratio', type=str, default='0.7,0.15,0.15',
                        help='train,test,val的划分比例，如果split不是"all"(用逗号分隔)')
    
    parser.add_argument('--traits', type=str, default=None, 
                        help='JSON格式的特定特质调整(例如, \'{"E1":0.8,"N":0.3}\')或JSON文件路径')
    
    parser.add_argument('--num_profiles', type=int, default=1,
                        help='如果未指定traits，为每个对话生成的不同人格配置文件数量')
    
    parser.add_argument('--realistic_distribution', action='store_true',
                        help='使用符合现实分布的人格特质而非均匀随机分布')
    
    parser.add_argument('--output_prefix', type=str, default="dialogues_with_personality",
                        help='输出文件名前缀')
    
    return parser.parse_args()

def main():
    # 解析参数
    args = parse_arguments()
    
    # 设置随机种子以确保可重现性
    random.seed(args.random_seed)
    
    # 配置
    input_data_path = args.data_path
    output_dir = args.output_dir
    sample_size = args.sample_size
    output_prefix = args.output_prefix
    
    # 处理特质配置
    trait_adjustments = None
    if args.traits:
        if os.path.isfile(args.traits):
            # 如果是文件路径，从文件加载特质配置
            with open(args.traits, 'r') as f:
                trait_adjustments = json.load(f)
        else:
            # 尝试将其解析为JSON字符串
            try:
                trait_adjustments = json.loads(args.traits)
            except json.JSONDecodeError:
                print(f"警告：无法解析traits参数为JSON格式。使用默认行为。")
    
    # transformer的API密钥
    api_key = API_KEY
    
    # 如果输出目录不存在，则创建
    os.makedirs(output_dir, exist_ok=True)
    
    # 初始化transformer
    transformer = PersonalityTransformer(api_key)
    
    try:
        # 加载数据
        print("加载对话数据...")
        df = load_dialogue_data(input_data_path)
        
        # 分组对话
        print("对话数据分组...")
        all_conversations = group_conversations(df)
        print(f"已加载 {len(all_conversations)} 个对话")
        
        # 根据指定的分割方式处理数据集
        conversations = all_conversations
        if args.split != 'all':
            # 解析分割比例
            split_ratios = [float(r) for r in args.split_ratio.split(',')]
            if len(split_ratios) != 3 or abs(sum(split_ratios) - 1.0) > 0.001:
                print(f"警告：分割比例 {split_ratios} 之和不为1.0。进行归一化...")
                total = sum(split_ratios)
                split_ratios = [r / total for r in split_ratios]
            
            # 对会话ID进行排序以确保一致性
            conv_ids = sorted(all_conversations.keys())
            random.shuffle(conv_ids)  # 随机化顺序，但使用固定种子
            n_total = len(conv_ids)
            
            # 计算每个分割的大小
            n_train = int(n_total * split_ratios[0])
            n_test = int(n_total * split_ratios[1])
            
            # 分割数据集
            if args.split == 'train':
                selected_ids = conv_ids[:n_train]
            elif args.split == 'test':
                selected_ids = conv_ids[n_train:n_train+n_test]
            else:  # val
                selected_ids = conv_ids[n_train+n_test:]
                
            # 创建所选分割的会话子集
            conversations = {id: all_conversations[id] for id in selected_ids}
            print(f"选择了 {len(conversations)} 个对话用于 {args.split} 划分")
        
        # 应用人格特质转换
        print("应用人格特质转换...")
        results = apply_personality_traits(
            conversations, 
            transformer, 
            sample_size, 
            trait_adjustments=trait_adjustments,
            num_profiles=args.num_profiles,
            realistic_distribution=args.realistic_distribution
        )
        
        # 保存结果
        timestamp = int(time.time())
        split_suffix = "" if args.split == 'all' else f"_{args.split}"
        output_path = os.path.join(output_dir, f"{output_prefix}{split_suffix}_{timestamp}.csv")
        print(f"保存结果至 {output_path}...")
        save_transformed_conversations(results, output_path)
        
        print("处理完成!")
        
    except Exception as e:
        print(f"发生错误: {e}")

if __name__ == "__main__":
    main()


# 使用示例:

# python MPEAF/initial_transformation/process_dialogue_data.py --data_path MPEAF/dataset/cleaned_data/sgd_processed.csv --traits '{"E1":0.8,"N":0.3}' --num_profiles 3 --sample_size 2 --realistic_distribution --random_seed 42 --split train --split_ratio 0.7,0.15,0.15 --output_prefix sgd_dialogues

# python MPEAF/initial_transformation/process_dialogue_data.py --data_path MPEAF/dataset/cleaned_data/sgd_processed.csv --traits MPEAF/framework/traits_config/traits1.json --num_profiles 3 --sample_size 1 --realistic_distribution --random_seed 42 --split all --output_prefix sgd_dialogues