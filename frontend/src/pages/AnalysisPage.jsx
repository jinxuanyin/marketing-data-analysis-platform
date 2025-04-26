import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';

const API_URL = 'http://localhost:8000';

const AnalysisPage = () => {
  const { sessionId } = useParams();
  const navigate = useNavigate();
  const [analyzing, setAnalyzing] = useState(true);
  const [error, setError] = useState('');
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    const startAnalysis = async () => {
      try {
        // 启动分析过程
        const response = await axios.post(`${API_URL}/analyze/${sessionId}`);
        
        // 分析完成，跳转到结果页面
        navigate(`/results/${sessionId}`);
      } catch (err) {
        setAnalyzing(false);
        setError(err.response?.data?.detail || '分析过程出错，请重试');
      }
    };

    // 模拟进度，实际进度无法获取，这里只是提供视觉反馈
    const progressInterval = setInterval(() => {
      setProgress((prevProgress) => {
        // 模拟进度，最大到95%，实际完成后会跳转
        const newProgress = prevProgress + Math.random() * 3;
        return newProgress > 95 ? 95 : newProgress;
      });
    }, 500);

    startAnalysis();

    return () => {
      clearInterval(progressInterval);
    };
  }, [sessionId, navigate]);

  const handleRetry = () => {
    setAnalyzing(true);
    setError('');
    setProgress(0);
    navigate('/');
  };

  return (
    <div className="max-w-3xl mx-auto">
      <div className="text-center mb-8">
        <h1 className="text-2xl font-bold text-gray-900">数据分析中</h1>
        <p className="mt-2 text-gray-600">
          请耐心等待，系统正在执行以下步骤：
        </p>
      </div>

      {analyzing ? (
        <div className="bg-white p-6 rounded-lg shadow-md">
          <div className="space-y-6">
            <div>
              <div className="flex justify-between mb-1">
                <span className="text-sm font-medium text-primary-700">分析进度</span>
                <span className="text-sm font-medium text-primary-700">{Math.round(progress)}%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2.5">
                <div
                  className="bg-primary-600 h-2.5 rounded-full"
                  style={{ width: `${progress}%` }}
                ></div>
              </div>
            </div>

            <div className="bg-gray-50 p-4 rounded-md">
              <h4 className="text-sm font-medium text-gray-900 mb-2">分析步骤</h4>
              <ul className="space-y-3">
                <li className="flex items-start">
                  <div className={`mt-0.5 h-5 w-5 flex items-center justify-center rounded-full ${
                    progress > 10 ? 'bg-green-500' : 'bg-gray-300'
                  }`}>
                    <span className="text-white text-xs">{progress > 10 ? '✓' : '1'}</span>
                  </div>
                  <span className="ml-2 text-sm text-gray-700">数据清洗：识别并移除标记为"脏数据"的行，准备分析数据集</span>
                </li>
                <li className="flex items-start">
                  <div className={`mt-0.5 h-5 w-5 flex items-center justify-center rounded-full ${
                    progress > 40 ? 'bg-green-500' : 'bg-gray-300'
                  }`}>
                    <span className="text-white text-xs">{progress > 40 ? '✓' : '2'}</span>
                  </div>
                  <span className="ml-2 text-sm text-gray-700">K-means聚类分析：对用户进行分群并生成可视化结果</span>
                </li>
                <li className="flex items-start">
                  <div className={`mt-0.5 h-5 w-5 flex items-center justify-center rounded-full ${
                    progress > 70 ? 'bg-green-500' : 'bg-gray-300'
                  }`}>
                    <span className="text-white text-xs">{progress > 70 ? '✓' : '3'}</span>
                  </div>
                  <span className="ml-2 text-sm text-gray-700">用户行为热力图：生成交互式热力图展示用户行为模式</span>
                </li>
                <li className="flex items-start">
                  <div className={`mt-0.5 h-5 w-5 flex items-center justify-center rounded-full ${
                    progress > 90 ? 'bg-green-500' : 'bg-gray-300'
                  }`}>
                    <span className="text-white text-xs">{progress > 90 ? '✓' : '4'}</span>
                  </div>
                  <span className="ml-2 text-sm text-gray-700">转化漏斗分析：计算转化路径和各阶段转化率</span>
                </li>
              </ul>
            </div>

            <p className="text-sm text-gray-600 text-center italic">
              分析过程通常需要10-30秒，具体时间取决于数据量大小
            </p>
          </div>
        </div>
      ) : (
        <div className="bg-white p-6 rounded-lg shadow-md text-center">
          <div className="rounded-full bg-red-100 p-3 mx-auto w-16 h-16 flex items-center justify-center">
            <svg
              className="h-8 w-8 text-red-600"
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
              />
            </svg>
          </div>
          <h3 className="mt-4 text-lg font-medium text-red-800">分析失败</h3>
          <p className="mt-2 text-sm text-gray-600">{error}</p>
          <div className="mt-6">
            <button
              onClick={handleRetry}
              className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
            >
              返回重试
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default AnalysisPage; 