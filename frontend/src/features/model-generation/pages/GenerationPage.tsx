import { useState } from 'react';
import ModelPreview from '../components/ModelPreview';

export default function GenerationPage() {
  const [modelUrl, setModelUrl] = useState<string>('');
  const [showPreview, setShowPreview] = useState(false);

  const handleLoadDemo = () => {
    setModelUrl('/test-models/cube.stl');
    setShowPreview(true);
  };

  return (
    <div className="space-y-8">
      <div className="text-center">
        <h2 className="text-3xl font-bold text-gray-900">3D模型生成</h2>
        <p className="mt-2 text-gray-600">
          通过文本描述或照片生成3D模型
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="space-y-4">
            <div>
              <label htmlFor="prompt" className="block text-sm font-medium text-gray-700">
                文本描述
              </label>
              <textarea
                id="prompt"
                rows={4}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                placeholder="例如: 一个圆形的咖啡杯"
              />
            </div>
            <button
              type="button"
              className="w-full bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
            >
              生成3D模型
            </button>
            
            <div className="relative">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-gray-300" />
              </div>
              <div className="relative flex justify-center text-sm">
                <span className="px-2 bg-white text-gray-500">或</span>
              </div>
            </div>

            <button
              type="button"
              onClick={handleLoadDemo}
              className="w-full bg-gray-100 text-gray-700 px-4 py-2 rounded-md hover:bg-gray-200 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2 border border-gray-300"
            >
              加载测试模型
            </button>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">3D预览</h3>
          {showPreview ? (
            <ModelPreview
              modelUrl={modelUrl}
              className="h-[500px]"
              onLoadComplete={() => console.log('Model loaded successfully')}
              onLoadError={(error) => console.error('Model load error:', error)}
            />
          ) : (
            <div className="h-[500px] flex items-center justify-center bg-gray-50 rounded-lg border-2 border-dashed border-gray-300">
              <div className="text-center">
                <svg
                  className="mx-auto h-16 w-16 text-gray-400"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"
                  />
                </svg>
                <p className="mt-2 text-sm text-gray-500">生成或加载模型后显示3D预览</p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
