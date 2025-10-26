/**
 * 风格化图片上传组件
 *
 * 简化版的图片上传,只支持单张图片
 */

import React, { useCallback, useState } from 'react'
import { useDropzone } from 'react-dropzone'
import { Card, Space, Typography, Toast } from '@douyinfe/semi-ui'

const { Text, Title } = Typography

interface StyleImageUploadProps {
  /** 文件选择回调 */
  onFileChange: (file: File | null) => void
  /** 是否加载中 */
  loading?: boolean
  /** 最大文件大小(字节) */
  maxSize?: number
}

/**
 * 风格化图片上传组件
 */
export const StyleImageUpload: React.FC<StyleImageUploadProps> = ({
  onFileChange,
  loading = false,
  maxSize = 10 * 1024 * 1024, // 10MB
}) => {
  const [preview, setPreview] = useState<string | null>(null)

  const onDrop = useCallback(
    (acceptedFiles: File[]) => {
      if (acceptedFiles.length === 0) return

      const file = acceptedFiles[0]

      // 验证文件大小
      if (file.size > maxSize) {
        Toast.error(`文件过大,最大支持 ${maxSize / 1024 / 1024}MB`)
        return
      }

      // 验证文件类型
      if (!file.type.startsWith('image/')) {
        Toast.error('只支持图片文件')
        return
      }

      // 创建预览
      const previewUrl = URL.createObjectURL(file)
      if (preview) {
        URL.revokeObjectURL(preview)
      }
      setPreview(previewUrl)

      // 回调
      onFileChange(file)
      Toast.success('图片上传成功')
    },
    [onFileChange, maxSize, preview]
  )

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.jpg', '.jpeg', '.png', '.webp'],
    },
    maxFiles: 1,
    disabled: loading,
  })

  return (
    <Space vertical spacing={16} style={{ width: '100%' }}>
      {/* 上传区域 */}
      <Card
        {...getRootProps()}
        style={{
          border: isDragActive ? '2px dashed var(--semi-color-primary)' : '2px dashed #e8e8e8',
          background: isDragActive ? 'rgba(var(--semi-blue-0), 0.5)' : '#fafafa',
          cursor: loading ? 'not-allowed' : 'pointer',
          transition: 'all 0.3s ease',
        }}
        bodyStyle={{
          padding: 40,
          textAlign: 'center',
        }}
      >
        <input {...getInputProps()} />
        <Space vertical spacing={12} align="center">
          <div style={{ fontSize: 48 }}>📸</div>
          {isDragActive ? (
            <Text>松开以上传图片</Text>
          ) : (
            <>
              <Title heading={5} style={{ margin: 0 }}>
                拖拽图片到此处,或点击选择文件
              </Title>
              <Text type="tertiary" size="small">
                支持 JPG、PNG、WEBP 格式,最大 10MB
              </Text>
            </>
          )}
        </Space>
      </Card>

      {/* 预览 */}
      {preview && (
        <Card>
          <Title heading={5} style={{ marginBottom: 16 }}>
            图片预览
          </Title>
          <div
            style={{
              width: '100%',
              maxWidth: 400,
              height: 300,
              margin: '0 auto',
              borderRadius: 8,
              overflow: 'hidden',
              background: '#f0f0f0',
            }}
          >
            <img
              src={preview}
              alt="预览"
              style={{
                width: '100%',
                height: '100%',
                objectFit: 'contain',
              }}
            />
          </div>
        </Card>
      )}
    </Space>
  )
}

export default StyleImageUpload
