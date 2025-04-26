import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import networkx as nx
from mlxtend.frequent_patterns import apriori, association_rules
from mlxtend.preprocessing import TransactionEncoder
import os
import matplotlib as mpl
from matplotlib.font_manager import FontProperties
import io
import base64
from pathlib import Path

# 导入自定义字体模块
from embed_font import setup_chinese_font, get_font_prop

def perform_association_analysis(data_path, output_dir):
    # 使用统一的字体设置
    font_prop = setup_chinese_font()
    
    print(f"关联规则分析使用字体: {plt.rcParams['font.family']}")

    # 读取清洗后的数据
    df = pd.read_csv(data_path)
    
    # 为了进行关联规则分析，我们需要将数据转换为交易记录的格式
    # 假设我们要基于产品观看、添加到购物车和购买操作来发现规则
    
    # 首先检查必要的列是否存在
    required_columns = ['product_id', 'user_id', 'action_type']
    missing_columns = [col for col in required_columns if col not in df.columns]
    
    if missing_columns:
        print(f"警告: 以下必要列在数据集中不存在: {', '.join(missing_columns)}")
        # 如果缺少必要列，我们可以尝试创建替代列
        if 'product_id' in missing_columns and 'product_category' in df.columns:
            print("使用product_category代替product_id")
            df['product_id'] = df['product_category']
        if 'action_type' in missing_columns and 'is_purchase' in df.columns:
            print("基于is_purchase构造action_type")
            df['action_type'] = np.where(df['is_purchase'] == 1, '购买', '浏览')
        
        # 如果仍然缺少必要列，无法进行分析
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            print(f"错误: 无法继续分析，缺少必要列: {', '.join(missing_columns)}")
            return {
                'error': f"缺少必要列: {', '.join(missing_columns)}"
            }
    
    # 确保操作类型/行为类型列中的值是字符串格式
    df['action_type'] = df['action_type'].astype(str)
    
    # 创建交易数据
    # 为每个用户创建一个交易列表，其中包含他们执行的操作和相关产品
    transactions = []
    
    # 根据用户ID分组
    user_groups = df.groupby('user_id')
    
    for user_id, group in user_groups:
        # 为用户创建交易项
        items = []
        for _, row in group.iterrows():
            product = str(row['product_id'])
            action = str(row['action_type'])
            # 将产品和操作组合成一个项目，如 "产品A_购买"
            item = f"{product}_{action}"
            items.append(item)
        
        # 添加到交易列表
        if items:
            transactions.append(items)
    
    print(f"共有 {len(transactions)} 个用户交易记录用于关联规则分析")
    
    # 如果交易记录太少，则无法进行分析
    if len(transactions) < 10:
        print("错误: 交易记录太少，无法进行有意义的分析")
        return {
            'error': "交易记录太少，无法进行有意义的分析"
        }
    
    # 将交易数据转换为二进制编码
    te = TransactionEncoder()
    te_ary = te.fit(transactions).transform(transactions)
    df_encoded = pd.DataFrame(te_ary, columns=te.columns_)
    
    # 使用Apriori算法找出频繁项集
    min_support = 0.01  # 最小支持度
    try:
        frequent_itemsets = apriori(df_encoded, min_support=min_support, use_colnames=True)
        
        # 如果没有找到频繁项集，调整最小支持度并重试
        if len(frequent_itemsets) == 0:
            print("未找到频繁项集，降低最小支持度阈值...")
            min_support = 0.005
            frequent_itemsets = apriori(df_encoded, min_support=min_support, use_colnames=True)
            
            # 如果仍然没有找到频繁项集，再次降低阈值
            if len(frequent_itemsets) == 0:
                min_support = 0.001
                frequent_itemsets = apriori(df_encoded, min_support=min_support, use_colnames=True)
        
        print(f"使用最小支持度 {min_support} 找到 {len(frequent_itemsets)} 个频繁项集")
        
        # 如果仍然没有找到频繁项集，返回错误
        if len(frequent_itemsets) == 0:
            print("错误: 即使降低支持度阈值也无法找到频繁项集")
            return {
                'error': "无法找到频繁项集，请检查数据质量"
            }
            
        # 从频繁项集中找出关联规则
        rules = association_rules(frequent_itemsets, metric="confidence", min_threshold=0.3)
        
        print(f"找到 {len(rules)} 条关联规则")
        
        # 如果规则太少，降低阈值
        if len(rules) < 5:
            print("找到的规则太少，降低置信度阈值...")
            rules = association_rules(frequent_itemsets, metric="confidence", min_threshold=0.1)
            print(f"使用较低阈值后找到 {len(rules)} 条规则")
        
        # 如果仍然没有找到足够的规则，返回错误
        if len(rules) == 0:
            print("错误: 无法找到关联规则")
            return {
                'error': "无法找到关联规则，请检查数据质量"
            }
        
        # 保存规则到CSV
        rules_path = os.path.join(output_dir, 'association_rules.csv')
        rules.to_csv(rules_path, index=False)
        
        # 只保留最重要的信息列，便于前端显示
        simplified_rules = rules[['antecedents', 'consequents', 'support', 'confidence', 'lift']]
        
        # 将frozenset转换为可读字符串
        def format_itemset(itemset):
            return ', '.join(list(itemset))
        
        simplified_rules['antecedents'] = simplified_rules['antecedents'].apply(format_itemset)
        simplified_rules['consequents'] = simplified_rules['consequents'].apply(format_itemset)
        
        # 生成关联规则的网络图 - 适合中文显示
        plt.figure(figsize=(12, 10), facecolor='white')
        
        # 创建一个有向图
        G = nx.DiGraph()
        
        # 将规则添加到图中 - 只使用顶部规则以避免过度拥挤
        top_rules = rules.sort_values('lift', ascending=False).head(15)
        
        # 为每个规则添加节点和边
        for _, row in top_rules.iterrows():
            antecedents = list(row['antecedents'])
            consequents = list(row['consequents'])
            
            # 添加所有前项和后项作为节点
            for item in antecedents + consequents:
                if not G.has_node(item):
                    G.add_node(item)
            
            # 为每个前项到每个后项添加一条边
            for a_item in antecedents:
                for c_item in consequents:
                    G.add_edge(a_item, c_item, weight=row['lift'], 
                              confidence=row['confidence'], support=row['support'])
        
        # 设置节点位置
        pos = nx.spring_layout(G, k=0.15, iterations=50)
        
        # 绘制节点
        nx.draw_networkx_nodes(G, pos, node_color='skyblue', node_size=2000, alpha=0.8)
        
        # 绘制边，边的粗细表示提升度
        for u, v, data in G.edges(data=True):
            width = data['weight'] * 1.0  # 根据提升度调整边的宽度
            nx.draw_networkx_edges(G, pos, edgelist=[(u, v)], width=width, alpha=0.7, 
                                  edge_color='navy', arrows=True, arrowsize=20)
        
        # 添加节点标签 - 使用指定的中文字体
        nx.draw_networkx_labels(G, pos, font_size=10, font_color='black', font_family=plt.rcParams['font.family'], font_weight='bold')
        
        # 添加标题
        plt.title("商品关联规则网络图", fontproperties=font_prop, fontsize=16)
        
        # 保存图形
        network_image_path = os.path.join(output_dir, 'association_network.png')
        plt.axis('off')  # 关闭坐标轴
        plt.tight_layout()
        plt.savefig(network_image_path, dpi=300, bbox_inches='tight', format='png')
        plt.close()
        
        # 创建气泡图，展示关联规则的支持度、置信度和提升度
        plt.figure(figsize=(12, 8), facecolor='white')
        
        # 使用散点图展示规则，大小表示支持度，颜色表示提升度
        scatter = plt.scatter(rules['support'], rules['confidence'], 
                            s=rules['lift']*1000, # 将提升度转换为适当的点大小
                            alpha=0.6, 
                            c=rules['lift'], # 使用提升度作为颜色
                            cmap='viridis') 
        
        # 添加颜色条，显示提升度
        plt.colorbar(scatter, label='提升度 (Lift)')
        
        # 添加标题和轴标签 - 使用指定的中文字体
        plt.title('关联规则气泡图', fontproperties=font_prop, fontsize=16)
        plt.xlabel('支持度 (Support)', fontproperties=font_prop, fontsize=14)
        plt.ylabel('置信度 (Confidence)', fontproperties=font_prop, fontsize=14)
        
        # 添加网格线
        plt.grid(True, linestyle='--', alpha=0.7)
        
        # 保存气泡图
        bubble_image_path = os.path.join(output_dir, 'association_bubble.png')
        plt.tight_layout()
        plt.savefig(bubble_image_path, dpi=300, bbox_inches='tight', format='png')
        plt.close()
        
        # 返回分析结果
        return {
            'rules_path': rules_path,
            'network_image': network_image_path,
            'bubble_image': bubble_image_path,
            'rules_count': len(rules),
            'top_rules': simplified_rules.head(10).to_dict('records')
        }
    
    except Exception as e:
        print(f"关联规则分析过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        return {
            'error': f"分析过程中发生错误: {str(e)}"
        } 