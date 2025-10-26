/**
 * 风格化结果预览组件
 *
 * 显示原图和风格化后的图片对比
 */

import React, { useState } from 'react'
import { Card, Button, Space, Typography, Tooltip, Switch } from '@douyinfe/semi-ui'
import { IconDownload, IconArrowLeft, IconArrowRight } from '@douyinfe/semi-icons'

const { Title, Text } = Typography

interface StylePreviewProps {
  /** 原图URL */
  originalImageUrl: string
  /** 风格化结果URL */
  styledImageUrl: string
  /** 风格名称 */
  styleName: string
  /** 下载回调 */
  onDownload?: () => void
}

/**
 * 风格化结果预览组件
 */
export const StylePreview: React.FC<StylePreviewProps> = ({
  originalImageUrl,
  styledImageUrl,
  styleName,
  onDownload,
}) => {
  const [compareMode, setCompareMode] = useState(false)
  const [sliderPosition, setSliderPosition] = useState(50)

  // 处理滑块拖动
  const handleSliderChange = (e: React.MouseEvent<HTMLDivElement>) => {
    const rect = e.currentTarget.getBoundingClientRect()
    const x = e.clientX - rect.left
    const percentage = (x / rect.width) * 100
    setSliderPosition(Math.max(0, Math.min(100, percentage)))
  }

  return (
    <div style={{ width: '100%' }}>
      {/* 标题栏 */}
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginBottom: 20,
        }}
      >
        <Title heading={4} style={{ margin: 0 }}>
          风格化结果
        </Title>

        <Space>
          {/* 对比模式切换 */}
          <Tooltip content="切换对比模式">
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <Text size="small">对比模式</Text>
              <Switch
                checked={compareMode}
                onChange={(checked) => setCompareMode(checked)}
                aria-label="切换对比模式"
              />
            </div>
          </Tooltip>

          {/* 下载按钮 */}
          <Button icon={<IconDownload />} theme="solid" type="primary" onClick={onDownload}>
            下载图片
          </Button>
        </Space>
      </div>

      {/* 预览区域 */}
      <Card
        style={{
          padding: 0,
          overflow: 'hidden',
        }}
        bodyStyle={{ padding: 0 }}
      >
        {compareMode ? (
          // 对比模式:滑块对比
          <div
            style={{
              position: 'relative',
              width: '100%',
              height: 600,
              overflow: 'hidden',
              cursor: 'ew-resize',
            }}
            onMouseMove={handleSliderChange}
          >
            {/* 风格化图片(底层) */}
            <div
              style={{
                position: 'absolute',
                width: '100%',
                height: '100%',
                backgroundImage: `url(${styledImageUrl})`,
                backgroundSize: 'contain',
                backgroundPosition: 'center',
                backgroundRepeat: 'no-repeat',
              }}
            />

            {/* 原图(顶层,带裁剪) */}
            <div
              style={{
                position: 'absolute',
                width: '100%',
                height: '100%',
                clipPath: `inset(0 ${100 - sliderPosition}% 0 0)`,
                backgroundImage: `url(${originalImageUrl})`,
                backgroundSize: 'contain',
                backgroundPosition: 'center',
                backgroundRepeat: 'no-repeat',
              }}
            />

            {/* 滑块分割线 */}
            <div
              style={{
                position: 'absolute',
                left: `${sliderPosition}%`,
                top: 0,
                bottom: 0,
                width: 3,
                background: 'white',
                boxShadow: '0 0 10px rgba(0,0,0,0.3)',
                transform: 'translateX(-50%)',
              }}
            >
              {/* 滑块手柄 */}
              <div
                style={{
                  position: 'absolute',
                  top: '50%',
                  left: '50%',
                  transform: 'translate(-50%, -50%)',
                  width: 40,
                  height: 40,
                  background: 'white',
                  borderRadius: '50%',
                  boxShadow: '0 2px 10px rgba(0,0,0,0.2)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: 2,
                }}
              >
                <IconArrowLeft size="small" />
                <IconArrowRight size="small" />
              </div>
            </div>

            {/* 标签 */}
            <div
              style={{
                position: 'absolute',
                top: 16,
                left: 16,
                background: 'rgba(0,0,0,0.6)',
                padding: '4px 12px',
                borderRadius: 4,
              }}
            >
              <Text style={{ color: 'white', fontSize: 12 }}>原图</Text>
            </div>
            <div
              style={{
                position: 'absolute',
                top: 16,
                right: 16,
                background: 'rgba(0,0,0,0.6)',
                padding: '4px 12px',
                borderRadius: 4,
              }}
            >
              <Text style={{ color: 'white', fontSize: 12 }}>{styleName}</Text>
            </div>
          </div>
        ) : (
          // 普通模式:左右并排
          <div
            style={{
              display: 'grid',
              gridTemplateColumns: '1fr 1fr',
              gap: 1,
              background: '#f0f0f0',
            }}
          >
            {/* 原图 */}
            <div style={{ position: 'relative', height: 600, background: 'white' }}>
              <div
                style={{
                  width: '100%',
                  height: '100%',
                  backgroundImage: `url(${originalImageUrl})`,
                  backgroundSize: 'contain',
                  backgroundPosition: 'center',
                  backgroundRepeat: 'no-repeat',
                }}
              />
              <div
                style={{
                  position: 'absolute',
                  top: 16,
                  left: 16,
                  background: 'rgba(0,0,0,0.6)',
                  padding: '4px 12px',
                  borderRadius: 4,
                }}
              >
                <Text style={{ color: 'white', fontSize: 12 }}>原图</Text>
              </div>
            </div>

            {/* 风格化图片 */}
            <div style={{ position: 'relative', height: 600, background: 'white' }}>
              <div
                style={{
                  width: '100%',
                  height: '100%',
                  backgroundImage: `url(${styledImageUrl})`,
                  backgroundSize: 'contain',
                  backgroundPosition: 'center',
                  backgroundRepeat: 'no-repeat',
                }}
              />
              <div
                style={{
                  position: 'absolute',
                  top: 16,
                  left: 16,
                  background: 'rgba(0,0,0,0.6)',
                  padding: '4px 12px',
                  borderRadius: 4,
                }}
              >
                <Text style={{ color: 'white', fontSize: 12 }}>{styleName}</Text>
              </div>
            </div>
          </div>
        )}
      </Card>

      {/* 提示信息 */}
      <div style={{ marginTop: 16, padding: 16, background: '#f8f9fa', borderRadius: 8 }}>
        <Text type="tertiary" size="small">
          💡 提示:
          {compareMode
            ? '拖动中间的滑块可以对比原图和风格化效果'
            : '开启对比模式可使用滑块查看细节差异'}
        </Text>
      </div>
    </div>
  )
}

export default StylePreview
