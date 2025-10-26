/**
 * 风格选择器组件
 *
 * 显示所有可用的风格预设,支持选择单个风格
 */

import React from 'react'
import { Card, Tag, Space, Typography, Spin, Empty } from '@douyinfe/semi-ui'
import { IconTickCircle } from '@douyinfe/semi-icons'
import type { StylePreset } from '../types'

const { Title, Text, Paragraph } = Typography

interface StyleSelectorProps {
  /** 风格预设列表 */
  presets: StylePreset[]
  /** 当前选中的风格ID */
  selectedStyleId?: string
  /** 选择风格的回调 */
  onSelect: (styleId: string) => void
  /** 是否加载中 */
  loading?: boolean
}

/**
 * 风格选择器组件
 */
export const StyleSelector: React.FC<StyleSelectorProps> = ({
  presets,
  selectedStyleId,
  onSelect,
  loading = false,
}) => {
  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '40px 0' }}>
        <Spin size="large" tip="加载风格预设中..." />
      </div>
    )
  }

  if (!presets || presets.length === 0) {
    return (
      <Empty
        title="暂无风格预设"
        description="请稍后再试或联系管理员"
        style={{ padding: '40px 0' }}
      />
    )
  }

  return (
    <div style={{ width: '100%' }}>
      <Title heading={4} style={{ marginBottom: 20 }}>
        选择风格
      </Title>

      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))',
          gap: '20px',
        }}
      >
        {presets.map((preset) => {
          const isSelected = selectedStyleId === preset.id

          return (
            <Card
              key={preset.id}
              hoverable
              onClick={() => onSelect(preset.id)}
              style={{
                cursor: 'pointer',
                border: isSelected ? '2px solid var(--semi-color-primary)' : '1px solid #e8e8e8',
                position: 'relative',
                transition: 'all 0.3s ease',
              }}
              bodyStyle={{ padding: 16 }}
            >
              {/* 选中标识 */}
              {isSelected && (
                <div
                  style={{
                    position: 'absolute',
                    top: 12,
                    right: 12,
                    zIndex: 1,
                  }}
                >
                  <IconTickCircle
                    size="extra-large"
                    style={{ color: 'var(--semi-color-success)' }}
                  />
                </div>
              )}

              {/* 预览图 */}
              <div
                style={{
                  width: '100%',
                  height: 160,
                  background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                  borderRadius: 6,
                  marginBottom: 12,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  overflow: 'hidden',
                }}
              >
                {/* TODO: 替换为实际预览图 */}
                <Text style={{ color: 'white', fontSize: 24, fontWeight: 'bold' }}>
                  {preset.name_en}
                </Text>
              </div>

              {/* 标题 */}
              <Space vertical spacing={8} style={{ width: '100%' }}>
                <div
                  style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}
                >
                  <Text strong style={{ fontSize: 16 }}>
                    {preset.name}
                  </Text>
                  <Text type="tertiary" size="small">
                    ~{preset.estimated_time}s
                  </Text>
                </div>

                {/* 描述 */}
                <Paragraph
                  ellipsis={{ rows: 2 }}
                  style={{ margin: 0, fontSize: 13, color: '#666' }}
                >
                  {preset.description}
                </Paragraph>

                {/* 标签 */}
                <div style={{ marginTop: 8 }}>
                  <Space spacing={4}>
                    {preset.tags.slice(0, 3).map((tag) => (
                      <Tag key={tag} size="small" color="blue">
                        {tag}
                      </Tag>
                    ))}
                  </Space>
                </div>

                {/* 推荐强度 */}
                <div style={{ marginTop: 8 }}>
                  <Text size="small" type="tertiary">
                    推荐强度: {preset.recommended_strength}
                  </Text>
                </div>
              </Space>
            </Card>
          )
        })}
      </div>

      {/* 说明文字 */}
      <div style={{ marginTop: 20, padding: 16, background: '#f8f9fa', borderRadius: 8 }}>
        <Text type="tertiary" size="small">
          💡
          提示:点击卡片选择风格,不同风格适合不同类型的图片。处理时间仅供参考,实际时间可能因图片大小而异。
        </Text>
      </div>
    </div>
  )
}

export default StyleSelector
