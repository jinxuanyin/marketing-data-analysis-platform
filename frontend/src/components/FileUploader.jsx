import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const FileUploader = () => {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile && selectedFile.name.endsWith('.csv')) {
      setFile(selectedFile);
      setError('');
    } else {
      setFile(null);
      setError('请选择CSV格式的文件');
    }
  };

  const handleUpload = async () => {
    if (!file) {
      setError('请先选择一个CSV文件');
      return;
    }

    setUploading(true);
    setError('');

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post(`${API_URL}/upload/`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      if (response.data && response.data.session_id) {
        // 上传成功，跳转到分析页面
        navigate(`/analysis/${response.data.session_id}`);
      } else {
        setError('上传失败，未获取会话ID');
      }
    } catch (err) {
      setError(err.response?.data?.detail || '文件上传失败，请重试');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow-md">
      <div className="space-y-4">
        <div className="text-center">
          <h3 className="text-lg font-medium text-gray-900">上传数据文件</h3>
          <p className="mt-1 text-sm text-gray-500">请上传包含用户行为数据的CSV文件</p>
        </div>

        <div className="mt-2">
          <div className="flex justify-center px-6 pt-5 pb-6 border-2 border-gray-300 border-dashed rounded-md">
            <div className="space-y-1 text-center">
              <svg
                className="mx-auto h-12 w-12 text-gray-400"
                stroke="currentColor"
                fill="none"
                viewBox="0 0 48 48"
                aria-hidden="true"
              >
                <path
                  d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02"
                  strokeWidth={2}
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />
              </svg>
              <div className="flex text-sm text-gray-600">
                <label
                  htmlFor="file-upload"
                  className="relative cursor-pointer bg-white rounded-md font-medium text-primary-600 hover:text-primary-500 focus-within:outline-none focus-within:ring-2 focus-within:ring-offset-2 focus-within:ring-primary-500"
                >
                  <span>选择文件</span>
                  <input
                    id="file-upload"
                    name="file-upload"
                    type="file"
                    className="sr-only"
                    accept=".csv"
                    onChange={handleFileChange}
                    disabled={uploading}
                  />
                </label>
                <p className="pl-1">或拖放到此区域</p>
              </div>
              <p className="text-xs text-gray-500">仅支持CSV格式</p>
              {file && (
                <p className="text-sm text-primary-600">已选择: {file.name}</p>
              )}
            </div>
          </div>
        </div>

        {error && (
          <div className="text-sm text-red-600 mt-2">
            <p>{error}</p>
          </div>
        )}

        <div className="flex justify-center">
          <button
            type="button"
            onClick={handleUpload}
            disabled={!file || uploading}
            className={`inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white ${
              !file || uploading
                ? 'bg-gray-300 cursor-not-allowed'
                : 'bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500'
            }`}
          >
            {uploading ? '上传中...' : '开始分析'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default FileUploader;