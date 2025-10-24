export default function GenerationPage() {
  return (
    <div className="space-y-8">
      <div className="text-center">
        <h2 className="text-3xl font-bold text-gray-900">3D模型生成</h2>
        <p className="mt-2 text-gray-600">
          通过文本描述或照片生成3D模型
        </p>
      </div>

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
        </div>
      </div>
    </div>
  );
}
