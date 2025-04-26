import React, { useState } from 'react';

const API_URL = 'http://localhost:8000';

// 图片放大Modal组件
const ImageModal = ({ imageUrl, altText, onClose }) => {
  return (
    <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50" onClick={onClose}>
      <div className="relative max-w-4xl max-h-screen p-4">
        <button 
          onClick={onClose}
          className="absolute top-2 right-2 bg-white rounded-full p-2 text-gray-800 hover:text-gray-600 focus:outline-none"
        >
          <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
        <img 
          src={imageUrl} 
          alt={altText} 
          className="max-w-full max-h-[90vh] object-contain"
          onClick={(e) => e.stopPropagation()}
        />
      </div>
    </div>
  );
};

const AnalysisResult = ({ results }) => {
  const [imageErrors, setImageErrors] = useState({});
  const [imageLoading, setImageLoading] = useState({});
  const [modalImage, setModalImage] = useState(null);
  
  if (!results) {
    return null;
  }

  const { image_urls, cleaning_stats, kmeans_results, heatmap_results, funnel_results } = results;
  
  // 图片加载处理
  const handleImageLoad = (imageId) => {
    setImageLoading(prev => ({...prev, [imageId]: false}));
  };
  
  // 图片加载错误处理
  const handleImageError = (imageId, url) => {
    console.error(`图像加载失败: ${imageId}, URL: ${url}`);
    setImageErrors(prev => ({...prev, [imageId]: true}));
    setImageLoading(prev => ({...prev, [imageId]: false}));
  };
  
  // 开始加载图片
  const startLoading = (imageId) => {
    setImageLoading(prev => ({...prev, [imageId]: true}));
  };
  
  // 图片下载处理函数
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

  // 打开图片Modal
  const openImageModal = (imageUrl, altText) => {
    const fullImageUrl = imageUrl.startsWith('http') ? imageUrl : `${API_URL}${imageUrl}`;
    setModalImage({ url: fullImageUrl, alt: altText });
  };

  // 关闭图片Modal
  const closeImageModal = () => {
    setModalImage(null);
  };

  // 创建图像元素
  const renderImage = (imageUrl, altText, imageId, downloadName) => {
    const fullImageUrl = `${API_URL}${imageUrl}`;
    
    // 第一次渲染时开始加载
    if (imageLoading[imageId] === undefined) {
      startLoading(imageId);
    }
    
    return (
      <div className="relative border rounded-lg overflow-hidden">
        {imageLoading[imageId] && (
          <div className="absolute inset-0 flex items-center justify-center bg-gray-100 bg-opacity-75">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
          </div>
        )}
        
        {imageErrors[imageId] ? (
          <div className="flex flex-col items-center justify-center p-8 bg-gray-50 text-gray-500">
            <svg xmlns="http://www.w3.org/2000/svg" className="h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
            <p className="mt-2">图像加载失败</p>
            <p className="text-xs mt-1">{fullImageUrl}</p>
            <button 
              onClick={() => {
                setImageErrors(prev => ({...prev, [imageId]: false}));
                startLoading(imageId);
              }}
              className="mt-4 px-4 py-2 text-sm text-blue-600 hover:text-blue-800 underline"
            >
              重试
            </button>
          </div>
        ) : (
          <img 
            src={fullImageUrl}
            alt={altText} 
            className="w-full h-auto cursor-pointer hover:opacity-90 transition-opacity"
            onLoad={() => handleImageLoad(imageId)}
            onError={() => handleImageError(imageId, fullImageUrl)}
            onClick={() => openImageModal(imageUrl, altText)}
          />
        )}
      </div>
    );
  };

  return (
    <div className="space-y-8">
      <h2 className="text-2xl font-bold text-gray-900">分析结果</h2>

      {/* 数据清洗统计信息 */}
      {cleaning_stats && (
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-xl font-semibold text-gray-900 mb-4">数据清洗统计</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="bg-blue-50 p-4 rounded-lg">
              <p className="text-sm text-gray-500">原始数据行数</p>
              <p className="text-xl font-semibold text-blue-700">{cleaning_stats.original_rows}</p>
            </div>
            <div className="bg-green-50 p-4 rounded-lg">
              <p className="text-sm text-gray-500">清洗后行数</p>
              <p className="text-xl font-semibold text-green-700">{cleaning_stats.cleaned_rows}</p>
            </div>
            <div className="bg-red-50 p-4 rounded-lg">
              <p className="text-sm text-gray-500">删除的行数</p>
              <p className="text-xl font-semibold text-red-700">{cleaning_stats.removed_rows}</p>
            </div>
            <div className="bg-purple-50 p-4 rounded-lg">
              <p className="text-sm text-gray-500">保留数据百分比</p>
              <p className="text-xl font-semibold text-purple-700">{cleaning_stats.percent_kept}%</p>
            </div>
          </div>
        </div>
      )}

      {/* K-means聚类分析结果 */}
      <div className="bg-white p-6 rounded-lg shadow">
        <h3 className="text-xl font-semibold text-gray-900 mb-4">K-means用户聚类分析</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* 肘部法则图 */}
          {image_urls?.kmeans_elbow && (
            <div>
              <div className="flex justify-between items-center mb-2">
                <h4 className="text-lg font-medium text-gray-700">聚类K值选择 (肘部法则)</h4>
                <button 
                  onClick={() => handleDownloadImage(image_urls.kmeans_elbow, 'kmeans_elbow.png')}
                  className="text-sm text-blue-600 hover:text-blue-800 flex items-center"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                  </svg>
                  下载
                </button>
              </div>
              {renderImage(image_urls.kmeans_elbow, "K-means肘部法则图", "elbow", "kmeans_elbow.png")}
            </div>
          )}
          
          {/* 聚类结果图 */}
          {image_urls?.kmeans_clusters && (
            <div>
              <div className="flex justify-between items-center mb-2">
                <h4 className="text-lg font-medium text-gray-700">用户聚类结果</h4>
                <button 
                  onClick={() => handleDownloadImage(image_urls.kmeans_clusters, 'kmeans_clusters.png')}
                  className="text-sm text-blue-600 hover:text-blue-800 flex items-center"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                  </svg>
                  下载
                </button>
              </div>
              {renderImage(image_urls.kmeans_clusters, "用户聚类结果图", "clusters", "kmeans_clusters.png")}
            </div>
          )}
        </div>
        
        {/* 聚类统计信息 */}
        {kmeans_results?.cluster_stats && kmeans_results.cluster_stats.length > 0 && (
          <div className="mt-6">
            <h4 className="text-lg font-medium text-gray-700 mb-2">聚类统计信息</h4>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      聚类
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      用户数量
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      百分比
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {kmeans_results.cluster_stats.map((cluster, index) => (
                    <tr key={index}>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                        聚类 {cluster.聚类 + 1}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {cluster.用户数量}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {((cluster.用户数量 / kmeans_results.cluster_stats.reduce((sum, c) => sum + c.用户数量, 0)) * 100).toFixed(2)}%
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>

      {/* 用户行为热力图 */}
      <div className="bg-white p-6 rounded-lg shadow">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-xl font-semibold text-gray-900">用户行为指标热力图</h3>
          {image_urls?.heatmap && (
            <button 
              onClick={() => handleDownloadImage(image_urls.heatmap, 'user_behavior_heatmap.png')}
              className="text-sm text-blue-600 hover:text-blue-800 flex items-center"
            >
              <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
              </svg>
              下载热力图
            </button>
          )}
        </div>
        
        {image_urls?.heatmap && (
          renderImage(image_urls.heatmap, "用户行为热力图", "heatmap", "user_behavior_heatmap.png")
        )}
        
        {/* 行为统计 */}
        {heatmap_results?.top_behaviors && heatmap_results.top_behaviors.length > 0 && (
          <div className="mt-6">
            <h4 className="text-lg font-medium text-gray-700 mb-2">行为指标统计</h4>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      行为指标
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      平均值
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      最大值
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {heatmap_results.top_behaviors.map((behavior, index) => (
                    <tr key={index}>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                        {behavior.行为}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {Number(behavior.均值).toFixed(2)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {behavior.最大值}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>

      {/* 用户转化漏斗图 */}
      {image_urls?.funnel && (
      <div className="bg-white p-6 rounded-lg shadow">
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-xl font-semibold text-gray-900">用户转化漏斗分析</h3>
            <button 
              onClick={() => handleDownloadImage(image_urls.funnel, 'user_funnel.png')}
              className="text-sm text-blue-600 hover:text-blue-800 flex items-center"
            >
              <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
              </svg>
              下载漏斗图
            </button>
          </div>
          
          {renderImage(image_urls.funnel, "用户转化漏斗图", "funnel", "user_funnel.png")}
        
        {/* 漏斗数据 */}
        {funnel_results?.funnel_data && funnel_results.funnel_data.length > 0 && (
          <div className="mt-6">
            <h4 className="text-lg font-medium text-gray-700 mb-2">转化阶段明细</h4>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      阶段
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      用户数
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      转化率
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {funnel_results.funnel_data.map((stage, index) => (
                    <tr key={index}>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                        {stage.stage}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {stage.count}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {stage.conversion_rate}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>
      )}

      {/* 图片放大的Modal */}
      {modalImage && (
        <ImageModal 
          imageUrl={modalImage.url} 
          altText={modalImage.alt} 
          onClose={closeImageModal} 
        />
      )}
    </div>
  );
};

export default AnalysisResult; 