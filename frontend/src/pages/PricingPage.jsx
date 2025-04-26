import React from 'react';

const PricingPage = () => {
  return (
    <div className="bg-white shadow overflow-hidden sm:rounded-lg">
      <div className="px-4 py-5 sm:px-6">
        <h2 className="text-2xl font-bold leading-7 text-gray-900">价格方案</h2>
        <p className="mt-1 max-w-2xl text-sm text-gray-500">我们为所有用户提供免费的数据分析服务</p>
      </div>
      
      <div className="border-t border-gray-200">
        <div className="bg-gray-50 px-4 py-5 sm:grid sm:grid-cols-1 sm:gap-4 sm:px-6">
          <div className="mt-5 md:mt-0 md:col-span-2">
            <div className="bg-white overflow-hidden shadow rounded-lg">
              <div className="px-4 py-5 sm:p-6">
                <h3 className="text-lg leading-6 font-medium text-gray-900">免费版</h3>
                <div className="mt-2 max-w-xl text-sm text-gray-500">
                  <p>包含所有基础数据分析功能</p>
                </div>
                <div className="mt-5">
                  <div className="rounded-md bg-gray-50 px-6 py-5">
                    <div className="flex items-center">
                      <h4 className="text-3xl font-extrabold text-gray-900">¥0</h4>
                      <p className="ml-3 text-xl font-medium text-gray-500">/永久</p>
                    </div>
                  </div>
                </div>
                <div className="mt-8">
                  <div className="flex items-center">
                    <div className="flex-shrink-0 h-5 w-5 text-green-500">
                      <svg className="h-5 w-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                        <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                      </svg>
                    </div>
                    <p className="ml-3 text-sm text-gray-700">数据清洗与预处理</p>
                  </div>
                  <div className="mt-4 flex items-center">
                    <div className="flex-shrink-0 h-5 w-5 text-green-500">
                      <svg className="h-5 w-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                        <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                      </svg>
                    </div>
                    <p className="ml-3 text-sm text-gray-700">RFM客户分析</p>
                  </div>
                  <div className="mt-4 flex items-center">
                    <div className="flex-shrink-0 h-5 w-5 text-green-500">
                      <svg className="h-5 w-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                        <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                      </svg>
                    </div>
                    <p className="ml-3 text-sm text-gray-700">K-means聚类分析</p>
                  </div>
                  <div className="mt-4 flex items-center">
                    <div className="flex-shrink-0 h-5 w-5 text-green-500">
                      <svg className="h-5 w-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                        <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                      </svg>
                    </div>
                    <p className="ml-3 text-sm text-gray-700">漏斗分析</p>
                  </div>
                  <div className="mt-4 flex items-center">
                    <div className="flex-shrink-0 h-5 w-5 text-green-500">
                      <svg className="h-5 w-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                        <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                      </svg>
                    </div>
                    <p className="ml-3 text-sm text-gray-700">用户行为热力图</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PricingPage;