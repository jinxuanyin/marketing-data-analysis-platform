import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from mlxtend.frequent_patterns import apriori, association_rules
from mlxtend.preprocessing import TransactionEncoder
import os
import datetime
from pathlib import Path
import matplotlib as mpl
from collections import Counter

# 导入自定义字体模块
from embed_font import setup_chinese_font, get_font_prop

def perform_basket_analysis(data_path, output_dir, min_support=0.01, min_threshold=0.5):
    # 使用统一的字体设置
    font_prop = setup_chinese_font()
    
    print(f"购物篮分析使用字体: {plt.rcParams['font.family']}")
    
    # 读取清洗后的数据
    df = pd.read_csv(data_path)
    
    # 检查必要的列是否存在
    required_columns = ['user_id', 'product_id', 'product_name']
    missing_columns = [col for col in required_columns if col not in df.columns]
    
    # 尝试寻找替代列
    replacements = {
        'user_id': ['customer_id', 'client_id', 'id'],
        'product_id': ['item_id', 'sku', 'product_code'],
        'product_name': ['item_name', 'name', 'product']
    }
    
    for missing in missing_columns.copy():
        possible_replacements = replacements.get(missing, [])
        for replacement in possible_replacements:
            if replacement in df.columns:
                print(f"使用 {replacement} 替代 {missing}")
                df[missing] = df[replacement]
                missing_columns.remove(missing)
                break
    
    if missing_columns:
        print(f"错误: 无法继续分析，缺少必要列: {', '.join(missing_columns)}")
        return {
            'error': f"缺少必要列: {', '.join(missing_columns)}"
        }
    
    # 如果数据量太大，使用随机抽样减少计算量
    if len(df) > 100000:
        print(f"数据量较大 ({len(df)} 行)，随机抽样 100,000 行进行分析")
        df = df.sample(n=100000, random_state=42)
    
    # 按用户分组创建购物篮
    baskets = df.groupby(['user_id', 'product_name'])['product_id'].count().unstack().reset_index().fillna(0)
    baskets = baskets.drop('user_id', axis=1)
    
    # 检查产品数量，如果太多，只保留最受欢迎的产品
    if baskets.shape[1] > 100:
        print(f"产品数量过多 ({baskets.shape[1]}), 只保留前100个最常购买的产品")
        product_counts = df['product_name'].value_counts().head(100).index.tolist()
        mask = df['product_name'].isin(product_counts)
        df_filtered = df[mask]
        baskets = df_filtered.groupby(['user_id', 'product_name'])['product_id'].count().unstack().reset_index().fillna(0)
        baskets = baskets.drop('user_id', axis=1)
    
    # 将数据转换为二进制格式（购买 = 1，未购买 = 0）
    basket_sets = baskets.applymap(lambda x: 1 if x > 0 else 0)
    
    # 检查数据是否足够
    if basket_sets.shape[0] < 10 or basket_sets.shape[1] < 2:
        print("错误: 数据不足，无法进行有意义的购物篮分析")
        return {
            'error': "数据不足，无法进行有意义的购物篮分析"
        }
    
    # 计算频繁项集，动态调整支持度阈值
    adjusted_min_support = min_support
    
    # 自动调整支持度直到找到频繁项集
    frequent_itemsets = apriori(basket_sets, min_support=adjusted_min_support, use_colnames=True)
    
    attempts = 0
    while len(frequent_itemsets) < 5 and attempts < 5:
        adjusted_min_support = adjusted_min_support / 2.0
        print(f"将最小支持度调整至 {adjusted_min_support}")
        frequent_itemsets = apriori(basket_sets, min_support=adjusted_min_support, use_colnames=True)
        attempts += 1
    
    if len(frequent_itemsets) == 0:
        print("错误: 无法找到频繁项集，请尝试降低最小支持度阈值")
        return {
            'error': "无法找到频繁项集，请尝试降低最小支持度阈值"
        }
    
    # 生成关联规则
    rules = association_rules(frequent_itemsets, metric="lift", min_threshold=min_threshold)
    
    if len(rules) == 0:
        # 如果没有找到规则，降低阈值
        min_threshold = 0.1
        print(f"降低最小阈值至 {min_threshold}")
        rules = association_rules(frequent_itemsets, metric="lift", min_threshold=min_threshold)
        
        if len(rules) == 0:
            print("错误: 找不到关联规则，请尝试降低阈值或增加数据量")
            return {
                'error': "找不到关联规则，请尝试降低阈值或增加数据量"
            }
    
    # 转换frozenset为字符串以便保存和展示
    rules["antecedents"] = rules["antecedents"].apply(lambda x: ', '.join(list(x)))
    rules["consequents"] = rules["consequents"].apply(lambda x: ', '.join(list(x)))
    
    # 保存关联规则结果
    rules_path = os.path.join(output_dir, 'basket_rules.csv')
    rules.to_csv(rules_path, index=False)
    
    # 分析规则的支持度、置信度和提升度分布
    plt.figure(figsize=(18, 6), facecolor='white')
    
    # 支持度分布
    plt.subplot(1, 3, 1)
    sns.histplot(rules['support'], kde=True, color='skyblue')
    plt.title('支持度分布', fontproperties=font_prop, fontsize=14)
    plt.xlabel('支持度', fontproperties=font_prop, fontsize=12)
    plt.ylabel('频率', fontproperties=font_prop, fontsize=12)
    
    # 置信度分布
    plt.subplot(1, 3, 2)
    sns.histplot(rules['confidence'], kde=True, color='lightgreen')
    plt.title('置信度分布', fontproperties=font_prop, fontsize=14)
    plt.xlabel('置信度', fontproperties=font_prop, fontsize=12)
    plt.ylabel('频率', fontproperties=font_prop, fontsize=12)
    
    # 提升度分布
    plt.subplot(1, 3, 3)
    sns.histplot(rules['lift'], kde=True, color='salmon')
    plt.title('提升度分布', fontproperties=font_prop, fontsize=14)
    plt.xlabel('提升度', fontproperties=font_prop, fontsize=12)
    plt.ylabel('频率', fontproperties=font_prop, fontsize=12)
    
    plt.tight_layout()
    metrics_image_path = os.path.join(output_dir, 'basket_metrics_distribution.png')
    plt.savefig(metrics_image_path, dpi=300, bbox_inches='tight', format='png')
    plt.close()
    
    # 散点图：支持度vs提升度，点大小表示置信度
    plt.figure(figsize=(10, 8), facecolor='white')
    plt.scatter(rules['support'], rules['lift'], alpha=0.5, s=rules['confidence']*100, c='skyblue')
    plt.title('关联规则分布：支持度、提升度和置信度', fontproperties=font_prop, fontsize=14)
    plt.xlabel('支持度', fontproperties=font_prop, fontsize=12)
    plt.ylabel('提升度', fontproperties=font_prop, fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.7)
    
    # 添加标注
    for i, row in rules.sort_values('lift', ascending=False).head(5).iterrows():
        plt.annotate(
            f"{row['antecedents']} -> {row['consequents']}",
            xy=(row['support'], row['lift']),
            xytext=(5, 5),
            textcoords='offset points',
            fontproperties=font_prop,
            fontsize=8
        )
    
    scatter_image_path = os.path.join(output_dir, 'basket_scatter.png')
    plt.savefig(scatter_image_path, dpi=300, bbox_inches='tight', format='png')
    plt.close()
    
    # 创建网络图表示关联规则
    import networkx as nx
    
    # 选择提升度最高的规则子集
    top_rules = rules.sort_values('lift', ascending=False).head(15)
    
    G = nx.DiGraph()
    
    # 添加节点和边
    for i, row in top_rules.iterrows():
        antecedent = row['antecedents']
        consequent = row['consequents']
        
        # 添加节点
        if antecedent not in G.nodes():
            G.add_node(antecedent)
        if consequent not in G.nodes():
            G.add_node(consequent)
        
        # 添加边，权重为提升度
        G.add_edge(antecedent, consequent, weight=row['lift'], confidence=row['confidence'])
    
    # 创建图形
    plt.figure(figsize=(12, 10), facecolor='white')
    
    # 使用spring布局
    pos = nx.spring_layout(G)
    
    # 根据提升度计算边的宽度
    edge_widths = [G[u][v]['weight'] / 2 for u, v in G.edges()]
    
    # 绘制节点和边
    nx.draw_networkx_nodes(G, pos, node_size=1500, node_color='lightblue', alpha=0.8)
    nx.draw_networkx_edges(G, pos, width=edge_widths, edge_color='gray', alpha=0.6)
    
    # 添加节点标签
    labels = {node: node for node in G.nodes()}
    nx.draw_networkx_labels(G, pos, labels=labels, font_size=8, font_family=plt.rcParams['font.family'])
    
    # 添加边标签（显示提升度）
    edge_labels = {(u, v): f"{G[u][v]['weight']:.2f}" for u, v in G.edges()}
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=8, font_family=plt.rcParams['font.family'])
    
    plt.title('产品关联网络图 (Top 15)', fontproperties=font_prop, fontsize=16)
    plt.axis('off')
    network_image_path = os.path.join(output_dir, 'basket_network.png')
    plt.savefig(network_image_path, dpi=300, bbox_inches='tight', format='png')
    plt.close()
    
    # 计算每个产品在关联规则中的出现频率
    product_occurrences = Counter()
    
    # 计算每个产品在前提和结果中的出现次数
    for i, row in rules.iterrows():
        antecedent_products = row['antecedents'].split(', ')
        consequent_products = row['consequents'].split(', ')
        
        for product in antecedent_products:
            product_occurrences[product] += 1
        
        for product in consequent_products:
            product_occurrences[product] += 1
    
    # 选择出现频率最高的10个产品
    top_products = pd.DataFrame(product_occurrences.most_common(10), columns=['product', 'frequency'])
    
    # 产品频率柱状图
    plt.figure(figsize=(12, 8), facecolor='white')
    bars = plt.bar(top_products['product'], top_products['frequency'], color=sns.color_palette('pastel'))
    plt.title('关联规则中最常出现的产品', fontproperties=font_prop, fontsize=14)
    plt.xlabel('产品', fontproperties=font_prop, fontsize=12)
    plt.ylabel('出现频率', fontproperties=font_prop, fontsize=12)
    plt.xticks(rotation=45, ha='right', fontproperties=font_prop)
    plt.tight_layout()
    
    # 添加数值标签
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                 f'{height}',
                 ha='center', va='bottom', fontproperties=font_prop, fontsize=10)
    
    top_products_image_path = os.path.join(output_dir, 'basket_top_products.png')
    plt.savefig(top_products_image_path, dpi=300, bbox_inches='tight', format='png')
    plt.close()
    
    # 创建热图显示项目之间的共现关系
    # 选择最常出现的前15个产品
    most_common_products = [item[0] for item in product_occurrences.most_common(15)]
    
    # 创建共现矩阵
    cooccurrence_matrix = pd.DataFrame(0, index=most_common_products, columns=most_common_products)
    
    # 填充共现矩阵
    for i, row in rules.iterrows():
        antecedent_products = row['antecedents'].split(', ')
        consequent_products = row['consequents'].split(', ')
        all_products = antecedent_products + consequent_products
        
        # 筛选出在最常出现产品列表中的产品
        relevant_products = [p for p in all_products if p in most_common_products]
        
        # 更新共现矩阵
        for p1 in relevant_products:
            for p2 in relevant_products:
                if p1 != p2:  # 避免自我关联
                    cooccurrence_matrix.loc[p1, p2] += 1
    
    # 创建热图
    plt.figure(figsize=(12, 10), facecolor='white')
    mask = np.triu(np.ones_like(cooccurrence_matrix, dtype=bool))  # 创建上三角掩码
    
    sns.heatmap(cooccurrence_matrix, annot=True, fmt='d', cmap='YlGnBu', 
                linewidths=0.5, mask=mask, cbar_kws={'label': '共现次数'})
    
    plt.title('产品共现热图', fontproperties=font_prop, fontsize=16)
    plt.xticks(rotation=45, ha='right', fontproperties=font_prop)
    plt.yticks(fontproperties=font_prop)
    plt.tight_layout()
    
    cooccurrence_image_path = os.path.join(output_dir, 'basket_cooccurrence.png')
    plt.savefig(cooccurrence_image_path, dpi=300, bbox_inches='tight', format='png')
    plt.close()
    
    # 返回分析结果
    return {
        'rules_path': rules_path,
        'metrics_image': metrics_image_path,
        'scatter_image': scatter_image_path,
        'network_image': network_image_path,
        'top_products_image': top_products_image_path,
        'cooccurrence_image': cooccurrence_image_path,
        'rule_count': len(rules),
        'support_threshold': adjusted_min_support,
        'confidence_threshold': min_threshold,
        'frequent_itemsets_count': len(frequent_itemsets),
        'top_rules': rules.sort_values('lift', ascending=False).head(5)[['antecedents', 'consequents', 'lift', 'confidence']].to_dict('records')
    } 