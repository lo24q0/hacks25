/**
 * 图片风格化页面
 *
 * 整合所有风格化功能的主页面
 */

import React from 'react'
import { Layout, Typography, Steps, Space, Button, Card } from '@douyinfe/semi-ui'
import { IconRefresh } from '@douyinfe/semi-icons'
import { StyleImageUpload } from '../components/StyleImageUpload'
import { StyleSelector } from '../components/StyleSelector'
import { StyleProgress } from '../components/StyleProgress'
import { StylePreview } from '../components/StylePreview'
import { useStyleTransfer } from '../hooks/useStyleTransfer'

const { Content } = Layout
const { Title, Paragraph } = Typography

/**
 * 图片风格化页面组件
 */
export const StyleTransferPage: React.FC = () => {
  const [state, actions] = useStyleTransfer()

  // 当前步骤
  const getCurrentStep = () => {
    if (!state.uploadedFile) return 0
    // 只要还没开始处理(无taskStatus),就停留在步骤1(选择风格并点击开始按钮)
    if (!state.taskStatus) return 1
    // 处理完成,进入步骤3(查看结果)
    if (state.taskStatus === 'completed') return 3
    // 处理中(pending/processing/failed),显示步骤2(处理进度)
    return 2
  }

  const currentStep = getCurrentStep()

  // 选中的风格名称
  const selectedStyleName =
    state.presets.find((p) => p.id === state.selectedStyleId)?.name || '未选择'

  // 获取结果图片URL
  const getResultImageUrl = () => {
    if (state.currentTask?.id) {
      const url = `${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'}/api/v1/styles/tasks/${
        state.currentTask.id
      }/result`
      console.log('[StyleTransferPage] Result image URL:', url)
      console.log('[StyleTransferPage] Task ID:', state.currentTask.id)
      console.log('[StyleTransferPage] Task status:', state.currentTask.status)
      console.log('[StyleTransferPage] Result path:', state.currentTask.result_path)
      return url
    }
    console.warn('[StyleTransferPage] No task ID available, currentTask:', state.currentTask)
    return ''
  }

  return (
    <Layout style={{ minHeight: '100vh', background: '#f5f5f5' }}>
      <Content style={{ padding: '40px 24px' }}>
        <div style={{ maxWidth: 1400, margin: '0 auto' }}>
          {/* 页面标题 */}
          <div style={{ marginBottom: 40, textAlign: 'center' }}>
            <Title heading={2}>🎨 图片风格化</Title>
            <Paragraph type="secondary" style={{ fontSize: 16 }}>
              上传图片,选择风格,将普通照片转换为艺术作品
            </Paragraph>
          </div>

          {/* 步骤指示器 */}
          <Card style={{ marginBottom: 30 }}>
            <Steps current={currentStep} type="basic">
              <Steps.Step title="上传图片" description="选择要风格化的图片" />
              <Steps.Step title="选择风格" description="从5种风格中选择" />
              <Steps.Step title="处理中" description="AI处理约15-30秒" />
              <Steps.Step title="查看结果" description="下载风格化图片" />
            </Steps>
          </Card>

          {/* 主要内容区域 */}
          <Space vertical spacing={30} style={{ width: '100%' }}>
            {/* 步骤 1: 上传图片 */}
            {currentStep === 0 && (
              <Card>
                <Title heading={4} style={{ marginBottom: 20 }}>
                  步骤 1: 上传图片
                </Title>
                <StyleImageUpload
                  onFileChange={(file) => {
                    if (file) {
                      actions.uploadImage(file)
                    }
                  }}
                />
                <div style={{ marginTop: 16, padding: 16, background: '#f8f9fa', borderRadius: 8 }}>
                  <Paragraph type="tertiary" style={{ margin: 0, fontSize: 13 }}>
                    💡 提示:
                    <br />
                    - 支持 JPG, PNG, WEBP 格式
                    <br />
                    - 文件大小不超过 10MB
                    <br />
                    - 建议分辨率: 1024x1024 到 2048x2048
                    <br />- 动漫和3D卡通风格适合人物照片,其他风格适合风景照片
                  </Paragraph>
                </div>
              </Card>
            )}

            {/* 步骤 2: 选择风格 */}
            {currentStep === 1 && (
              <>
                {/* 显示上传的图片预览 */}
                <Card>
                  <Title heading={4} style={{ marginBottom: 16 }}>
                    已上传的图片
                  </Title>
                  <div
                    style={{
                      width: '100%',
                      maxWidth: 400,
                      height: 300,
                      background: '#f0f0f0',
                      borderRadius: 8,
                      overflow: 'hidden',
                      margin: '0 auto',
                    }}
                  >
                    {state.uploadedImageUrl && (
                      <img
                        src={state.uploadedImageUrl}
                        alt="上传的图片"
                        style={{
                          width: '100%',
                          height: '100%',
                          objectFit: 'contain',
                        }}
                      />
                    )}
                  </div>
                  <div style={{ textAlign: 'center', marginTop: 16 }}>
                    <Button
                      type="tertiary"
                      onClick={() => {
                        actions.reset()
                      }}
                    >
                      重新上传
                    </Button>
                  </div>
                </Card>

                {/* 风格选择器 */}
                <Card>
                  <StyleSelector
                    presets={state.presets}
                    selectedStyleId={state.selectedStyleId || undefined}
                    onSelect={actions.selectStyle}
                    loading={state.presetsLoading}
                  />

                  {/* 开始按钮 */}
                  {state.selectedStyleId && (
                    <div style={{ marginTop: 24, textAlign: 'center' }}>
                      <Button
                        type="primary"
                        theme="solid"
                        size="large"
                        onClick={actions.startStyleTransfer}
                        style={{ minWidth: 200 }}
                      >
                        开始风格化
                      </Button>
                    </div>
                  )}
                </Card>
              </>
            )}

            {/* 步骤 3: 处理中 */}
            {currentStep === 2 && state.taskStatus && state.taskStatus !== 'completed' && (
              <StyleProgress
                status={state.taskStatus}
                styleName={selectedStyleName}
                estimatedTime={
                  state.presets.find((p) => p.id === state.selectedStyleId)?.estimated_time
                }
                actualTime={state.currentTask?.metadata?.actual_time}
                errorMessage={state.currentTask?.error_info?.user_message}
                errorSuggestion={state.currentTask?.error_info?.suggestion}
              />
            )}

            {/* 步骤 4: 查看结果 */}
            {currentStep === 3 && state.uploadedImageUrl && state.currentTask?.id && (
              <>
                <StylePreview
                  originalImageUrl={state.uploadedImageUrl}
                  styledImageUrl={getResultImageUrl()}
                  styleName={selectedStyleName}
                  onDownload={actions.downloadResult}
                />

                {/* 操作按钮 */}
                <Card>
                  <div style={{ display: 'flex', justifyContent: 'center', gap: 16 }}>
                    <Button icon={<IconRefresh />} size="large" onClick={actions.reset}>
                      开始新的风格化
                    </Button>
                    <Button type="primary" size="large" onClick={actions.downloadResult}>
                      下载风格化图片
                    </Button>
                  </div>
                </Card>
              </>
            )}
          </Space>
        </div>
      </Content>
    </Layout>
  )
}

export default StyleTransferPage
