import React, { useCallback, useState } from 'react';
import { useDropzone, type FileRejection } from 'react-dropzone';
import { Button } from '@/shared/components/ui';

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
  const [previews, setPreviews] = useState<Array<{ file: File; preview: string }>>([]);
  const [error, setError] = useState<string | null>(null);

  const onDrop = useCallback(
    (acceptedFiles: File[], rejectedFiles: FileRejection[]) => {
      setError(null);

      if (rejectedFiles.length > 0) {
        const firstError = rejectedFiles[0].errors[0];
        if (firstError.code === 'file-too-large') {
          setError(`文件大小不能超过 ${maxSize / (1024 * 1024)} MB`);
        } else if (firstError.code === 'file-invalid-type') {
          setError('只支持 JPG, PNG 格式的图片');
        } else {
          setError(firstError.message);
        }
        return;
      }

      if (previews.length + acceptedFiles.length > maxFiles) {
        setError(`最多只能上传 ${maxFiles} 张图片`);
        return;
      }

      const newPreviews = acceptedFiles.map((file) => ({
        file,
        preview: URL.createObjectURL(file),
      }));

      setPreviews((prev) => [...prev, ...newPreviews]);
    },
    [maxFiles, maxSize, previews.length]
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/jpeg': ['.jpg', '.jpeg'],
      'image/png': ['.png'],
    },
    maxSize,
    maxFiles,
    disabled: loading,
  });

  const removePreview = (index: number) => {
    setPreviews((prev) => {
      const updated = [...prev];
      URL.revokeObjectURL(updated[index].preview);
      updated.splice(index, 1);
      return updated;
    });
    setError(null);
  };

  const handleUpload = () => {
    if (previews.length === 0) {
      setError('请至少上传一张图片');
      return;
    }
    const files = previews.map((p) => p.file);
    onUpload(files);
  };

  React.useEffect(() => {
    return () => {
      previews.forEach((preview) => URL.revokeObjectURL(preview.preview));
    };
  }, [previews]);

  return (
    <div className="space-y-4">
      <div
        {...getRootProps()}
        className={`
          border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors
          ${isDragActive ? 'border-blue-500 bg-blue-50' : 'border-gray-300 hover:border-blue-400'}
          ${loading ? 'opacity-50 cursor-not-allowed' : ''}
        `}
      >
        <input {...getInputProps()} />
        <div className="flex flex-col items-center space-y-2">
          <svg
            className="w-12 h-12 text-gray-400"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
            />
          </svg>
          <div>
            {isDragActive ? (
              <p className="text-blue-600 font-medium">松开鼠标即可上传</p>
            ) : (
              <>
                <p className="text-gray-700 font-medium">拖拽图片到这里,或点击选择</p>
                <p className="text-sm text-gray-500 mt-1">
                  支持 JPG、PNG 格式,单个文件最大 {maxSize / (1024 * 1024)} MB
                </p>
                <p className="text-sm text-gray-500">
                  最多上传 {maxFiles} 张图片
                </p>
              </>
            )}
          </div>
        </div>
      </div>

      {error && (
        <div className="p-3 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-sm text-red-600">{error}</p>
        </div>
      )}

      {previews.length > 0 && (
        <div>
          <h3 className="text-sm font-medium text-gray-700 mb-2">
            已选择 {previews.length} 张图片
          </h3>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
            {previews.map((preview, index) => (
              <div key={preview.preview} className="relative group">
                <img
                  src={preview.preview}
                  alt={`预览 ${index + 1}`}
                  className="w-full h-32 object-cover rounded-lg"
                />
                <button
                  type="button"
                  onClick={() => removePreview(index)}
                  className="absolute top-1 right-1 p-1 bg-red-600 text-white rounded-full opacity-0 group-hover:opacity-100 transition-opacity"
                  disabled={loading}
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M6 18L18 6M6 6l12 12"
                    />
                  </svg>
                </button>
                <div className="absolute bottom-1 left-1 right-1 bg-black bg-opacity-50 text-white text-xs p-1 rounded truncate">
                  {preview.file.name}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {previews.length > 0 && (
        <Button
          type="button"
          variant="primary"
          size="lg"
          fullWidth
          onClick={handleUpload}
          disabled={loading}
          loading={loading}
        >
          {loading ? '上传中...' : '上传并生成 3D 模型'}
        </Button>
      )}
    </div>
  );
};

export default ImageUpload;
