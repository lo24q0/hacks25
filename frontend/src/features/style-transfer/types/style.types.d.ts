/**
 * 风格化功能相关类型定义
 */

/**
 * 任务状态枚举
 */
export type TaskStatus = 'pending' | 'processing' | 'completed' | 'failed'

/**
 * 风格预设接口
 */
export interface StylePreset {
  /** 风格ID */
  id: string
  /** 中文名称 */
  name: string
  /** 英文名称 */
  name_en: string
  /** 描述 */
  description: string
  /** 预览图URL */
  preview_image: string
  /** 标签 */
  tags: string[]
  /** 推荐强度 */
  recommended_strength: number
  /** 预计处理时间(秒) */
  estimated_time: number
}

/**
 * 风格预设列表响应
 */
export interface StylePresetsResponse {
  presets: StylePreset[]
  total: number
}

/**
 * 任务元数据
 */
export interface StyleTaskMetadata {
  /** 风格预设ID */
  style_preset_id: string
  /** 风格预设名称 */
  style_preset_name: string
  /** 预计时间 */
  estimated_time: number
  /** 实际处理时间 */
  actual_time?: number
  /** 腾讯云请求ID */
  tencent_request_id?: string
  /** 创建时间 */
  created_at: string
  /** 完成时间 */
  completed_at?: string
}

/**
 * 错误信息
 */
export interface ErrorInfo {
  /** 错误码 */
  error_code: string
  /** 错误消息 */
  error_message: string
  /** 腾讯云错误码 */
  tencent_error_code?: string
  /** 用户友好的错误提示 */
  user_message?: string
  /** 解决建议 */
  suggestion?: string
  /** 是否可重试 */
  is_retryable: boolean
}

/**
 * 风格化任务
 */
export interface StyleTask {
  /** 任务ID */
  id: string
  /** 输入图片路径 */
  image_path: string
  /** 风格预设ID */
  style_preset_id: string
  /** 任务状态 */
  status: TaskStatus
  /** 结果图片路径 */
  result_path?: string
  /** 元数据 */
  metadata: StyleTaskMetadata
  /** 错误信息 */
  error_info?: ErrorInfo
  /** 创建时间 */
  created_at: string
  /** 更新时间 */
  updated_at: string
}

/**
 * 创建风格化任务请求
 */
export interface CreateStyleTaskRequest {
  /** 图片文件 */
  file: File
  /** 风格预设ID */
  style_preset_id: string
}

/**
 * 创建风格化任务响应
 */
export interface StyleTransferResponse {
  /** 任务ID */
  task_id: string
  /** 任务状态 */
  status: TaskStatus
  /** 提示消息 */
  message: string
}

/**
 * 任务状态响应
 */
export interface StyleTaskResponse {
  id: string
  image_path: string
  style_preset_id: string
  status: TaskStatus
  result_path?: string
  metadata: StyleTaskMetadata
  error_info?: ErrorInfo
  created_at: string
  updated_at: string
}
