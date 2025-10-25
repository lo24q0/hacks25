export const SourceType = {
  TEXT: 'text',
  IMAGE: 'image',
} as const;

export type SourceType = typeof SourceType[keyof typeof SourceType];

export const ModelStatus = {
  PENDING: 'pending',
  PROCESSING: 'processing',
  COMPLETED: 'completed',
  FAILED: 'failed',
} as const;

export type ModelStatus = typeof ModelStatus[keyof typeof ModelStatus];

export interface ModelMetadata {
  dimensions?: {
    x: number
    y: number
    z: number
  }
  volume?: number
  triangle_count?: number
  vertex_count?: number
  is_manifold?: boolean
  bounding_box?: {
    min_point: [number, number, number]
    max_point: [number, number, number]
  }
}

export interface Model3D {
  id: string
  source_type: SourceType
  status: ModelStatus
  file_path?: string
  thumbnail_path?: string
  metadata?: ModelMetadata
  error_message?: string
  celery_task_id?: string
  model_files?: {
    glb?: string
    obj?: string
    fbx?: string
    mtl?: string
  }
  created_at: string
  updated_at: string
}

export interface GenerateModelRequest {
  prompt?: string
  image_paths?: string[]
  style_preset?: string
}

export interface GenerateModelResponse {
  id: string
  source_type: SourceType
  status: ModelStatus
  file_path?: string
  thumbnail_path?: string
  metadata?: ModelMetadata
  error_message?: string
  celery_task_id?: string
  taskId?: string  // 添加 taskId 属性
  model?: Model3D  // 添加 model 属性
  model_files?: {
    glb?: string
    obj?: string
    fbx?: string
    mtl?: string
  }
  created_at: string
  updated_at: string
}
