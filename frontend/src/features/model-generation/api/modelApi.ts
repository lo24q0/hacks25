import { apiClient } from '@/infrastructure/api/client'
import type { GenerateModelResponse, Model3D } from '../types/model.types'

export const modelApi = {
  generateFromText: async (textPrompt: string): Promise<GenerateModelResponse> => {
    const response = await apiClient.post<GenerateModelResponse>('/api/v1/models/generate/text', {
      prompt: textPrompt,
    })
    return response.data
  },

  generateFromImage: async (imagePaths: string[]): Promise<GenerateModelResponse> => {
    const response = await apiClient.post<GenerateModelResponse>('/api/v1/models/generate/image', {
      image_paths: imagePaths,
    })
    return response.data
  },

  getModel: async (id: string): Promise<Model3D> => {
    const response = await apiClient.get<Model3D>(`/api/v1/models/${id}`)
    return response.data
  },

  downloadModel: async (id: string): Promise<Blob> => {
    const response = await apiClient.get<Blob>(`/api/v1/models/${id}/download`, {
      responseType: 'blob',
    })
    return response.data
  },

  deleteModel: async (id: string): Promise<void> => {
    await apiClient.delete(`/api/v1/models/${id}`)
  },

  getTaskStatus: async (
    taskId: string
  ): Promise<{
    task_id: string
    state: string
    ready: boolean
    info?: { progress?: number }
    result?: { model_files?: { glb?: string }; file_path?: string }
    error?: string
  }> => {
    const response = await apiClient.get(`/api/v1/models/task/${taskId}`)
    return response.data
  },
}
