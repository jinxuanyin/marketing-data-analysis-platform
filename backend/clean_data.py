import pandas as pd
import os

def clean_data(input_file_path, output_file_path):
    """
    根据用户提供的代码执行数据清洗操作
    
    Args:
        input_file_path: 输入文件路径
        output_file_path: 输出文件路径
    
    Returns:
        dict: 包含清洗统计信息的字典
    """
    # 1️⃣ 读取数据
    print(f"正在读取文件: {input_file_path}")
    df = pd.read_csv(input_file_path)
    
    # 2️⃣ 记录原始数据情况
    original_rows = len(df)
    print(f"原始数据总行数：{original_rows}")
    
    # 检查是否存在"是否脏数据"列
    if '是否脏数据' in df.columns:
        dirty_rows = df[df['是否脏数据'] == '是'].shape[0]
        print(f"脏数据标记为'是'的行数：{dirty_rows}")
        
        # 3️⃣ 清洗数据：删除标记为"是"的脏数据
        df_cleaned = df[df['是否脏数据'] != '是'].copy()
        
        # 4️⃣ 删除"是否脏数据"辅助列
        df_cleaned.drop(columns=['是否脏数据'], inplace=True)
    else:
        print("未找到'是否脏数据'列，将检查空值和异常值进行基本清洗")
        # 执行基本清洗 - 删除所有列均为空的行
        df_cleaned = df.dropna(how='all').copy()
        
        # 对于数值列，将异常值（超过3个标准差）替换为平均值
        numeric_cols = df.select_dtypes(include=['number']).columns
        for col in numeric_cols:
            mean_val = df[col].mean()
            std_val = df[col].std()
            # 识别异常值
            outliers = (df[col] > mean_val + 3*std_val) | (df[col] < mean_val - 3*std_val)
            # 替换异常值
            df_cleaned.loc[outliers, col] = mean_val
    
    # 5️⃣ 保存清洗后的数据
    # 确保输出目录存在
    os.makedirs(os.path.dirname(output_file_path), exist_ok=True)
    df_cleaned.to_csv(output_file_path, index=False)
    
    # 打印清洗结果
    cleaned_rows = len(df_cleaned)
    print(f"✅ 清洗完成，结果已保存为：{output_file_path}")
    print(f"清洗后总行数：{cleaned_rows}")
    
    # 返回清洗统计信息
    stats = {
        "original_rows": original_rows,
        "cleaned_rows": cleaned_rows,
        "removed_rows": original_rows - cleaned_rows,
        "percent_kept": round((cleaned_rows / original_rows) * 100, 2) if original_rows > 0 else 0
    }
    
    return stats 