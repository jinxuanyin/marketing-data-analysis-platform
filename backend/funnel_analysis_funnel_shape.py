import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import sys
from matplotlib.font_manager import FontProperties

# 导入字体处理函数
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from embed_font import download_simsun_font, setup_chinese_font

def generate_funnel(data_path, output_dir):
    # 使用固定的中文字体
    font_path = download_simsun_font()
    
    if font_path and os.path.exists(font_path):
        # 注册字体
        font_prop = FontProperties(fname=font_path)
        plt.rcParams['font.family'] = font_prop.get_name()
    else:
        # 备选方案 - 使用宋体/黑体
        plt.rcParams['font.sans-serif'] = ['SimHei', 'SimSun', 'Microsoft YaHei']
    
    # 禁用负号转换
    plt.rcParams['axes.unicode_minus'] = False
    
    print(f"漏斗图使用字体: {plt.rcParams['font.family']}")
    
    # 读取清洗后的数据
    df = pd.read_csv(data_path)
    
    # 假设数据包含转化流程相关的行为列
    # 典型的转化漏斗包括：浏览->加购物车->下单->支付成功
    # 需要根据实际数据调整以下代码
    
    # 检查常见的转化漏斗相关列名
    funnel_stages = []
    
    # 常见的漏斗阶段名称（按照顺序）
    common_stages = [
        ['view', 'browse', 'visit', 'page_views', '浏览', '访问'], 
        ['cart', 'add_to_cart', 'addCart', '加购', '加入购物车'],
        ['order', 'create_order', 'createOrder', 'purchase', '下单', '订单创建'],
        ['pay', 'payment', 'paySuccess', '支付', '支付成功'],
        ['deliver', 'delivery', 'shipping', '发货', '物流'],
        ['receive', 'received', 'receiving', '收货', '收货确认'],
        ['comment', 'review', 'feedback', '评价', '评论']
    ]
    
    # 查找数据中存在的漏斗阶段
    for stage_synonyms in common_stages:
        found = False
        for synonym in stage_synonyms:
            matching_cols = [col for col in df.columns if synonym.lower() in col.lower()]
            if matching_cols:
                # 找到了匹配的列，使用第一个匹配的列
                funnel_stages.append(matching_cols[0])
                found = True
                break
        
        if found and len(funnel_stages) >= 3:
            # 如果已经找到至少3个阶段，就认为有足够的数据绘制漏斗图
            break
    
    # 如果没有找到典型的漏斗阶段，尝试使用数值型列（假设较大的值表示更早的阶段）
    if len(funnel_stages) < 3:
        # 优先使用K-means中的特征
        target_features = [
            'page_views',
            'add_to_cart',
            'purchase'
        ]
        
        # 检查这些特征是否在数据中
        available_features = [col for col in target_features if col in df.columns]
        if len(available_features) >= 3:
            funnel_stages = available_features[:3]  # 使用前3个特征
        else:
            # 作为备选，使用数值列
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            if len(numeric_cols) >= 3:
                # 获取每列的平均值
                col_means = df[numeric_cols].mean()
                # 按照均值降序排列（假设转化漏斗中，早期阶段的数值更大）
                sorted_cols = col_means.sort_values(ascending=False).index.tolist()
                funnel_stages = sorted_cols[:min(6, len(sorted_cols))]  # 最多取6个阶段
    
    if len(funnel_stages) < 3:
        raise ValueError("无法识别足够的转化漏斗阶段（至少需要3个阶段）")
    
    # 阶段名称优化 - 使用中文显示
    stage_display_names = {
        'page_views': '页面浏览',
        'add_to_cart': '加入购物车',
        'purchase': '购买',
        'use_count': '使用次数',
        'days_to_first_use': '首次使用',
        'days_since_last_use': '最近使用'
    }
    
    # 计算每个阶段的用户数量
    stage_counts = []
    for stage in funnel_stages:
        # 根据列的类型确定计数方式
        if df[stage].dtype == bool:
            # 布尔列，计算True的数量
            count = df[stage].sum()
        elif pd.api.types.is_numeric_dtype(df[stage]):
            # 数值列，计算非零值的数量
            count = (df[stage] > 0).sum()
        else:
            # 其他类型，计算非空值的数量
            count = df[stage].notna().sum()
        
        stage_counts.append(count)
    
    # 计算转化率
    conversion_rates = []
    for i in range(1, len(stage_counts)):
        if stage_counts[i-1] > 0:
            rate = stage_counts[i] / stage_counts[i-1] * 100
        else:
            rate = 0
        conversion_rates.append(f"{rate:.1f}%")
    
    # 绘制漏斗图
    plt.figure(figsize=(12, 8), facecolor='white')
    
    # 设置底部宽度为1，顶部宽度根据数值比例确定
    bottom_width = 0.8
    max_count = max(stage_counts)
    
    # 漏斗图的颜色
    colors = plt.cm.Blues(np.linspace(0.3, 0.9, len(funnel_stages)))
    
    # 画漏斗的梯形
    for i, (count, stage, color) in enumerate(zip(stage_counts, funnel_stages, colors)):
        # 获取阶段的显示名称
        display_name = stage_display_names.get(stage, stage)
        
        # 梯形的上下底宽度
        width_top = bottom_width * (count / max_count)
        width_bottom = bottom_width * (stage_counts[i-1] / max_count if i > 0 else count / max_count)
        
        # 梯形的左右上下四个点坐标
        left_bottom = -width_bottom / 2
        right_bottom = width_bottom / 2
        left_top = -width_top / 2
        right_top = width_top / 2
        
        # y坐标位置（自上而下递减）
        y_bottom = -i
        y_top = -(i + 0.8)
        
        # 绘制梯形
        plt.fill([left_bottom, right_bottom, right_top, left_top], 
                [y_bottom, y_bottom, y_top, y_top], 
                color=color, edgecolor='white', linewidth=2)
        
        # 添加阶段名称和计数 - 使用指定字体
        if font_path:
            plt.text(0, y_bottom - 0.4, f'{display_name}: {count}', 
                    ha='center', va='center', fontsize=14, 
                    fontweight='bold', fontproperties=font_prop)
        else:
            plt.text(0, y_bottom - 0.4, f'{display_name}: {count}', 
                    ha='center', va='center', fontsize=14, fontweight='bold')
        
        # 添加转化率
        if i > 0:
            plt.text(right_bottom + 0.05, (y_bottom + y_top) / 2, 
                    f"↓ {conversion_rates[i-1]}", 
                    ha='left', va='center', fontsize=12, fontweight='bold')
    
    # 添加标题
    if font_path:
        plt.title('用户转化漏斗分析', fontproperties=font_prop, fontsize=16, pad=20)
    else:
        plt.title('用户转化漏斗分析', fontsize=16, pad=20)
    
    plt.axis('off')  # 不显示坐标轴
    plt.tight_layout()
    
    # 保存漏斗图
    funnel_path = os.path.join(output_dir, 'conversion_funnel.png')
    plt.savefig(funnel_path, dpi=300, bbox_inches='tight', format='png')
    plt.close()
    
    # 准备返回的数据 - 使用显示名称
    funnel_data = []
    for i, stage in enumerate(funnel_stages):
        display_name = stage_display_names.get(stage, stage)
        stage_data = {
            'stage': display_name,
            'count': int(stage_counts[i]),
            'conversion_rate': conversion_rates[i-1] if i > 0 else '100%'
        }
        funnel_data.append(stage_data)
    
    return {
        'funnel_image': funnel_path,
        'funnel_data': funnel_data
    }