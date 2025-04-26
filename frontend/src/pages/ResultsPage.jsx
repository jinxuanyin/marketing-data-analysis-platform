import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import AnalysisResult from '../components/AnalysisResult';

const API_URL = 'http://localhost:8000';

const ResultsPage = () => {
  const { sessionId } = useParams();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [results, setResults] = useState(null);

  useEffect(() => {
    const fetchResults = async () => {
      try {
        const response = await axios.get(`${API_URL}/results/${sessionId}`);
        
        if (response.data.status === 'success') {
          // 如果只有图片URL，则需要再获取完整的分析结果
          if (response.data.image_urls && !response.data.kmeans_results) {
            try {
              const detailResponse = await axios.post(`${API_URL}/analyze/${sessionId}`);
              setResults(detailResponse.data);
            } catch (detailErr) {
              // 如果获取详细分析失败，至少显示图片
              setResults(response.data);
            }
          } else {
            setResults(response.data);
          }
        } else if (response.data.status === 'pending') {
          // 如果分析还在进行中，重定向回分析页面
          navigate(`/analysis/${sessionId}`);
        } else {
          // 如果有错误
          setError(response.data.message || '获取分析结果失败');
        }
        
        setLoading(false);
      } catch (err) {
        setError(err.response?.data?.detail || '获取分析结果失败，请重试');
        setLoading(false);
      }
    };

    fetchResults();
  }, [sessionId, navigate]);

  const handleDownloadImage = (imageUrl, imageName) => {
    // 确保图片URL是完整的
    const fullImageUrl = imageUrl.startsWith('http') ? imageUrl : `${API_URL}${imageUrl}`;
    
    // 使用fetch获取图片数据
    fetch(fullImageUrl)
      .then(response => {
        if (!response.ok) {
          throw new Error('图片加载失败');
        }
        return response.blob();
      })
      .then(blob => {
        // 创建一个Blob URL
        const blobUrl = window.URL.createObjectURL(blob);
        
        // 创建一个隐藏的a标签进行下载
        const link = document.createElement('a');
        link.href = blobUrl;
        link.download = imageName || 'analysis_result.png';
        document.body.appendChild(link);
        link.click();
        
        // 完成后清理
        document.body.removeChild(link);
        window.URL.revokeObjectURL(blobUrl);
      })
      .catch(error => {
        console.error('下载图片时出错:', error);
        alert('下载图片失败，请重试');
      });
  };

  const handleNewAnalysis = () => {
    navigate('/');
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-screen -mt-16">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-3xl mx-auto text-center">
        <div className="bg-white p-6 rounded-lg shadow-md">
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
          <h3 className="mt-4 text-lg font-medium text-red-800">获取结果失败</h3>
          <p className="mt-2 text-sm text-gray-600">{error}</p>
          <div className="mt-6">
            <button
              onClick={handleNewAnalysis}
              className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
            >
              开始新的分析
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold text-gray-900">分析结果</h1>
        <div className="flex space-x-4">
          <button
            onClick={handleNewAnalysis}
            className="inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md shadow-sm text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
          >
            开始新的分析
          </button>
          
          {/* 下载按钮组 */}
          <div className="relative inline-block text-left">
            <div className="inline-flex rounded-md shadow-sm">
              <div className="flex space-x-2">
                {results?.image_urls?.kmeans_clusters && (
                  <button
                    type="button"
                    onClick={() => handleDownloadImage(results.image_urls.kmeans_clusters, 'kmeans_clusters.png')}
                    className="inline-flex items-center px-3 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
                  >
                    下载聚类分析
                  </button>
                )}
                
                {results?.image_urls?.kmeans_elbow && (
                  <button
                    type="button"
                    onClick={() => handleDownloadImage(results.image_urls.kmeans_elbow, 'kmeans_elbow.png')}
                    className="inline-flex items-center px-3 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
                  >
                    下载肘部法则图
                  </button>
                )}
                
                {results?.image_urls?.heatmap && (
                  <button
                    type="button"
                    onClick={() => handleDownloadImage(results.image_urls.heatmap, 'user_heatmap.png')}
                    className="inline-flex items-center px-3 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-amber-600 hover:bg-amber-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-amber-500"
                  >
                    下载热力图
                  </button>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>

      <AnalysisResult results={results} />
    </div>
  );
};

export default ResultsPage; 