"""修复matplotlib编码问题的补丁"""
import os
import sys
import importlib
import codecs

def apply_patch():
    """应用补丁，修复matplotlib的编码问题"""
    try:
        # 导入matplotlib
        import matplotlib
        
        # 强制使用Agg后端
        matplotlib.use('Agg')
        
        # 直接修补matplotlib的_rc_params_in_file函数，这是导致编码错误的根源
        original_rc_params_in_file = matplotlib._rc_params_in_file
        
        def safe_rc_params_in_file(fname, fail_on_error=False):
            """安全的读取配置文件函数，避免编码错误"""
            try:
                # 尝试使用原始函数
                return original_rc_params_in_file(fname, fail_on_error)
            except UnicodeDecodeError:
                # 如果遇到编码错误，使用latin-1编码重试
                print(f"警告: 读取配置文件时遇到编码错误: {fname}，尝试使用latin-1编码")
                config = {}
                try:
                    with codecs.open(fname, encoding='latin-1') as fd:
                        for line_no, line in enumerate(fd, 1):
                            line = line.strip()
                            if not line or line.startswith('#'):
                                continue
                            key, val = [s.strip() for s in line.split(':', 1)]
                            config[key] = val
                    return config
                except Exception as e:
                    print(f"警告: 使用latin-1编码读取配置文件时出错: {e}，返回空配置")
                    return {}
            except Exception as e:
                print(f"警告: 读取配置文件时出错: {e}，返回空配置")
                return {}
        
        # 替换原始函数
        matplotlib._rc_params_in_file = safe_rc_params_in_file
        
        # 修补matplotlib的style模块
        import matplotlib.style.core as style_core
        
        # 保存原始函数
        original_read_style_directory = style_core.read_style_directory
        
        # 创建一个安全的替代函数
        def safe_read_style_directory(style_dir):
            """安全的读取样式目录函数，避免编码错误"""
            try:
                return original_read_style_directory(style_dir)
            except UnicodeDecodeError:
                print(f"警告: 读取样式目录时遇到编码错误: {style_dir}，返回空样式")
                return {}
            except Exception as e:
                print(f"警告: 读取样式目录时出错: {e}，返回空样式")
                return {}
        
        # 替换原始函数
        style_core.read_style_directory = safe_read_style_directory
        
        # 重新加载matplotlib.style模块
        importlib.reload(matplotlib.style)
        
        print("已成功应用matplotlib补丁，修复编码问题")
        return True
    except Exception as e:
        print(f"应用matplotlib补丁时出错: {e}")
        return False

# 如果直接运行此脚本，则应用补丁
if __name__ == "__main__":
    apply_patch()