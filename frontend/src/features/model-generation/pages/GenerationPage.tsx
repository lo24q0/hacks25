import { useState } from 'react';
import ModelPreview from '../components/ModelPreview';
import TextInput from '../components/TextInput';
import ImageUpload from '../components/ImageUpload';
import { modelApi } from '../api/modelApi';
import { fileApi } from '../api/fileApi';
import { Loading } from '@/shared/components/ui';

type TabType = 'text' | 'image';

export default function GenerationPage() {
  const [activeTab, setActiveTab] = useState<TabType>('text');
  const [modelUrl, setModelUrl] = useState<string>('');
  const [showPreview, setShowPreview] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [modelId, setModelId] = useState<string | null>(null);
  const [progress, setProgress] = useState<string>('');

  const handleTextGenerate = async (text: string) => {
    setLoading(true);
    setError(null);
    setProgress('正在生成 3D 模型...');
    
    try {
      const response = await modelApi.generateFromText(text);
      setModelId(response.id);
      setProgress('模型生成中,请稍候...');
      
      await pollModelStatus(response.id);
    } catch (err) {
      setError(err instanceof Error ? err.message : '生成失败,请重试');
      setProgress('');
    } finally {
      setLoading(false);
    }
  };

  const handleImageUpload = async (files: File[]) => {
    setLoading(true);
    setError(null);
    setProgress('正在上传图片...');
    
    try {
      const uploadedFiles = await fileApi.uploadMultipleFiles(files, 24);
      const imagePaths = uploadedFiles.map(f => f.object_key);
      
      setProgress('图片上传成功,正在生成 3D 模型...');
      
      const response = await modelApi.generateFromImage(imagePaths);
      setModelId(response.id);
      setProgress('模型生成中,请稍候...');
      
      await pollModelStatus(response.id);
    } catch (err) {
      setError(err instanceof Error ? err.message : '上传或生成失败,请重试');
      setProgress('');
    } finally {
      setLoading(false);
    }
  };

  const pollModelStatus = async (id: string) => {
    const maxAttempts = 60;
    let attempts = 0;
    
    const poll = async (): Promise<void> => {
      if (attempts >= maxAttempts) {
        throw new Error('生成超时,请重试');
      }
      
      attempts++;
      const model = await modelApi.getModel(id);
      
      if (model.status === 'completed') {
        if (model.file_path) {
          setModelUrl(model.file_path);
          setShowPreview(true);
          setProgress('模型生成成功!');
        } else {
          throw new Error('模型文件路径不存在');
        }
      } else if (model.status === 'failed') {
        throw new Error(model.error_message || '模型生成失败');
      } else {
        setProgress(`生成进度: ${attempts * 2}%`);
        await new Promise(resolve => setTimeout(resolve, 2000));
        return poll();
      }
    };
    
    return poll();
  };

  const handleDownloadModel = async () => {
    if (!modelId) return;
    
    try {
      const blob = await modelApi.downloadModel(modelId);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `model_${modelId}.stl`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err) {
      setError('下载失败,请重试');
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        <div className="text-center mb-12">
          <h1 className="text-5xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-purple-600 mb-4">
            AI 3D 模型生成器
          </h1>
          <p className="text-xl text-gray-600">
            使用文本描述或照片,轻松创建专属 3D 模型
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <div className="bg-white rounded-2xl shadow-xl p-8">
            <div className="mb-6">
              <div className="flex space-x-1 bg-gray-100 p-1 rounded-lg">
                <button
                  onClick={() => setActiveTab('text')}
                  className={`flex-1 py-3 px-4 rounded-md font-medium transition-all duration-200 ${
                    activeTab === 'text'
                      ? 'bg-white text-blue-600 shadow-md'
                      : 'text-gray-600 hover:text-gray-900'
                  }`}
                >
                  <span className="flex items-center justify-center">
                    <svg className="w-5 h-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                    </svg>
                    文本生成
                  </span>
                </button>
                <button
                  onClick={() => setActiveTab('image')}
                  className={`flex-1 py-3 px-4 rounded-md font-medium transition-all duration-200 ${
                    activeTab === 'image'
                      ? 'bg-white text-blue-600 shadow-md'
                      : 'text-gray-600 hover:text-gray-900'
                  }`}
                >
                  <span className="flex items-center justify-center">
                    <svg className="w-5 h-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                    </svg>
                    图片生成
                  </span>
                </button>
              </div>
            </div>

            <div className="mt-6">
              {activeTab === 'text' ? (
                <div className="space-y-4">
                  <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                    <p className="text-sm text-blue-800">
                      💡 <strong>提示:</strong> 详细描述模型的形状、大小和特征,例如 "一个带把手的圆形咖啡杯,高度10厘米"
                    </p>
                  </div>
                  <TextInput onGenerate={handleTextGenerate} loading={loading} />
                </div>
              ) : (
                <div className="space-y-4">
                  <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
                    <p className="text-sm text-purple-800">
                      💡 <strong>提示:</strong> 上传清晰的物体照片,多角度照片效果更好
                    </p>
                  </div>
                  <ImageUpload onUpload={handleImageUpload} loading={loading} />
                </div>
              )}
            </div>

            {error && (
              <div className="mt-6 bg-red-50 border border-red-200 rounded-lg p-4">
                <div className="flex items-start">
                  <svg className="w-5 h-5 text-red-500 mt-0.5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <p className="text-sm text-red-700">{error}</p>
                </div>
              </div>
            )}

            {loading && progress && (
              <div className="mt-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
                <div className="flex items-center">
                  <Loading size="sm" />
                  <p className="ml-3 text-sm text-blue-700 font-medium">{progress}</p>
                </div>
              </div>
            )}
          </div>

          <div className="bg-white rounded-2xl shadow-xl p-8">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-2xl font-bold text-gray-900">3D 预览</h3>
              {showPreview && modelId && (
                <button
                  onClick={handleDownloadModel}
                  className="flex items-center px-4 py-2 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg hover:from-blue-700 hover:to-purple-700 transition-all duration-200 shadow-md hover:shadow-lg"
                >
                  <svg className="w-5 h-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                  </svg>
                  下载模型
                </button>
              )}
            </div>

            {showPreview ? (
              <div className="relative">
                <ModelPreview
                  modelUrl={modelUrl}
                  className="h-[600px] rounded-xl overflow-hidden border-2 border-gray-100"
                  onLoadComplete={() => console.log('Model loaded successfully')}
                  onLoadError={(error) => setError(`模型加载失败: ${error.message}`)}
                />
                <div className="absolute bottom-4 left-4 bg-black bg-opacity-60 text-white px-3 py-2 rounded-lg text-sm">
                  <p>🖱️ 拖拽旋转 | 🔍 滚轮缩放</p>
                </div>
              </div>
            ) : (
              <div className="h-[600px] flex items-center justify-center bg-gradient-to-br from-gray-50 to-gray-100 rounded-xl border-2 border-dashed border-gray-300">
                <div className="text-center">
                  <svg
                    className="mx-auto h-24 w-24 text-gray-400 mb-4"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={1.5}
                      d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"
                    />
                  </svg>
                  <p className="text-lg font-medium text-gray-600 mb-2">等待模型生成</p>
                  <p className="text-sm text-gray-500">生成完成后将在此处显示 3D 预览</p>
                </div>
              </div>
            )}
          </div>
        </div>

        <div className="mt-12 bg-white rounded-2xl shadow-lg p-8">
          <h3 className="text-2xl font-bold text-gray-900 mb-6">功能特点</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="flex items-start">
              <div className="flex-shrink-0 bg-blue-100 rounded-lg p-3">
                <svg className="w-6 h-6 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              </div>
              <div className="ml-4">
                <h4 className="text-lg font-semibold text-gray-900">AI 驱动</h4>
                <p className="mt-1 text-sm text-gray-600">使用先进的 AI 技术,快速生成高质量 3D 模型</p>
              </div>
            </div>

            <div className="flex items-start">
              <div className="flex-shrink-0 bg-purple-100 rounded-lg p-3">
                <svg className="w-6 h-6 text-purple-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 15l-2 5L9 9l11 4-5 2zm0 0l5 5M7.188 2.239l.777 2.897M5.136 7.965l-2.898-.777M13.95 4.05l-2.122 2.122m-5.657 5.656l-2.12 2.122" />
                </svg>
              </div>
              <div className="ml-4">
                <h4 className="text-lg font-semibold text-gray-900">简单易用</h4>
                <p className="mt-1 text-sm text-gray-600">无需专业知识,输入描述或上传图片即可开始</p>
              </div>
            </div>

            <div className="flex items-start">
              <div className="flex-shrink-0 bg-green-100 rounded-lg p-3">
                <svg className="w-6 h-6 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                </svg>
              </div>
              <div className="ml-4">
                <h4 className="text-lg font-semibold text-gray-900">即时下载</h4>
                <p className="mt-1 text-sm text-gray-600">生成后可立即下载 STL 格式,用于 3D 打印</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
