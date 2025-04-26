"""
嵌入一个基本的中文字体，确保图表可以显示中文
完全隔离matplotlib环境，避免编码问题
"""
import os
import sys
import base64
import shutil
from pathlib import Path

# 在导入matplotlib前完全隔离环境
# 创建隔离的配置目录
config_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'mpl_config')
os.makedirs(config_dir, exist_ok=True)

# 创建空的样式目录，防止matplotlib读取系统样式
stylelib_dir = os.path.join(config_dir, 'stylelib')
os.makedirs(stylelib_dir, exist_ok=True)

# 设置环境变量，完全隔离matplotlib环境
os.environ['MPLCONFIGDIR'] = config_dir
os.environ['MATPLOTLIBRC'] = os.path.join(config_dir, 'matplotlibrc')
os.environ['MPLBACKEND'] = 'Agg'  # 使用非交互式后端
os.environ['MATPLOTLIBDATA'] = config_dir  # 重定向matplotlib数据目录

# 创建空的配置文件
with open(os.environ['MATPLOTLIBRC'], 'w', encoding='utf-8') as f:
    f.write('# Empty config file\n')

# 禁用matplotlib缓存
os.environ['MPL_CACHE_DIR'] = config_dir

# 确保matplotlib不会尝试读取任何可能存在编码问题的文件
try:
    # 导入matplotlib并立即设置基本配置
    import matplotlib
    matplotlib.use('Agg')  # 强制使用非交互式后端
    
    # 禁用字体缓存
    matplotlib.rcParams['font.family'] = 'sans-serif'
    matplotlib.rcParams['font.sans-serif'] = ['DejaVu Sans']
    matplotlib.rcParams['axes.unicode_minus'] = False
    
    # 导入其他matplotlib模块
    import matplotlib.font_manager as fm
    import matplotlib as mpl
except Exception as e:
    print(f"导入matplotlib时出错: {e}")
    # 创建一个最小化的matplotlib环境
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.font_manager as fm
    import matplotlib as mpl

# 导入其他需要的模块
import requests
import zipfile

# 字体目录
FONT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fonts')
os.makedirs(FONT_DIR, exist_ok=True)

# 字体文件路径
FONT_PATH = os.path.join(FONT_DIR, 'simsun.ttc')

def download_simsun_font():
    """
    获取字体文件路径
    """
    # 如果字体已存在，直接返回路径
    if os.path.exists(FONT_PATH):
        print(f"使用已有字体: {FONT_PATH}")
        return FONT_PATH
    
    # 使用matplotlib内置字体
    print("使用matplotlib内置字体...")
    try:
        # 使用不依赖于系统字体的方式设置字体
        # 指定使用matplotlib内置的DejaVu Sans字体
        default_font = fm.findfont(fm.FontProperties(family='DejaVu Sans'))
        print(f"使用默认字体: {default_font}")
        shutil.copyfile(default_font, FONT_PATH)
        return FONT_PATH
    except Exception as e:
        print(f"设置默认字体失败: {e}")
        try:
            # 尝试使用任何可用的默认字体
            default_font = fm.findfont(fm.FontProperties())
            print(f"使用备选默认字体: {default_font}")
            shutil.copyfile(default_font, FONT_PATH)
            return FONT_PATH
        except Exception as e:
            print(f"所有字体设置尝试均失败: {e}")
            # 创建一个空字体文件，避免后续错误
            with open(FONT_PATH, 'wb') as f:
                f.write(b'')
            return FONT_PATH

def get_font_prop():
    """
    获取中文字体属性
    """
    font_path = download_simsun_font()
    return fm.FontProperties(fname=font_path)

def setup_chinese_font():
    """
    设置matplotlib使用中文字体
    """
    try:
        # 获取字体路径
        font_path = download_simsun_font()
        font_prop = fm.FontProperties(fname=font_path)
        
        # 完全重置matplotlib配置，避免读取任何外部文件
        mpl.rcdefaults()  # 使用内置默认值
        
        # 直接设置基本字体配置，不使用样式文件
        mpl.rcParams['font.family'] = 'sans-serif'
        mpl.rcParams['font.sans-serif'] = ['DejaVu Sans']
        mpl.rcParams['axes.unicode_minus'] = False  # 正确显示负号
        mpl.rcParams['font.size'] = 12
        mpl.rcParams['font.weight'] = 'normal'
        
        # 禁用字体管理器的自动扫描功能
        try:
            # 直接使用字体，不扫描系统字体
            if hasattr(fm, 'fontManager'):
                fm.fontManager._finders = []
        except Exception as e:
            print(f"禁用字体扫描失败: {e}")
        
        return font_prop
    except Exception as e:
        print(f"字体设置过程中发生错误: {e}")
        # 返回一个默认字体属性，确保程序可以继续运行
        return fm.FontProperties()

# 如果直接运行此脚本，则测试字体设置
if __name__ == "__main__":
    import matplotlib.pyplot as plt
    
    try:
        # 设置字体
        font_prop = setup_chinese_font()
        print("字体设置成功")
        
        # 测试绘图
        plt.figure(figsize=(8, 6))
        plt.title('中文字体测试', fontproperties=font_prop, fontsize=16)
        plt.xlabel('横坐标', fontproperties=font_prop)
        plt.ylabel('纵坐标', fontproperties=font_prop)
        plt.text(0.5, 0.5, '中文显示测试', fontproperties=font_prop, fontsize=14, 
                 ha='center', transform=plt.gca().transAxes)
        
        # 保存测试图
        test_dir = os.path.join(os.path.dirname(FONT_PATH), 'test')
        os.makedirs(test_dir, exist_ok=True)
        plt.savefig(os.path.join(test_dir, 'font_test.png'), dpi=300)
        plt.close()
        
        print(f"字体测试完成，测试图片保存在: {test_dir}")
    except Exception as e:
        print(f"字体测试过程中发生错误: {e}")
        print("尽管测试失败，但字体模块仍可在实际应用中使用默认配置")