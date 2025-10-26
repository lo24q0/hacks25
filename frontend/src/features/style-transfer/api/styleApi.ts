/**
 * 风格化 API 调用封装
 */

import apiClient from '@/infrastructure/api/client'
import type {
  StylePresetsResponse,
  StylePreset,
  CreateStyleTaskRequest,
  StyleTransferResponse,
  StyleTaskResponse,
} from '../types'

/**
 * 获取可用的风格预设列表
 *
 * @returns 风格预设列表
 */
export async function getStylePresets(): Promise<StylePresetsResponse> {
  const response = await apiClient.get<StylePresetsResponse>('/api/v1/styles/presets')
  return response.data
}

/**
 * 获取指定的风格预设
 *
 * @param presetId 风格预设ID
 * @returns 风格预设详情
 */
export async function getStylePreset(presetId: string): Promise<StylePreset> {
  const response = await apiClient.get<StylePreset>(`/api/v1/styles/presets/${presetId}`)
  return response.data
}

/**
 * 创建风格化任务
 *
 * @param request 创建任务请求
 * @returns 任务创建响应
 */
export async function createStyleTask(
  request: CreateStyleTaskRequest
): Promise<StyleTransferResponse> {
  const formData = new FormData()
  formData.append('file', request.file)
  formData.append('style_preset_id', request.style_preset_id)

  const response = await apiClient.post<StyleTransferResponse>(
    '/api/v1/styles/transfer',
    formData,
    {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    }
  )

  return response.data
}

/**
 * 查询任务状态
 *
 * @param taskId 任务ID
 * @returns 任务状态响应
 */
export async function getTaskStatus(taskId: string): Promise<StyleTaskResponse> {
  const response = await apiClient.get<StyleTaskResponse>(`/api/v1/styles/tasks/${taskId}`)
  return response.data
}

/**
 * 获取结果图片下载链接
 *
 * @param taskId 任务ID
 * @returns 下载链接
 */
export function getResultDownloadUrl(taskId: string): string {
  return `${apiClient.defaults.baseURL}/api/v1/styles/tasks/${taskId}/result`
}

/**
 * 下载结果图片
 *
 * @param taskId 任务ID
 * @param filename 保存的文件名
 */
export async function downloadResult(taskId: string, filename: string): Promise<void> {
  const response = await apiClient.get(`/api/v1/styles/tasks/${taskId}/result`, {
    responseType: 'blob',
  })

  // 创建下载链接
  const url = window.URL.createObjectURL(new Blob([response.data]))
  const link = document.createElement('a')
  link.href = url
  link.setAttribute('download', filename)
  document.body.appendChild(link)
  link.click()
  link.remove()
  window.URL.revokeObjectURL(url)
}
