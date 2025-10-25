import { apiClient } from '@/infrastructure/api/client';

export interface FileUploadResponse {
  id: string;
  object_key: string;
  original_filename: string;
  content_type: string;
  size_bytes: number;
  download_url: string;
  created_at: string;
}

export const fileApi = {
  uploadFile: async (file: File, ttlHours?: number): Promise<FileUploadResponse> => {
    const formData = new FormData();
    formData.append('file', file);

    const params = ttlHours ? { ttl_hours: ttlHours } : {};

    const response = await apiClient.post<FileUploadResponse>(
      '/api/v1/files/upload',
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        params,
      }
    );
    return response.data;
  },

  uploadMultipleFiles: async (files: File[], ttlHours?: number): Promise<FileUploadResponse[]> => {
    const uploadPromises = files.map(file => fileApi.uploadFile(file, ttlHours));
    return Promise.all(uploadPromises);
  },

  downloadFile: async (objectKey: string): Promise<Blob> => {
    const response = await apiClient.get<Blob>(`/api/v1/files/${objectKey}`, {
      responseType: 'blob',
    });
    return response.data;
  },

  deleteFile: async (objectKey: string): Promise<void> => {
    await apiClient.delete(`/api/v1/files/${objectKey}`);
  },
};
