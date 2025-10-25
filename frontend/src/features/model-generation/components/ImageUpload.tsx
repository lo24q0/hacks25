import React, { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { 
  Button, 
  Card, 
  Space, 
  Typography, 
  Toast,
  Empty,
  Spin
} from '@douyinfe/semi-ui';
import { 
  IconClose, 
  IconUpload, 
  IconImage 
} from '@douyinfe/semi-icons';

const { Text, Title } = Typography;

interface ImageUploadProps {
  onUpload: (files: File[]) => void;
  loading?: boolean;
  maxFiles?: number;
  maxSize?: number;
}

const ImageUpload: React.FC<ImageUploadProps> = ({
  onUpload,
  loading = false,
  maxFiles = 5,
  maxSize = 10 * 1024 * 1024,
}) => {
  const [uploadedFiles, setUploadedFiles] = useState<File[]>([]);
  const [previews, setPreviews] = useState<string[]>([]);

  const onDrop = useCallback((acceptedFiles: File[]) => {
    setUploadedFiles(acceptedFiles);
    
    const newPreviews = acceptedFiles.map(file => URL.createObjectURL(file));
    setPreviews(prev => {
      prev.forEach(url => URL.revokeObjectURL(url));
      return newPreviews;
    });
  }, []);

  const { getRootProps, getInputProps, isDragActive, fileRejections } = useDropzone({
    onDrop,
    accept: {
      'image/jpeg': ['.jpg', '.jpeg'],
      'image/png': ['.png'],
    },
    maxFiles,
    maxSize,
    multiple: true,
    disabled: loading,
  });

  const handleSubmit = () => {
    if (uploadedFiles.length > 0) {
      onUpload(uploadedFiles);
    }
  };

  const removeFile = (index: number) => {
    setUploadedFiles(prev => prev.filter((_, i) => i !== index));
    setPreviews(prev => {
      URL.revokeObjectURL(prev[index]);
      return prev.filter((_, i) => i !== index);
    });
  };

  React.useEffect(() => {
    return () => {
      previews.forEach(url => URL.revokeObjectURL(url));
    };
  }, [previews]);

  React.useEffect(() => {
    if (fileRejections.length > 0) {
      const errors = fileRejections.map(({ file, errors }) => 
        `${file.name}: ${errors.map(e => e.message).join(', ')}`
      ).join('\n');
      Toast.error({
        content: errors,
        duration: 3,
      });
    }
  }, [fileRejections]);

  return (
    <Space vertical align="start" style={{ width: '100%' }} spacing="large">
      {/* 拖拽上传区域 */}
      <Card
        {...getRootProps()}
        style={{ 
          width: '100%',
          cursor: loading ? 'not-allowed' : 'pointer',
          transition: 'all 0.3s ease',
          background: isDragActive 
            ? 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' 
            : 'var(--semi-color-fill-0)',
        }}
        bodyStyle={{ 
          padding: '48px 24px',
          textAlign: 'center',
        }}
        bordered
        hoverable={!loading}
        className={isDragActive ? 'drag-active' : ''}
      >
        <input {...getInputProps()} disabled={loading} />
        
        <Spin spinning={loading}>
          <Space vertical align="center" spacing="medium" style={{ width: '100%' }}>
            {/* 图标 */}
            <div 
              style={{ 
                fontSize: '64px',
                color: isDragActive ? '#fff' : 'var(--semi-color-primary)',
                transition: 'all 0.3s ease',
              }}
            >
              {isDragActive ? (
                <IconImage style={{ fontSize: '64px' }} />
              ) : (
                <IconUpload style={{ fontSize: '64px' }} />
              )}
            </div>

            {/* 文本提示 */}
            {isDragActive ? (
              <div>
                <Title 
                  heading={5} 
                  style={{ 
                    color: '#fff',
                    margin: 0,
                    fontWeight: 600,
                  }}
                >
                  松开鼠标上传图片
                </Title>
              </div>
            ) : (
              <div>
                <Title 
                  heading={5} 
                  style={{ 
                    color: 'var(--semi-color-text-0)',
                    margin: '0 0 8px 0',
                    fontWeight: 600,
                  }}
                >
                  拖拽图片到这里，或点击选择文件
                </Title>
                <Text 
                  type="tertiary" 
                  size="small"
                  style={{ display: 'block' }}
                >
                  支持 JPG、PNG 格式
                </Text>
                <Text 
                  type="tertiary" 
                  size="small"
                  style={{ display: 'block', marginTop: '4px' }}
                >
                  最多 {maxFiles} 张，每张最大 {maxSize / 1024 / 1024}MB
                </Text>
              </div>
            )}

            {/* 上传按钮 */}
            {!isDragActive && (
              <Button 
                theme="solid" 
                type="primary"
                icon={<IconUpload />}
                disabled={loading}
                style={{ marginTop: '8px' }}
              >
                选择图片
              </Button>
            )}
          </Space>
        </Spin>
      </Card>

      {/* 图片预览区域 */}
      {uploadedFiles.length > 0 ? (
        <Space vertical align="start" style={{ width: '100%' }} spacing="medium">
          <div style={{ 
            display: 'flex', 
            justifyContent: 'space-between', 
            alignItems: 'center',
            width: '100%',
          }}>
            <Text strong style={{ fontSize: '16px' }}>
              已选择 {uploadedFiles.length} 张图片
            </Text>
            {uploadedFiles.length > 0 && !loading && (
              <Button
                type="tertiary"
                size="small"
                onClick={() => {
                  previews.forEach(url => URL.revokeObjectURL(url));
                  setUploadedFiles([]);
                  setPreviews([]);
                }}
              >
                清空
              </Button>
            )}
          </div>
          
          <div 
            style={{ 
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))',
              gap: '16px',
              width: '100%',
            }}
          >
            {uploadedFiles.map((file, index) => (
              <Card
                key={index}
                bodyStyle={{ 
                  padding: 0,
                  position: 'relative',
                  overflow: 'hidden',
                }}
                style={{
                  transition: 'all 0.3s ease',
                }}
                hoverable
                cover={
                  <img
                    src={previews[index]}
                    alt={file.name}
                    style={{
                      width: '100%',
                      height: '180px',
                      objectFit: 'cover',
                    }}
                  />
                }
              >
                <div style={{ padding: '12px' }}>
                  <Text 
                    ellipsis={{ showTooltip: true }}
                    size="small"
                    style={{ display: 'block' }}
                  >
                    {file.name}
                  </Text>
                  <Text 
                    type="tertiary" 
                    size="small"
                    style={{ display: 'block', marginTop: '4px' }}
                  >
                    {(file.size / 1024).toFixed(2)} KB
                  </Text>
                </div>
                
                {!loading && (
                  <Button
                    type="danger"
                    theme="solid"
                    icon={<IconClose />}
                    size="small"
                    onClick={() => removeFile(index)}
                    style={{
                      position: 'absolute',
                      top: '8px',
                      right: '8px',
                      opacity: 0.9,
                      transition: 'opacity 0.2s ease',
                    }}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.opacity = '1';
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.opacity = '0.9';
                    }}
                  />
                )}
              </Card>
            ))}
          </div>

          <Button
            type="primary"
            theme="solid"
            size="large"
            block
            onClick={handleSubmit}
            disabled={loading || uploadedFiles.length === 0}
            loading={loading}
            icon={<IconUpload />}
            style={{
              marginTop: '16px',
              height: '48px',
              fontSize: '16px',
              fontWeight: 600,
            }}
          >
            {loading ? '上传中...' : `上传 ${uploadedFiles.length} 张图片并生成 3D 模型`}
          </Button>
        </Space>
      ) : (
        !loading && (
          <Empty
            image={<IconImage style={{ fontSize: '48px' }} />}
            title="暂无图片"
            description="请拖拽或点击上方区域选择图片"
            style={{ padding: '24px 0' }}
          />
        )
      )}

      <style>{`
        .drag-active {
          border: 2px dashed #fff !important;
          box-shadow: 0 8px 24px rgba(102, 126, 234, 0.3) !important;
        }
      `}</style>
    </Space>
  );
};

export default ImageUpload;
