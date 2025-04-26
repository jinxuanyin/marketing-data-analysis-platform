import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
import sys
from matplotlib.font_manager import FontProperties

# 导入字体处理函数
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from embed_font import download_simsun_font, setup_chinese_font

def generate_heatmap(data_path, output_dir):
    # 使用统一的字体设置
    font_prop = setup_chinese_font()
    
    print(f"热力图使用字体: {plt.rcParams['font.family']}")
    
    # 读取清洗后的数据
    df = pd.read_csv(data_path)

    # 检查必要的列是否存在
    required_columns = ['年龄', '职业', '使用频率（次/周）']
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        print(f"错误: 热力图分析缺少必要列: {', '.join(missing_columns)}")
        return {
            'error': f"缺少必要列: {', '.join(missing_columns)}"
        }

    # 构造年龄段字段
    try:
        df["年龄段"] = pd.cut(
            df["年龄"],
            bins=[0, 15, 18, 25, 35, 45, 100],
            labels=["0-15", "15-18", "18-25", "26-35", "36-45", "45+"],
            right=False
        )
    except Exception as e:
        print(f"错误: 构造年龄段时出错: {e}")
        return {
            'error': f"构造年龄段时出错: {e}"
        }

    # 构造透视表
    try:
        pivot = df.pivot_table(
            values="使用频率（次/周）",
            index="职业",
            columns="年龄段",
            aggfunc="mean"
        )
    except Exception as e:
        print(f"错误: 创建透视表时出错: {e}")
        return {
            'error': f"创建透视表时出错: {e}"
        }

    # 填补缺失值 (保持 NaN)
    pivot = pivot.fillna(np.nan)

    # 作图
    plt.figure(figsize=(12, 6), facecolor='white')
    
    # 使用用户指定的 YlGnBu 配色方案
    sns.heatmap(pivot, annot=True, fmt=".1f", cmap="YlGnBu", linewidths=.5)
    
    plt.title("不同职业与年龄段用户的平均使用频率热力图", fontproperties=font_prop, fontsize=16)
    plt.xlabel("年龄段", fontproperties=font_prop, fontsize=14)
    plt.ylabel("职业", fontproperties=font_prop, fontsize=14)
    plt.xticks(fontproperties=font_prop, rotation=0, fontsize=12) # 保持标签水平
    plt.yticks(fontproperties=font_prop, fontsize=12)
    
    # 保存热力图
    heatmap_path = os.path.join(output_dir, 'user_behavior_heatmap.png')
    plt.tight_layout()
    plt.savefig(heatmap_path, dpi=300, bbox_inches='tight', format='png')
    plt.close()

    # 返回结果（可以根据需要添加统计信息）
    return {
        'heatmap_image': heatmap_path,
        # 可以选择性地返回透视表数据或其他统计信息
        # 'pivot_table': pivot.reset_index().to_dict('records')
    }