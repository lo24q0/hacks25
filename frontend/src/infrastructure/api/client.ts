import axios, { AxiosError } from 'axios';
import type { AxiosInstance, InternalAxiosRequestConfig, AxiosResponse } from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
const API_TIMEOUT = 30000

export const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: API_TIMEOUT,
  headers: {
    'Content-Type': 'application/json',
  },
})

apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = localStorage.getItem('authToken')
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`
    }

    console.log(`[API Request] ${config.method?.toUpperCase()} ${config.url}`)
    return config
  },
  (error: AxiosError) => {
    console.error('[API Request Error]', error)
    return Promise.reject(error)
  }
)

apiClient.interceptors.response.use(
  (response: AxiosResponse) => {
    console.log(
      `[API Response] ${response.config.method?.toUpperCase()} ${response.config.url} - ${
        response.status
      }`
    )
    return response
  },
  (error: AxiosError) => {
    if (error.response) {
      console.error(
        `[API Error] ${error.response.status} - ${error.response.config.method?.toUpperCase()} ${
          error.response.config.url
        }`,
        error.response.data
      )

      if (error.response.status === 401) {
        localStorage.removeItem('authToken')
        window.location.href = '/login'
      }

      if (error.response.status === 429) {
        console.warn('[API] Rate limit exceeded')
      }
    } else if (error.request) {
      console.error('[API Error] No response received', error.request)
    } else {
      console.error('[API Error]', error.message)
    }

    return Promise.reject(error)
  }
)

export default apiClient
