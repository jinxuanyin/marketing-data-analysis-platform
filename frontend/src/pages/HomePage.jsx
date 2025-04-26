import React from 'react';
import FileUploader from '../components/FileUploader';

const HomePage = () => {
  return (
    <div>
      <div className="text-center mb-8">
        <h1 className="text-3xl font-extrabold text-gray-900 sm:text-4xl">
          营销大数据分析平台
        </h1>
        <p className="mt-3 max-w-2xl mx-auto text-xl text-gray-500 sm:mt-4">
          上传您的用户行为数据，获取专业的数据分析和可视化结果
        </p>
      </div>

      <div className="max-w-3xl mx-auto">
        <FileUploader />
      </div>

      <div className="mt-12 max-w-4xl mx-auto">
        <h2 className="text-2xl font-bold text-gray-900 mb-4">平台功能</h2>
        
        <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-2">
          <div className="bg-white overflow-hidden shadow rounded-lg">
            <div className="px-4 py-5 sm:p-6">
              <h3 className="text-lg font-medium text-gray-900">数据清洗</h3>
              <p className="mt-2 text-sm text-gray-500">
                自动检测并清理CSV文件中的脏数据、缺失值、异常值，保证分析准确性。
              </p>
            </div>
          </div>

          <div className="bg-white overflow-hidden shadow rounded-lg">
            <div className="px-4 py-5 sm:p-6">
              <h3 className="text-lg font-medium text-gray-900">K-means用户聚类</h3>
              <p className="mt-2 text-sm text-gray-500">
                使用K-means算法对用户进行精准分群，发现不同类型用户的特征和行为模式。
              </p>
            </div>
          </div>

          <div className="bg-white overflow-hidden shadow rounded-lg">
            <div className="px-4 py-5 sm:p-6">
              <h3 className="text-lg font-medium text-gray-900">用户行为热力图</h3>
              <p className="mt-2 text-sm text-gray-500">
                生成直观的用户行为热力图，快速识别高频行为和关键用户，辅助决策。
              </p>
            </div>
          </div>

          <div className="bg-white overflow-hidden shadow rounded-lg">
            <div className="px-4 py-5 sm:p-6">
              <h3 className="text-lg font-medium text-gray-900">用户转化漏斗分析</h3>
              <p className="mt-2 text-sm text-gray-500">
                自动识别用户转化路径，展示各阶段转化率，发现流失节点，优化用户体验。
              </p>
            </div>
          </div>
        </div>
      </div>

      <div className="mt-12 max-w-4xl mx-auto">
        <h2 className="text-2xl font-bold text-gray-900 mb-4">使用说明</h2>
        <div className="bg-white shadow overflow-hidden sm:rounded-md">
          <ul className="divide-y divide-gray-200">
            <li>
              <div className="px-4 py-4 sm:px-6">
                <div className="flex items-center">
                  <div className="flex-shrink-0 bg-primary-500 rounded-full p-1">
                    <span className="text-white text-xs font-medium">1</span>
                  </div>
                  <p className="ml-3 text-sm text-gray-700">
                    准备CSV格式的用户行为数据文件，确保包含"是否脏数据"列用于自动清洗。
                  </p>
                </div>
              </div>
            </li>
            <li>
              <div className="px-4 py-4 sm:px-6">
                <div className="flex items-center">
                  <div className="flex-shrink-0 bg-primary-500 rounded-full p-1">
                    <span className="text-white text-xs font-medium">2</span>
                  </div>
                  <p className="ml-3 text-sm text-gray-700">
                    上传数据文件并等待分析完成，系统会自动执行所有分析步骤。
                  </p>
                </div>
              </div>
            </li>
            <li>
              <div className="px-4 py-4 sm:px-6">
                <div className="flex items-center">
                  <div className="flex-shrink-0 bg-primary-500 rounded-full p-1">
                    <span className="text-white text-xs font-medium">3</span>
                  </div>
                  <p className="ml-3 text-sm text-gray-700">
                    查看分析结果，包括用户聚类图、行为热力图和转化漏斗图等可视化内容。
                  </p>
                </div>
              </div>
            </li>
            <li>
              <div className="px-4 py-4 sm:px-6">
                <div className="flex items-center">
                  <div className="flex-shrink-0 bg-primary-500 rounded-full p-1">
                    <span className="text-white text-xs font-medium">4</span>
                  </div>
                  <p className="ml-3 text-sm text-gray-700">
                    下载分析结果图表和处理后的数据文件，用于报告或进一步分析。
                  </p>
                </div>
              </div>
            </li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default HomePage; 