/**
 * 风格化进度显示组件
 *
 * 显示任务处理进度和状态
 */

import React, { useEffect, useState } from 'react'
import { Card, Progress, Typography, Space, Tag, Spin } from '@douyinfe/semi-ui'
import { IconTickCircle, IconAlertCircle, IconClock } from '@douyinfe/semi-icons'
import type { TaskStatus } from '../types'

const { Title, Text, Paragraph } = Typography

interface StyleProgressProps {
  /** 任务状态 */
  status: TaskStatus
  /** 风格名称 */
  styleName: string
  /** 预计处理时间(秒) */
  estimatedTime?: number
  /** 实际处理时间(秒) */
  actualTime?: number
  /** 错误消息 */
  errorMessage?: string
  /** 错误建议 */
  errorSuggestion?: string
}

/**
 * 风格化进度显示组件
 */
export const StyleProgress: React.FC<StyleProgressProps> = ({
  status,
  styleName,
  estimatedTime = 20,
  actualTime,
  errorMessage,
  errorSuggestion,
}) => {
  const [elapsedTime, setElapsedTime] = useState(0)
  const [progress, setProgress] = useState(0)

  // 计时器
  useEffect(() => {
    if (status === 'processing') {
      const startTime = Date.now()
      const timer = setInterval(() => {
        const elapsed = Math.floor((Date.now() - startTime) / 1000)
        setElapsedTime(elapsed)

        // 模拟进度(不超过95%)
        const simulatedProgress = Math.min(95, (elapsed / estimatedTime) * 100)
        setProgress(simulatedProgress)
      }, 500)

      return () => clearInterval(timer)
    } else if (status === 'completed') {
      setProgress(100)
    }
  }, [status, estimatedTime])

  // 根据状态获取颜色和图标
  const getStatusConfig = () => {
    switch (status) {
      case 'pending':
        return {
          color: 'blue',
          icon: <IconClock />,
          text: '等待处理',
        }
      case 'processing':
        return {
          color: 'orange',
          icon: <Spin size="small" />,
          text: '处理中',
        }
      case 'completed':
        return {
          color: 'green',
          icon: <IconTickCircle />,
          text: '处理完成',
        }
      case 'failed':
        return {
          color: 'red',
          icon: <IconAlertCircle />,
          text: '处理失败',
        }
      default:
        return {
          color: 'grey',
          icon: null,
          text: '未知状态',
        }
    }
  }

  const statusConfig = getStatusConfig()

  return (
    <Card style={{ width: '100%' }}>
      <Space vertical spacing={16} style={{ width: '100%' }}>
        {/* 标题和状态 */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Title heading={4} style={{ margin: 0 }}>
            风格化处理
          </Title>
          <Tag color={statusConfig.color} size="large" icon={statusConfig.icon}>
            {statusConfig.text}
          </Tag>
        </div>

        {/* 风格信息 */}
        <div>
          <Text type="secondary">当前风格:</Text>
          <Text strong style={{ marginLeft: 8 }}>
            {styleName}
          </Text>
        </div>

        {/* 进度条(仅在处理中时显示) */}
        {status === 'processing' && (
          <div>
            <Progress
              percent={progress}
              showInfo
              stroke="var(--semi-color-warning)"
              aria-label="处理进度"
            />
            <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: 8 }}>
              <Text size="small" type="tertiary">
                已用时间: {elapsedTime}秒
              </Text>
              <Text size="small" type="tertiary">
                预计时间: {estimatedTime}秒
              </Text>
            </div>
          </div>
        )}

        {/* 完成信息 */}
        {status === 'completed' && actualTime && (
          <div
            style={{
              padding: 16,
              background: 'rgba(var(--semi-green-5), 0.1)',
              borderRadius: 8,
              border: '1px solid var(--semi-color-success)',
            }}
          >
            <Space>
              <IconTickCircle style={{ color: 'var(--semi-color-success)' }} />
              <div>
                <Text strong>处理成功!</Text>
                <br />
                <Text size="small" type="tertiary">
                  用时 {actualTime} 秒
                </Text>
              </div>
            </Space>
          </div>
        )}

        {/* 错误信息 */}
        {status === 'failed' && errorMessage && (
          <div
            style={{
              padding: 16,
              background: 'rgba(var(--semi-red-5), 0.1)',
              borderRadius: 8,
              border: '1px solid var(--semi-color-danger)',
            }}
          >
            <Space vertical spacing={8}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                <IconAlertCircle style={{ color: 'var(--semi-color-danger)' }} />
                <Text strong>处理失败</Text>
              </div>
              <Paragraph style={{ margin: 0, color: '#666' }}>{errorMessage}</Paragraph>
              {errorSuggestion && (
                <div
                  style={{
                    padding: 8,
                    background: 'white',
                    borderRadius: 4,
                    marginTop: 8,
                  }}
                >
                  <Text size="small">💡 建议: {errorSuggestion}</Text>
                </div>
              )}
            </Space>
          </div>
        )}

        {/* 等待中提示 */}
        {status === 'pending' && (
          <div style={{ textAlign: 'center', padding: '20px 0' }}>
            <Spin size="large" />
            <br />
            <Text type="tertiary" style={{ marginTop: 16 }}>
              任务已提交,等待处理中...
            </Text>
          </div>
        )}

        {/* 处理中动画效果 */}
        {status === 'processing' && (
          <div style={{ textAlign: 'center', padding: '10px 0' }}>
            <div
              style={{
                display: 'inline-flex',
                gap: 8,
                alignItems: 'center',
              }}
            >
              <Spin />
              <Text type="tertiary">正在应用 {styleName} 风格,请稍候...</Text>
            </div>
          </div>
        )}
      </Space>
    </Card>
  )
}

export default StyleProgress
