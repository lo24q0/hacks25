export const API_ENDPOINTS = {
  models: {
    generateText: '/api/v1/models/generate/text',
    generateImage: '/api/v1/models/generate/image',
    get: (id: string) => `/api/v1/models/${id}`,
    download: (id: string) => `/api/v1/models/${id}/download`,
    delete: (id: string) => `/api/v1/models/${id}`,
    list: '/api/v1/models',
  },
  
  files: {
    upload: '/api/v1/files/upload',
    download: (objectKey: string) => `/api/v1/files/${objectKey}`,
    metadata: (objectKey: string) => `/api/v1/files/${objectKey}/metadata`,
    delete: (objectKey: string) => `/api/v1/files/${objectKey}`,
    cleanup: '/api/v1/files/cleanup',
  },
  
  styles: {
    transfer: '/api/v1/styles/transfer',
    presets: '/api/v1/styles/presets',
    getTask: (id: string) => `/api/v1/styles/tasks/${id}`,
  },
  
  prints: {
    slice: '/api/v1/prints/slice',
    printers: '/api/v1/prints/printers',
    getTask: (id: string) => `/api/v1/prints/tasks/${id}`,
    getGCode: (id: string) => `/api/v1/prints/tasks/${id}/gcode`,
  },
  
  auth: {
    register: '/api/v1/auth/register',
    login: '/api/v1/auth/login',
    me: '/api/v1/users/me',
    quota: '/api/v1/users/me/quota',
  },
} as const;
