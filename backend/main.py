import os
import shutil
import sys

# 在导入任何使用matplotlib的模块前设置环境变量
# 创建隔离的配置目录
config_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'mpl_config')
os.makedirs(config_dir, exist_ok=True)

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

# 导入并应用matplotlib补丁，修复编码问题
from matplotlib_patch import apply_patch
apply_patch()

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uuid
from typing import List, Dict, Any
import uvicorn

# 导入我们的分析脚本
from clean_data import clean_data
from kmeans_cluster_analysis import perform_kmeans_analysis
from draw_heatmap import generate_heatmap
from funnel_analysis_funnel_shape import generate_funnel

app = FastAPI(title="营销大数据分析平台")

# 设置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有源，生产环境应该指定具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 创建必要的文件夹
os.makedirs("uploads", exist_ok=True)
os.makedirs("results", exist_ok=True)

# 挂载静态文件目录，使得图片可以通过URL访问
app.mount("/static", StaticFiles(directory="results"), name="static")

@app.get("/")
def read_root():
    return {"message": "欢迎使用营销大数据分析平台API"}

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    # 检查文件类型
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="只接受CSV文件")
    
    # 创建唯一的会话ID，用于跟踪分析过程
    session_id = str(uuid.uuid4())
    session_dir = os.path.join("results", session_id)
    os.makedirs(session_dir, exist_ok=True)
    
    # 保存上传的文件
    file_path = os.path.join("uploads", f"{session_id}_{file.filename}")
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    return {
        "session_id": session_id,
        "filename": file.filename,
        "message": "文件上传成功，可以开始数据分析"
    }

@app.post("/analyze/{session_id}")
async def analyze_data(session_id: str):
    # 验证会话存在
    session_dir = os.path.join("results", session_id)
    if not os.path.exists(session_dir):
        raise HTTPException(status_code=404, detail="会话不存在，请先上传文件")
    
    # 查找该会话关联的文件
    uploaded_files = [f for f in os.listdir("uploads") if f.startswith(session_id)]
    if not uploaded_files:
        raise HTTPException(status_code=404, detail="未找到相关文件，请重新上传")
    
    file_path = os.path.join("uploads", uploaded_files[0])
    
    try:
        # 步骤1: 数据清洗
        cleaned_data_path = os.path.join(session_dir, "cleaned_data.csv")
        cleaning_stats = clean_data(file_path, cleaned_data_path)
        
        # 保存清洗统计信息到文件
        cleaning_stats_path = os.path.join(session_dir, "cleaning_stats.json")
        with open(cleaning_stats_path, "w") as f:
            import json
            json.dump(cleaning_stats, f, indent=2)
        
        # 步骤2: K-means聚类分析
        kmeans_results = perform_kmeans_analysis(cleaned_data_path, session_dir)
        
        # 步骤3: 生成热力图
        heatmap_results = generate_heatmap(cleaned_data_path, session_dir)
        
        # 步骤4: 生成漏斗图
        funnel_results = generate_funnel(cleaned_data_path, session_dir)
        
        # 处理图片路径，将其转换为可访问的URL
        image_urls = {
            'kmeans_elbow': f"/static/{session_id}/{os.path.basename(kmeans_results['elbow_image'])}",
            'kmeans_clusters': f"/static/{session_id}/{os.path.basename(kmeans_results['cluster_image'])}",
            'heatmap': f"/static/{session_id}/{os.path.basename(heatmap_results['heatmap_image'])}",
            'funnel': f"/static/{session_id}/{os.path.basename(funnel_results['funnel_image'])}"
        }
        
        # 返回分析结果和图像URL
        return {
            "session_id": session_id,
            "status": "success",
            "image_urls": image_urls,
            "cleaning_stats": cleaning_stats,
            "kmeans_results": {
                "cluster_stats": kmeans_results["cluster_stats"],
                "cluster_profiles": kmeans_results["cluster_profiles"]
            },
            "heatmap_results": {
                "behavior_stats": heatmap_results["behavior_stats"],
                "top_behaviors": heatmap_results["top_behaviors"]
            },
            "funnel_results": {
                "funnel_data": funnel_results["funnel_data"]
            }
        }
    
    except Exception as e:
        # 记录错误
        error_file = os.path.join(session_dir, "error_log.txt")
        with open(error_file, "w") as f:
            f.write(str(e))
        
        raise HTTPException(status_code=500, detail=f"分析过程中出错: {str(e)}")

@app.get("/results/{session_id}")
def get_results(session_id: str):
    # 获取已完成分析的结果
    session_dir = os.path.join("results", session_id)
    if not os.path.exists(session_dir):
        raise HTTPException(status_code=404, detail="未找到该会话的分析结果")
    
    # 检查是否有错误日志
    error_file = os.path.join(session_dir, "error_log.txt")
    if os.path.exists(error_file):
        with open(error_file, "r") as f:
            error_message = f.read()
        return {"status": "error", "message": error_message}
    
    # 获取所有生成的图片
    image_files = [f for f in os.listdir(session_dir) if f.endswith(('.png', '.jpg', '.jpeg'))]
    
    if not image_files:
        return {"status": "pending", "message": "分析尚未完成或未生成图片"}
    
    # 构建图片URL
    image_urls = {
        os.path.splitext(img)[0]: f"/static/{session_id}/{img}" 
        for img in image_files
    }
    
    return {
        "status": "success",
        "session_id": session_id,
        "image_urls": image_urls
    }

@app.get("/download/{session_id}/{file_name}")
def download_file(session_id: str, file_name: str):
    # 提供下载分析结果的功能
    file_path = os.path.join("results", session_id, file_name)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="文件不存在")
    
    return FileResponse(
        path=file_path, 
        filename=file_name,
        media_type='application/octet-stream'
    )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)