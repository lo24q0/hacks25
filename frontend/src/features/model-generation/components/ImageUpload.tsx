import React, { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { Button, Card, Space, Typography, Toast } from '@douyinfe/semi-ui';
import { IconClose } from '@douyinfe/semi-icons';

const { Text } = Typography;

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
    <Space vertical align="start" style={{ width: '100%' }} spacing="medium">
      <div
        {...getRootProps()}
        className={`
          border-2 border-dashed rounded-lg p-8 text-center cursor-pointer
          transition-colors duration-200
          ${isDragActive ? 'border-blue-500 bg-blue-50' : 'border-gray-300 hover:border-gray-400'}
          ${loading ? 'opacity-50 cursor-not-allowed' : ''}
        `}
        style={{ width: '100%' }}
      >
        <input {...getInputProps()} disabled={loading} />
        
        <svg
          className="mx-auto h-12 w-12 text-gray-400"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"
          />
        </svg>

        {isDragActive ? (
          <Text className="mt-2 text-sm" type="primary">松开鼠标上传图片...</Text>
        ) : (
          <div className="mt-2">
            <Text className="text-sm text-gray-600">
              拖拽图片到这里,或点击选择文件
            </Text>
            <br />
            <Text className="mt-1 text-xs text-gray-500">
              支持 JPG、PNG 格式,最多 {maxFiles} 张,每张最大 {maxSize / 1024 / 1024}MB
            </Text>
          </div>
        )}
      </div>

      {uploadedFiles.length > 0 && (
        <Space vertical align="start" style={{ width: '100%' }} spacing="medium">
          <Text strong>已选择 {uploadedFiles.length} 张图片:</Text>
          
          <div className="grid grid-cols-2 md:grid-cols-3 gap-4" style={{ width: '100%' }}>
            {uploadedFiles.map((file, index) => (
              <Card
                key={index}
                bodyStyle={{ padding: 8 }}
                className="relative group"
              >
                <img
                  src={previews[index]}
                  alt={file.name}
                  className="w-full h-32 object-cover rounded-lg"
                />
                <button
                  type="button"
                  onClick={() => removeFile(index)}
                  className="absolute top-2 right-2 bg-red-500 text-white rounded-full p-1 
                           opacity-0 group-hover:opacity-100 transition-opacity duration-200
                           hover:bg-red-600 focus:outline-none"
                  disabled={loading}
                >
                  <IconClose size="small" />
                </button>
                <Text size="small" className="mt-1 truncate block">{file.name}</Text>
              </Card>
            ))}
          </div>

          <Button
            type="primary"
            size="large"
            block
            onClick={handleSubmit}
            disabled={loading}
            loading={loading}
          >
            {loading ? '上传中...' : '上传并生成 3D 模型'}
          </Button>
        </Space>
      )}
    </Space>
  );
};

export default ImageUpload;
