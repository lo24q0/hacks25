import { useEffect, useRef, useState } from 'react'
import { SceneManager, ModelLoader, LoadProgress } from '../../../infrastructure/three'

interface ModelPreviewProps {
  modelUrl?: string
  modelFile?: File
  className?: string
  onLoadComplete?: () => void
  onLoadError?: (error: Error) => void
}

export default function ModelPreview({
  modelUrl,
  modelFile,
  className = '',
  onLoadComplete,
  onLoadError,
}: ModelPreviewProps) {
  const containerRef = useRef<HTMLDivElement>(null)
  const sceneManagerRef = useRef<SceneManager | null>(null)
  const modelLoaderRef = useRef<ModelLoader | null>(null)

  const [isLoading, setIsLoading] = useState(false)
  const [loadProgress, setLoadProgress] = useState<LoadProgress | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [modelInfo, setModelInfo] = useState<{
    vertexCount: number
    triangleCount: number
    dimensions: { x: number; y: number; z: number }
  } | null>(null)

  useEffect(() => {
    if (!containerRef.current) return

    sceneManagerRef.current = new SceneManager(containerRef.current, {
      antialias: true,
      backgroundColor: 0xf0f0f0,
      enableShadows: true,
    })

    modelLoaderRef.current = new ModelLoader()

    return () => {
      sceneManagerRef.current?.dispose()
      sceneManagerRef.current = null
      modelLoaderRef.current = null
    }
  }, [])

  useEffect(() => {
    const loadModel = async () => {
      if (!sceneManagerRef.current || !modelLoaderRef.current) return
      if (!modelUrl && !modelFile) return

      setIsLoading(true)
      setError(null)
      setLoadProgress(null)

      try {
        const mesh = modelFile
          ? await modelLoaderRef.current.loadSTLFromFile(modelFile, (progress) =>
              setLoadProgress(progress)
            )
          : modelUrl
            ? await modelLoaderRef.current.loadSTL(modelUrl, (progress) =>
                setLoadProgress(progress)
              )
            : null

        if (mesh) {
          sceneManagerRef.current.addModel(mesh)

          const info = modelLoaderRef.current.getModelInfo(mesh)
          setModelInfo({
            vertexCount: info.vertexCount,
            triangleCount: Math.floor(info.triangleCount),
            dimensions: {
              x: parseFloat(info.dimensions.x.toFixed(2)),
              y: parseFloat(info.dimensions.y.toFixed(2)),
              z: parseFloat(info.dimensions.z.toFixed(2)),
            },
          })

          onLoadComplete?.()
        }
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : 'Failed to load model'
        setError(errorMessage)
        onLoadError?.(err instanceof Error ? err : new Error(errorMessage))
      } finally {
        setIsLoading(false)
        setLoadProgress(null)
      }
    }

    loadModel()
  }, [modelUrl, modelFile, onLoadComplete, onLoadError])

  return (
    <div className={`relative ${className}`}>
      <div
        ref={containerRef}
        className="w-full h-full min-h-[400px] rounded-lg overflow-hidden bg-gray-100"
      />

      {isLoading && (
        <div className="absolute inset-0 flex items-center justify-center bg-white/80 rounded-lg">
          <div className="text-center">
            <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mb-4"></div>
            {loadProgress && (
              <div className="text-sm text-gray-600">
                Loading: {loadProgress.percentage.toFixed(0)}%
              </div>
            )}
          </div>
        </div>
      )}

      {error && (
        <div className="absolute inset-0 flex items-center justify-center bg-white/90 rounded-lg">
          <div className="text-center p-6 max-w-md">
            <svg
              className="mx-auto h-12 w-12 text-red-500 mb-4"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
              />
            </svg>
            <h3 className="text-lg font-medium text-gray-900 mb-2">Failed to load model</h3>
            <p className="text-sm text-gray-600">{error}</p>
          </div>
        </div>
      )}

      {!isLoading && !error && modelInfo && (
        <div className="absolute bottom-4 left-4 bg-white/90 backdrop-blur-sm rounded-lg shadow-lg p-4">
          <h3 className="text-sm font-semibold text-gray-900 mb-2">Model Info</h3>
          <div className="space-y-1 text-xs text-gray-600">
            <div className="flex justify-between gap-4">
              <span>Triangles:</span>
              <span className="font-medium text-gray-900">
                {modelInfo.triangleCount.toLocaleString()}
              </span>
            </div>
            <div className="flex justify-between gap-4">
              <span>Vertices:</span>
              <span className="font-medium text-gray-900">
                {modelInfo.vertexCount.toLocaleString()}
              </span>
            </div>
            <div className="border-t border-gray-200 my-2 pt-2">
              <div className="font-medium text-gray-700 mb-1">Dimensions:</div>
              <div className="space-y-0.5">
                <div className="flex justify-between gap-4">
                  <span>X:</span>
                  <span className="font-medium text-gray-900">{modelInfo.dimensions.x} units</span>
                </div>
                <div className="flex justify-between gap-4">
                  <span>Y:</span>
                  <span className="font-medium text-gray-900">{modelInfo.dimensions.y} units</span>
                </div>
                <div className="flex justify-between gap-4">
                  <span>Z:</span>
                  <span className="font-medium text-gray-900">{modelInfo.dimensions.z} units</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {!isLoading && !error && !modelUrl && !modelFile && (
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="text-center text-gray-500">
            <svg
              className="mx-auto h-16 w-16 text-gray-400 mb-4"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"
              />
            </svg>
            <p className="text-sm">No model loaded</p>
            <p className="text-xs mt-1">Upload or generate a model to preview</p>
          </div>
        </div>
      )}

      {!isLoading && !error && (modelUrl || modelFile) && (
        <div className="absolute top-4 right-4 bg-white/90 backdrop-blur-sm rounded-lg shadow-lg p-3">
          <div className="text-xs text-gray-600">
            <div className="flex items-center gap-2 mb-1">
              <svg
                className="h-4 w-4 text-blue-600"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M15 15l-2 5L9 9l11 4-5 2zm0 0l5 5M7.188 2.239l.777 2.897M5.136 7.965l-2.898-.777M13.95 4.05l-2.122 2.122m-5.657 5.656l-2.12 2.122"
                />
              </svg>
              <span className="font-medium text-gray-900">Controls</span>
            </div>
            <ul className="space-y-0.5">
              <li>Rotate: Left Click + Drag</li>
              <li>Zoom: Scroll Wheel</li>
              <li>Pan: Right Click + Drag</li>
            </ul>
          </div>
        </div>
      )}
    </div>
  )
}
