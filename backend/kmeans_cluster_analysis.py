import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.font_manager as fm
import matplotlib as mpl

# 导入自定义字体模块
from embed_font import setup_chinese_font, get_font_prop

# 使用统一的字体设置
font_prop = setup_chinese_font()

# 定义数据文件路径
file_path = "first_clean_batch_100.csv"

# 读取CSV文件
df = pd.read_csv(file_path)

# 构造年龄段字段
df["年龄段"] = pd.cut(
    df["年龄"],
    bins=[0, 15, 18, 25, 35, 45, 100],
    labels=["0-15", "15-18", "18-25", "26-35", "36-45", "45+"],
    right=False
)

# 构造透视表
pivot = df.pivot_table(
    values="使用频率（次/周）",
    index="职业",
    columns="年龄段",
    aggfunc="mean"
)

# 填补缺失值
pivot = pivot.fillna(np.nan)

# 作图
plt.figure(figsize=(12, 6))
sns.heatmap(pivot, annot=True, fmt=".1f", cmap="YlGnBu")

plt.title("不同职业与年龄段用户的平均使用频率热力图", fontproperties=font_prop)
plt.xlabel("年龄段", fontproperties=font_prop)
plt.ylabel("职业", fontproperties=font_prop)
plt.xticks(fontproperties=font_prop)
plt.yticks(fontproperties=font_prop)
plt.tight_layout()
plt.savefig('heatmap.png', dpi=300, bbox_inches='tight', format='png')
plt.close()
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
import os
import matplotlib as mpl
from matplotlib.font_manager import FontProperties
import io
import base64
from pathlib import Path

# 导入自定义字体模块
from embed_font import setup_chinese_font, get_font_prop

import matplotlib.patches as patches

def perform_kmeans_analysis(data_path, output_dir):
    # 使用统一的字体设置
    font_prop = setup_chinese_font()
    
    print(f"K-means分析使用字体: {plt.rcParams['font.family']}")
    
    # 读取清洗后的数据
    df = pd.read_csv(data_path)
    
    # 指定用于聚类的特征列表 - 与用户代码完全匹配
    target_features = [
        'page_views',
        'add_to_cart',
        'purchase',
        'use_count',
        'days_to_first_use',
        'days_since_last_use'
    ]
    
    # 检查这些特征是否存在于数据集中
    # 如果某些特征不存在，需要在日志中记录并通知用户
    missing_features = [col for col in target_features if col not in df.columns]
    if missing_features:
        print(f"警告: 以下特征在数据集中不存在: {', '.join(missing_features)}")
        # 创建缺失特征并填充0值，确保分析可以继续
        for feature in missing_features:
            df[feature] = 0
    
    # 确保只使用指定的特征进行分析
    X = df[target_features].fillna(0)  # 填充任何缺失值为0
    
    # 打印日志信息，显示使用的特征列
    print(f"使用以下特征进行K-means聚类分析: {target_features}")
    
    # 数据标准化
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # 使用肘部法则确定最佳聚类数
    inertia = []
    K_range = range(1, min(10, len(X_scaled)))
    
    for k in K_range:
        kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)  # 指定n_init=10
        kmeans.fit(X_scaled)
        inertia.append(kmeans.inertia_)
    
    # 定义创建图形的辅助函数
    def create_figure_with_chinese_labels(title, xlabel, ylabel, fig_size=(10, 6)):
        plt.figure(figsize=fig_size, facecolor='white')
        
        # 添加中文标签
        plt.suptitle(title, fontproperties=font_prop, fontsize=16)
        plt.xlabel(xlabel, fontproperties=font_prop, fontsize=14)
        plt.ylabel(ylabel, fontproperties=font_prop, fontsize=14)
    
    # 保存肘部法则图
    create_figure_with_chinese_labels('K-means聚类肘部法则图', '聚类数K', '惯性值 (Inertia)')
    plt.plot(K_range, inertia, 'bo-')
    plt.grid(True)
    plt.xticks(fontsize=12)
    plt.yticks(fontsize=12)
    
    elbow_image_path = os.path.join(output_dir, 'kmeans_elbow.png')
    plt.tight_layout()
    plt.savefig(elbow_image_path, dpi=300, bbox_inches='tight', format='png')
    plt.close()
    
    # 直接使用K=3进行聚类，与用户代码保持一致
    optimal_k = 3
    kmeans = KMeans(n_clusters=optimal_k, random_state=42, n_init=10)
    clusters = kmeans.fit_predict(X_scaled)
    
    # 将聚类结果添加到数据框
    df['cluster'] = clusters
    
    # 使用PCA进行降维，方便可视化
    pca = PCA(n_components=2)
    X_pca = pca.fit_transform(X_scaled)
    
    # 绘制聚类结果 - 按照用户提供的代码逻辑实现
    create_figure_with_chinese_labels('模块3 用户聚类分析结果', '主成分1', '主成分2', fig_size=(8, 6))
    
    # 使用Google风格的配色方案
    # 定义Google风格的配色方案 - 鲜艳且有辨识度的颜色
    google_colors = ['#4285F4', '#DB4437', '#F4B400', '#0F9D58', '#AB47BC', '#00ACC1', '#FF7043', '#9E9E9E']
    
    # 按照用户代码逻辑绘制散点图，但使用Google配色
    for i, c in enumerate(sorted(np.unique(clusters))):
        plt.scatter(
            X_pca[clusters == c, 0],
            X_pca[clusters == c, 1],
            color=google_colors[i % len(google_colors)],  # 使用Google配色
            label=f'Cluster {c}',
            alpha=0.7,  # 添加透明度使图形更美观
            edgecolors='w',  # 添加白色边缘增强可视效果
            s=70  # 稍微增大点的大小
        )
    
    # 添加网格线
    plt.grid(True)
    
    # 添加图例
    plt.legend(prop=font_prop, fontsize=12)
    plt.xticks(fontsize=12)
    plt.yticks(fontsize=12)
    
    # 保存聚类图 - 使用更高的DPI和更好的图像质量
    cluster_image_path = os.path.join(output_dir, 'kmeans_clusters.png')
    plt.tight_layout()
    plt.savefig(cluster_image_path, dpi=300, bbox_inches='tight', format='png')
    plt.close()
    
    # 保存每个聚类的用户数量统计
    cluster_stats = df['cluster'].value_counts().reset_index()
    cluster_stats.columns = ['聚类', '用户数量']
    
    # 计算聚类结果的特征统计信息 - 确保只使用目标特征
    cluster_profiles = df.groupby('cluster')[target_features].mean().reset_index()
    
    # 保存处理后的带聚类标签的数据
    output_data_path = os.path.join(output_dir, 'clustered_data.csv')
    df.to_csv(output_data_path, index=False)
    
    return {
        'elbow_image': elbow_image_path,
        'cluster_image': cluster_image_path,
        'cluster_stats': cluster_stats.to_dict('records'),
        'cluster_profiles': cluster_profiles.to_dict('records'),
        'output_data': output_data_path
    }


# 归一化宽度
max_width = 600

# 计算漏斗阶段的用户数量和转化率
funnel_stages = {
    "页面浏览": df.iloc[:, 1].sum(),
    "加入购物车": df.iloc[:, 2].sum(),
    "提交订单": df.iloc[:, 3].sum(),
    "支付成功": df.iloc[:, 4].sum()
}

stages = list(funnel_stages.keys())
users = list(funnel_stages.values())
conversion_rate = [100 * users[i] / users[0] for i in range(len(users))]

# 归一化用户数
norm_users = [u / max(users) * max_width for u in users]

fig, ax = plt.subplots(figsize=(8, 6))
height = 1.0
gap = 0.3
blue_color = '#4A90E2'  # 柔和蓝色

for i in range(len(stages) - 1):
    top_width = norm_users[i]
    bottom_width = norm_users[i + 1]
    y = -i * (height + gap)
    polygon = patches.Polygon([
        [(max_width - top_width) / 2, y],
        [(max_width + top_width) / 2, y],
        [(max_width + bottom_width) / 2, y - height],
        [(max_width - bottom_width) / 2, y - height]
    ], closed=True, facecolor=blue_color, edgecolor='black')
    ax.add_patch(polygon)
    label = f"{stages[i]}：{users[i]}人（{conversion_rate[i]:.1f}%）"
    ax.text((max_width + top_width) / 2 + 20, y - height / 2,
            label, ha='left', va='center', fontsize=12, fontproperties=font_prop)

# 最后一层（支付成功）封底 + 图例
last_width = norm_users[-1]
y = - (len(stages) - 1) * (height + gap)
polygon = patches.Polygon([
    [(max_width - last_width) / 2, y],
    [(max_width + last_width) / 2, y],
    [(max_width + last_width) / 2, y - height],
    [(max_width - last_width) / 2, y - height]
], closed=True, facecolor=blue_color, edgecolor='black')
ax.add_patch(polygon)
label = f"{stages[-1]}：{users[-1]}人（{conversion_rate[-1]:.1f}%）"
ax.text((max_width + last_width) / 2 + 20, y - height / 2,
        label, ha='left', va='center', fontsize=12, fontproperties=font_prop)

# 配置图像
ax.set_xlim(0, max_width + 250)
ax.set_ylim(-len(stages) * (height + gap) + gap, gap)
ax.axis('off')
plt.title("用户转化漏斗图", fontsize=16, fontproperties=font_prop)
plt.tight_layout()
plt.show()