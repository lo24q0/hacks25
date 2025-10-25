import { useState } from 'react';
import ModelPreview from '../components/ModelPreview';
import TextInput from '../components/TextInput';
import ImageUpload from '../components/ImageUpload';
import { modelApi } from '../api/modelApi';
import { fileApi } from '../api/fileApi';
import { Button, Card, Tabs, TabPane, Banner, Spin, Typography, Space, Toast } from '@douyinfe/semi-ui';
import { IconEdit, IconImage, IconDownload } from '@douyinfe/semi-icons';

const { Title, Paragraph, Text } = Typography;

export default function GenerationPage() {
  const [activeTab, setActiveTab] = useState<string>('text');
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
      const errorMsg = err instanceof Error ? err.message : '生成失败,请重试';
      setError(errorMsg);
      Toast.error(errorMsg);
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
      const errorMsg = err instanceof Error ? err.message : '上传或生成失败,请重试';
      setError(errorMsg);
      Toast.error(errorMsg);
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
      Toast.success('模型下载成功!');
    } catch (err) {
      const errorMsg = '下载失败,请重试';
      setError(errorMsg);
      Toast.error(errorMsg);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        <div className="text-center mb-12">
          <Title heading={1} className="text-5xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-purple-600 mb-4">
            AI 3D 模型生成器
          </Title>
          <Paragraph className="text-xl text-gray-600">
            使用文本描述或照片,轻松创建专属 3D 模型
          </Paragraph>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <Card className="rounded-2xl shadow-xl" bodyStyle={{ padding: 32 }}>
            <Tabs 
              type="button" 
              activeKey={activeTab} 
              onChange={setActiveTab}
              style={{ marginBottom: 24 }}
            >
              <TabPane 
                tab={
                  <Space>
                    <IconEdit />
                    <span>文本生成</span>
                  </Space>
                } 
                itemKey="text"
              >
                <Space vertical align="start" spacing="medium" style={{ width: '100%' }}>
                  <Banner
                    type="info"
                    icon={null}
                    description="详细描述模型的形状、大小和特征,例如 '一个带把手的圆形咖啡杯,高度10厘米'"
                  />
                  <TextInput onGenerate={handleTextGenerate} loading={loading} />
                </Space>
              </TabPane>
              <TabPane 
                tab={
                  <Space>
                    <IconImage />
                    <span>图片生成</span>
                  </Space>
                } 
                itemKey="image"
              >
                <Space vertical align="start" spacing="medium" style={{ width: '100%' }}>
                  <Banner
                    type="info"
                    icon={null}
                    description="上传清晰的物体照片,多角度照片效果更好"
                  />
                  <ImageUpload onUpload={handleImageUpload} loading={loading} />
                </Space>
              </TabPane>
            </Tabs>

            {error && (
              <Banner
                type="danger"
                description={error}
                style={{ marginTop: 24 }}
                closeIcon={null}
              />
            )}

            {loading && progress && (
              <Banner
                type="info"
                description={
                  <Space>
                    <Spin />
                    <Text>{progress}</Text>
                  </Space>
                }
                style={{ marginTop: 24 }}
                closeIcon={null}
              />
            )}
          </Card>

          <Card className="rounded-2xl shadow-xl" bodyStyle={{ padding: 32 }}>
            <div className="flex items-center justify-between mb-6">
              <Title heading={3}>3D 预览</Title>
              {showPreview && modelId && (
                <Button
                  type="primary"
                  icon={<IconDownload />}
                  onClick={handleDownloadModel}
                  theme="solid"
                >
                  下载模型
                </Button>
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
          </Card>
        </div>

        <Card className="mt-12 rounded-2xl shadow-lg" bodyStyle={{ padding: 32 }}>
          <Title heading={3} style={{ marginBottom: 24 }}>功能特点</Title>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="flex items-start">
              <div className="flex-shrink-0 bg-blue-100 rounded-lg p-3">
                <svg className="w-6 h-6 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              </div>
              <div className="ml-4">
                <Title heading={4} style={{ margin: 0 }}>AI 驱动</Title>
                <Paragraph style={{ margin: '4px 0 0 0' }}>使用先进的 AI 技术,快速生成高质量 3D 模型</Paragraph>
              </div>
            </div>

            <div className="flex items-start">
              <div className="flex-shrink-0 bg-purple-100 rounded-lg p-3">
                <svg className="w-6 h-6 text-purple-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 15l-2 5L9 9l11 4-5 2zm0 0l5 5M7.188 2.239l.777 2.897M5.136 7.965l-2.898-.777M13.95 4.05l-2.122 2.122m-5.657 5.656l-2.12 2.122" />
                </svg>
              </div>
              <div className="ml-4">
                <Title heading={4} style={{ margin: 0 }}>简单易用</Title>
                <Paragraph style={{ margin: '4px 0 0 0' }}>无需专业知识,输入描述或上传图片即可开始</Paragraph>
              </div>
            </div>

            <div className="flex items-start">
              <div className="flex-shrink-0 bg-green-100 rounded-lg p-3">
                <svg className="w-6 h-6 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                </svg>
              </div>
              <div className="ml-4">
                <Title heading={4} style={{ margin: 0 }}>即时下载</Title>
                <Paragraph style={{ margin: '4px 0 0 0' }}>生成后可立即下载 STL 格式,用于 3D 打印</Paragraph>
              </div>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
}
