/**
 * 风格化任务管理 Hook
 *
 * 管理风格化任务的完整生命周期
 */

import { useState, useCallback, useEffect, useRef } from 'react'
import { Toast } from '@douyinfe/semi-ui'
import type { TaskStatus, StylePreset, StyleTask, CreateStyleTaskRequest } from '../types'
import {
  getStylePresets,
  createStyleTask,
  getTaskStatus,
  downloadResult as downloadResultApi,
} from '../api/styleApi'

interface UseStyleTransferState {
  /** 可用的风格预设列表 */
  presets: StylePreset[]
  /** 预设列表加载状态 */
  presetsLoading: boolean
  /** 当前任务 */
  currentTask: StyleTask | null
  /** 任务处理状态 */
  taskStatus: TaskStatus | null
  /** 上传的图片文件 */
  uploadedFile: File | null
  /** 上传的图片预览URL */
  uploadedImageUrl: string | null
  /** 选中的风格ID */
  selectedStyleId: string | null
  /** 错误信息 */
  error: string | null
}

interface UseStyleTransferActions {
  /** 加载风格预设列表 */
  loadPresets: () => Promise<void>
  /** 上传图片 */
  uploadImage: (file: File) => void
  /** 选择风格 */
  selectStyle: (styleId: string) => void
  /** 开始风格化 */
  startStyleTransfer: () => Promise<void>
  /** 下载结果 */
  downloadResult: () => Promise<void>
  /** 重置状态 */
  reset: () => void
}

/**
 * 风格化任务管理 Hook
 *
 * @returns 状态和操作方法
 */
export const useStyleTransfer = (): [UseStyleTransferState, UseStyleTransferActions] => {
  const [state, setState] = useState<UseStyleTransferState>({
    presets: [],
    presetsLoading: false,
    currentTask: null,
    taskStatus: null,
    uploadedFile: null,
    uploadedImageUrl: null,
    selectedStyleId: null,
    error: null,
  })

  const pollingTimerRef = useRef<NodeJS.Timeout | null>(null)

  /**
   * 加载风格预设列表
   */
  const loadPresets = useCallback(async () => {
    setState((prev) => ({ ...prev, presetsLoading: true, error: null }))

    try {
      const response = await getStylePresets()
      setState((prev) => ({
        ...prev,
        presets: response.presets,
        presetsLoading: false,
      }))
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : '加载风格预设失败'
      setState((prev) => ({
        ...prev,
        presetsLoading: false,
        error: errorMessage,
      }))
      Toast.error(errorMessage)
    }
  }, [])

  /**
   * 上传图片
   */
  const uploadImage = useCallback((file: File) => {
    // 创建预览URL
    const previewUrl = URL.createObjectURL(file)

    setState((prev) => ({
      ...prev,
      uploadedFile: file,
      uploadedImageUrl: previewUrl,
      error: null,
    }))

    Toast.success('图片上传成功')
  }, [])

  /**
   * 选择风格
   */
  const selectStyle = useCallback((styleId: string) => {
    setState((prev) => ({
      ...prev,
      selectedStyleId: styleId,
      error: null,
    }))
  }, [])

  /**
   * 开始轮询任务状态
   */
  const startPolling = useCallback((taskId: string) => {
    // 清除之前的定时器
    if (pollingTimerRef.current) {
      clearInterval(pollingTimerRef.current)
    }

    let pollCount = 0
    const maxPolls = 60 // 最多轮询60次(2分钟)

    pollingTimerRef.current = setInterval(async () => {
      try {
        pollCount++

        const taskData = await getTaskStatus(taskId)

        setState((prev) => ({
          ...prev,
          currentTask: taskData,
          taskStatus: taskData.status,
        }))

        // 任务完成或失败,停止轮询
        if (taskData.status === 'completed' || taskData.status === 'failed') {
          if (pollingTimerRef.current) {
            clearInterval(pollingTimerRef.current)
            pollingTimerRef.current = null
          }

          if (taskData.status === 'completed') {
            Toast.success('风格化处理完成!')
          } else if (taskData.status === 'failed') {
            const errorMsg = taskData.error_info?.user_message || '处理失败'
            Toast.error(errorMsg)
          }
        }

        // 超过最大轮询次数
        if (pollCount >= maxPolls) {
          if (pollingTimerRef.current) {
            clearInterval(pollingTimerRef.current)
            pollingTimerRef.current = null
          }
          Toast.warning('任务处理超时,请稍后手动查询')
        }
      } catch (error) {
        console.error('轮询任务状态失败:', error)
      }
    }, 2000) // 每2秒轮询一次
  }, [])

  /**
   * 开始风格化处理
   */
  const startStyleTransfer = useCallback(async () => {
    if (!state.uploadedFile) {
      Toast.error('请先上传图片')
      return
    }

    if (!state.selectedStyleId) {
      Toast.error('请选择风格')
      return
    }

    setState((prev) => ({ ...prev, error: null }))

    try {
      const request: CreateStyleTaskRequest = {
        file: state.uploadedFile,
        style_preset_id: state.selectedStyleId,
      }

      Toast.info('正在创建风格化任务...')

      const response = await createStyleTask(request)

      setState((prev) => ({
        ...prev,
        taskStatus: response.status as TaskStatus,
      }))

      Toast.success('任务创建成功,开始处理')

      // 开始轮询任务状态
      startPolling(response.task_id)
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : '创建任务失败'
      setState((prev) => ({
        ...prev,
        error: errorMessage,
      }))
      Toast.error(errorMessage)
    }
  }, [state.uploadedFile, state.selectedStyleId, startPolling])

  /**
   * 下载结果
   */
  const downloadResult = useCallback(async () => {
    if (!state.currentTask || !state.currentTask.id) {
      Toast.error('没有可下载的结果')
      return
    }

    if (state.currentTask.status !== 'completed') {
      Toast.error('任务尚未完成')
      return
    }

    try {
      const styleName = state.presets.find((p) => p.id === state.selectedStyleId)?.name || 'styled'
      const filename = `${styleName}_${state.currentTask.id}.jpg`

      await downloadResultApi(state.currentTask.id, filename)

      Toast.success('下载成功')
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : '下载失败'
      Toast.error(errorMessage)
    }
  }, [state.currentTask, state.presets, state.selectedStyleId])

  /**
   * 重置状态
   */
  const reset = useCallback(() => {
    // 清除轮询定时器
    if (pollingTimerRef.current) {
      clearInterval(pollingTimerRef.current)
      pollingTimerRef.current = null
    }

    // 清除预览URL
    if (state.uploadedImageUrl) {
      URL.revokeObjectURL(state.uploadedImageUrl)
    }

    setState({
      presets: state.presets, // 保留预设列表
      presetsLoading: false,
      currentTask: null,
      taskStatus: null,
      uploadedFile: null,
      uploadedImageUrl: null,
      selectedStyleId: null,
      error: null,
    })

    Toast.info('已重置,可以开始新的风格化')
  }, [state.presets, state.uploadedImageUrl])

  /**
   * 组件卸载时清理
   */
  useEffect(() => {
    return () => {
      if (pollingTimerRef.current) {
        clearInterval(pollingTimerRef.current)
      }
      if (state.uploadedImageUrl) {
        URL.revokeObjectURL(state.uploadedImageUrl)
      }
    }
  }, [state.uploadedImageUrl])

  /**
   * 初始化时加载预设列表
   */
  useEffect(() => {
    loadPresets()
  }, [loadPresets])

  return [
    state,
    {
      loadPresets,
      uploadImage,
      selectStyle,
      startStyleTransfer,
      downloadResult,
      reset,
    },
  ]
}

export default useStyleTransfer
