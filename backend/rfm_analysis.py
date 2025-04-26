import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import os
import matplotlib as mpl
from matplotlib.font_manager import FontProperties
import io
import base64
from sklearn.cluster import KMeans
from pathlib import Path

# 导入自定义字体模块
from embed_font import setup_chinese_font, get_font_prop

def perform_rfm_analysis(data_path, output_dir):
    # 使用统一的字体设置
    font_prop = setup_chinese_font()

    print(f"RFM分析使用字体: {plt.rcParams['font.family']}")
    
    # 读取清洗后的数据
    df = pd.read_csv(data_path)
    
    # 首先检查必要的列是否存在
    required_columns = ['user_id', 'purchase_date', 'purchase_amount']
    missing_columns = [col for col in required_columns if col not in df.columns]
    
    # 尝试寻找替代列
    replacements = {
        'user_id': ['customer_id', 'client_id', 'id'],
        'purchase_date': ['order_date', 'transaction_date', 'date'],
        'purchase_amount': ['amount', 'price', 'sales_amount', 'order_value']
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
    
    # 确保日期格式正确
    try:
        df['purchase_date'] = pd.to_datetime(df['purchase_date'])
    except Exception as e:
        print(f"无法转换日期格式: {e}")
        # 尝试常见的日期格式
        date_formats = ['%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y', '%Y/%m/%d']
        converted = False
        for date_format in date_formats:
            try:
                df['purchase_date'] = pd.to_datetime(df['purchase_date'], format=date_format)
                converted = True
                break
            except:
                continue
        
        if not converted:
            print("无法识别日期格式，使用当前日期-行号作为替代")
            today = datetime.now()
            df['purchase_date'] = pd.Series([today - pd.Timedelta(days=i) for i in range(len(df))])
    
    # 计算RFM值
    # 选择截止日期（默认使用数据中最近的日期）
    snapshot_date = df['purchase_date'].max() + pd.Timedelta(days=1)
    
    # 按客户分组并计算RFM指标
    rfm = df.groupby('user_id').agg({
        'purchase_date': lambda x: (snapshot_date - x.max()).days,  # 最近一次购买距今天数
        'purchase_amount': ['sum', 'count']  # 总消费金额和消费次数
    })
    
    # 重命名列
    rfm.columns = ['recency', 'monetary', 'frequency']
    
    # 检查数据是否足够
    if len(rfm) < 5:
        print("错误: 用户数量太少，无法进行有意义的RFM分析")
        return {
            'error': "用户数量太少，无法进行有意义的RFM分析"
        }
    
    # 数据分布图
    plt.figure(figsize=(18, 6), facecolor='white')
    
    # 绘制Recency分布
    plt.subplot(1, 3, 1)
    sns.histplot(rfm['recency'], kde=True, color='skyblue')
    plt.title('用户购买时间间隔分布', fontproperties=font_prop, fontsize=14)
    plt.xlabel('时间间隔（天）', fontproperties=font_prop, fontsize=12)
    plt.ylabel('用户数量', fontproperties=font_prop, fontsize=12)
    
    # 绘制Frequency分布
    plt.subplot(1, 3, 2)
    sns.histplot(rfm['frequency'], kde=True, color='lightgreen')
    plt.title('用户购买频率分布', fontproperties=font_prop, fontsize=14)
    plt.xlabel('购买次数', fontproperties=font_prop, fontsize=12)
    plt.ylabel('用户数量', fontproperties=font_prop, fontsize=12)
    
    # 绘制Monetary分布
    plt.subplot(1, 3, 3)
    sns.histplot(rfm['monetary'], kde=True, color='salmon')
    plt.title('用户消费金额分布', fontproperties=font_prop, fontsize=14)
    plt.xlabel('消费金额', fontproperties=font_prop, fontsize=12)
    plt.ylabel('用户数量', fontproperties=font_prop, fontsize=12)
    
    plt.tight_layout()
    distribution_image_path = os.path.join(output_dir, 'rfm_distribution.png')
    plt.savefig(distribution_image_path, dpi=300, bbox_inches='tight', format='png')
    plt.close()
    
    # 计算RFM分数
    # 将R、F、M评分划分为1-5分（5分最好）
    rfm['R_score'] = pd.qcut(rfm['recency'], q=5, labels=range(5, 0, -1))
    rfm['F_score'] = pd.qcut(rfm['frequency'].rank(method='first'), q=5, labels=range(1, 6))
    rfm['M_score'] = pd.qcut(rfm['monetary'].rank(method='first'), q=5, labels=range(1, 6))
    
    # 计算总RFM得分
    rfm['RFM_score'] = rfm['R_score'].astype(int) + rfm['F_score'].astype(int) + rfm['M_score'].astype(int)
    
    # 定义客户细分类别
    def segment_customer(row):
        if row['RFM_score'] >= 13:
            return '高价值客户'
        elif (row['RFM_score'] >= 10) and (row['RFM_score'] < 13):
            return '中高价值客户'
        elif (row['RFM_score'] >= 7) and (row['RFM_score'] < 10):
            return '中价值客户'
        elif (row['RFM_score'] >= 4) and (row['RFM_score'] < 7):
            return '低价值客户'
        else:
            return '流失客户'
    
    rfm['customer_segment'] = rfm.apply(segment_customer, axis=1)
    
    # 创建细分饼图
    plt.figure(figsize=(10, 8), facecolor='white')
    segment_counts = rfm['customer_segment'].value_counts()
    colors = ['#ff9999', '#66b3ff', '#99ff99', '#ffcc99', '#c2c2f0']
    
    # 添加百分比和数量标签
    total = len(rfm)
    labels = [f"{segment}: {count} ({count/total*100:.1f}%)" for segment, count in segment_counts.items()]
    
    # 绘制饼图
    plt.pie(segment_counts, colors=colors, labels=labels, autopct='', startangle=90, 
           textprops={'fontproperties': font_prop, 'fontsize': 12})
    
    plt.axis('equal')
    plt.title('客户细分分布', fontproperties=font_prop, fontsize=16)
    
    segment_image_path = os.path.join(output_dir, 'rfm_segments.png')
    plt.savefig(segment_image_path, dpi=300, bbox_inches='tight', format='png')
    plt.close()
    
    # 使用K-Means进行客户聚类 (3D散点图)
    # 标准化RFM值用于聚类
    from sklearn.preprocessing import StandardScaler
    
    scaler = StandardScaler()
    rfm_scaled = scaler.fit_transform(rfm[['recency', 'frequency', 'monetary']])
    
    # 使用肘部法则确定聚类数
    inertia = []
    k_range = range(1, 10)
    for k in k_range:
        kmeans = KMeans(n_clusters=k, random_state=42)
        kmeans.fit(rfm_scaled)
        inertia.append(kmeans.inertia_)
    
    # 绘制肘部图
    plt.figure(figsize=(10, 6), facecolor='white')
    plt.plot(k_range, inertia, 'o-', color='skyblue')
    plt.title('确定最佳聚类数 (肘部法则)', fontproperties=font_prop, fontsize=14)
    plt.xlabel('聚类数量', fontproperties=font_prop, fontsize=12)
    plt.ylabel('组内平方和 (SSE)', fontproperties=font_prop, fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.7)
    
    elbow_image_path = os.path.join(output_dir, 'rfm_elbow.png')
    plt.savefig(elbow_image_path, dpi=300, bbox_inches='tight', format='png')
    plt.close()
    
    # 基于肘部图选择聚类数 (在实际中这应该是动态的，但为了简化，这里使用4)
    optimal_clusters = 4
    kmeans = KMeans(n_clusters=optimal_clusters, random_state=42)
    rfm['cluster'] = kmeans.fit_predict(rfm_scaled)
    
    # 绘制3D散点图
    from mpl_toolkits.mplot3d import Axes3D
    
    fig = plt.figure(figsize=(12, 10), facecolor='white')
    ax = fig.add_subplot(111, projection='3d')
    
    # 为每个聚类设置不同颜色
    colors = ['blue', 'red', 'green', 'orange', 'purple', 'cyan', 'magenta', 'yellow', 'black']
    
    # 绘制散点
    for i in range(optimal_clusters):
        cluster_data = rfm[rfm['cluster'] == i]
        ax.scatter(cluster_data['recency'], 
                  cluster_data['frequency'], 
                  cluster_data['monetary'],
                  s=50, c=colors[i], label=f'聚类 {i+1}')
    
    # 设置轴标签
    ax.set_xlabel('最近一次购买 (天)', fontproperties=font_prop, fontsize=12)
    ax.set_ylabel('购买频率 (次数)', fontproperties=font_prop, fontsize=12)
    ax.set_zlabel('消费总额', fontproperties=font_prop, fontsize=12)
    
    # 添加标题和图例
    ax.set_title('RFM 3D聚类分析', fontproperties=font_prop, fontsize=16)
    plt.legend(prop=font_prop)
    
    cluster_image_path = os.path.join(output_dir, 'rfm_clusters_3d.png')
    plt.savefig(cluster_image_path, dpi=300, bbox_inches='tight', format='png')
    plt.close()
    
    # 计算每个聚类的平均RFM值
    cluster_avg = rfm.groupby('cluster')[['recency', 'frequency', 'monetary']].mean()
    
    # 将聚类与业务含义映射
    # 基于RFM平均值确定每个聚类的业务含义
    
    # 归一化平均值以便比较
    cluster_avg_norm = (cluster_avg - cluster_avg.min()) / (cluster_avg.max() - cluster_avg.min())
    cluster_avg_norm['recency'] = 1 - cluster_avg_norm['recency']  # 反转recency (越小越好)
    
    # 计算总分
    cluster_avg_norm['total_score'] = cluster_avg_norm.sum(axis=1)
    
    # 排序并分配业务标签
    sorted_clusters = cluster_avg_norm.sort_values('total_score', ascending=False)
    business_labels = ['高价值活跃客户', '中价值活跃客户', '低价值客户', '流失风险客户']
    
    # 创建映射
    segment_mapping = {}
    for i, (cluster, _) in enumerate(sorted_clusters.iterrows()):
        if i < len(business_labels):
            segment_mapping[cluster] = business_labels[i]
        else:
            segment_mapping[cluster] = f'聚类 {cluster+1}'
    
    # 应用映射
    rfm['business_segment'] = rfm['cluster'].map(segment_mapping)
    
    # 创建业务细分饼图
    plt.figure(figsize=(10, 8), facecolor='white')
    business_segment_counts = rfm['business_segment'].value_counts()
    colors = ['#ff9999', '#66b3ff', '#99ff99', '#ffcc99']
    
    # 添加百分比和数量标签
    total = len(rfm)
    labels = [f"{segment}: {count} ({count/total*100:.1f}%)" for segment, count in business_segment_counts.items()]
    
    # 绘制饼图
    plt.pie(business_segment_counts, colors=colors, labels=labels, autopct='', startangle=90, 
           textprops={'fontproperties': font_prop, 'fontsize': 12})
    
    plt.axis('equal')
    plt.title('客户业务细分分布', fontproperties=font_prop, fontsize=16)
    
    business_segment_image_path = os.path.join(output_dir, 'rfm_business_segments.png')
    plt.savefig(business_segment_image_path, dpi=300, bbox_inches='tight', format='png')
    plt.close()
    
    # 保存RFM分析结果
    rfm_path = os.path.join(output_dir, 'rfm_results.csv')
    rfm.reset_index().to_csv(rfm_path, index=False)
    
    # 准备聚类特征可视化（雷达图）
    plt.figure(figsize=(10, 8), facecolor='white')
    
    # 准备雷达图数据
    cluster_avg_radar = cluster_avg.copy()
    # 反转recency，使得值越大越好
    max_recency = cluster_avg_radar['recency'].max()
    cluster_avg_radar['recency'] = max_recency - cluster_avg_radar['recency']
    
    # 标准化为0-1范围
    for col in cluster_avg_radar.columns:
        cluster_avg_radar[col] = (cluster_avg_radar[col] - cluster_avg_radar[col].min()) / (cluster_avg_radar[col].max() - cluster_avg_radar[col].min())
    
    # 准备雷达图角度
    categories = ['最近购买', '购买频率', '消费金额']
    N = len(categories)
    angles = [n / float(N) * 2 * np.pi for n in range(N)]
    angles += angles[:1]  # 闭合雷达图
    
    # 创建子图
    ax = plt.subplot(111, polar=True)
    
    # 设置雷达图的角度标签
    plt.xticks(angles[:-1], categories, fontproperties=font_prop, size=12)
    
    # 绘制每个聚类的雷达图
    for i, cluster_id in enumerate(cluster_avg_radar.index):
        values = cluster_avg_radar.loc[cluster_id].values.tolist()
        values += values[:1]  # 闭合雷达图
        ax.plot(angles, values, linewidth=2, label=segment_mapping[cluster_id])
        ax.fill(angles, values, alpha=0.25)
    
    # 添加标题和图例
    plt.title('聚类特征雷达图', fontproperties=font_prop, size=16)
    plt.legend(loc='upper right', bbox_to_anchor=(0.1, 0.1), prop=font_prop)
    
    radar_image_path = os.path.join(output_dir, 'rfm_radar.png')
    plt.savefig(radar_image_path, dpi=300, bbox_inches='tight', format='png')
    plt.close()
    
    # 返回分析结果
    return {
        'rfm_path': rfm_path,
        'distribution_image': distribution_image_path,
        'segment_image': segment_image_path,
        'business_segment_image': business_segment_image_path,
        'cluster_image': cluster_image_path,
        'elbow_image': elbow_image_path,
        'radar_image': radar_image_path,
        'user_count': len(rfm),
        'segments': {
            label: count for label, count in rfm['business_segment'].value_counts().items()
        }
    } 