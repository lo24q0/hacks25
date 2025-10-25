import React, { useEffect, useState } from 'react';
import { ModelStatus } from '../types/model.types';
import type { Model3D } from '../types/model.types';

interface GenerationProgressProps {
  taskId: string | null;
  model: Model3D | null;
  onPollStatus: (id: string) => Promise<Model3D>;
  pollInterval?: number;
}

const GenerationProgress: React.FC<GenerationProgressProps> = ({
  taskId,
  model,
  onPollStatus,
  pollInterval = 3000,
}) => {
  const [isPolling, setIsPolling] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!taskId || !model?.id) {
      setIsPolling(false);
      return;
    }

    if (
      model.status === ModelStatus.COMPLETED ||
      model.status === ModelStatus.FAILED
    ) {
      setIsPolling(false);
      return;
    }

    setIsPolling(true);
    const intervalId = setInterval(async () => {
      try {
        const updatedModel = await onPollStatus(model.id);
        
        if (
          updatedModel.status === ModelStatus.COMPLETED ||
          updatedModel.status === ModelStatus.FAILED
        ) {
          setIsPolling(false);
          clearInterval(intervalId);
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : '获取任务状态失败');
        setIsPolling(false);
        clearInterval(intervalId);
      }
    }, pollInterval);

    return () => {
      clearInterval(intervalId);
      setIsPolling(false);
    };
  }, [taskId, model?.id, model?.status, onPollStatus, pollInterval]);

  if (!model) {
    return null;
  }

  const getStatusInfo = () => {
    switch (model.status) {
      case ModelStatus.PENDING:
        return {
          color: 'blue',
          icon: (
            <svg className="animate-spin h-5 w-5" fill="none" viewBox="0 0 24 24">
              <circle
                className="opacity-25"
                cx="12"
                cy="12"
                r="10"
                stroke="currentColor"
                strokeWidth="4"
              />
              <path
                className="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
              />
            </svg>
          ),
          text: '任务已创建,等待处理...',
        };
      case ModelStatus.PROCESSING:
        return {
          color: 'blue',
          icon: (
            <svg className="animate-spin h-5 w-5" fill="none" viewBox="0 0 24 24">
              <circle
                className="opacity-25"
                cx="12"
                cy="12"
                r="10"
                stroke="currentColor"
                strokeWidth="4"
              />
              <path
                className="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
              />
            </svg>
          ),
          text: '正在生成 3D 模型...',
        };
      case ModelStatus.COMPLETED:
        return {
          color: 'green',
          icon: (
            <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M5 13l4 4L19 7"
              />
            </svg>
          ),
          text: '模型生成完成!',
        };
      case ModelStatus.FAILED:
        return {
          color: 'red',
          icon: (
            <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
          ),
          text: '模型生成失败',
        };
      default:
        return {
          color: 'gray',
          icon: null,
          text: '未知状态',
        };
    }
  };

  const statusInfo = getStatusInfo();

  const getProgressPercentage = () => {
    switch (model.status) {
      case ModelStatus.PENDING:
        return 25;
      case ModelStatus.PROCESSING:
        return 75;
      case ModelStatus.COMPLETED:
        return 100;
      case ModelStatus.FAILED:
        return 100;
      default:
        return 0;
    }
  };

  const progress = getProgressPercentage();

  return (
    <div className="space-y-4">
      <div
        className={`
          p-4 rounded-lg border
          ${statusInfo.color === 'blue' ? 'bg-blue-50 border-blue-200' : ''}
          ${statusInfo.color === 'green' ? 'bg-green-50 border-green-200' : ''}
          ${statusInfo.color === 'red' ? 'bg-red-50 border-red-200' : ''}
          ${statusInfo.color === 'gray' ? 'bg-gray-50 border-gray-200' : ''}
        `}
      >
        <div className="flex items-center space-x-3">
          {statusInfo.icon && (
            <div
              className={`
                ${statusInfo.color === 'blue' ? 'text-blue-600' : ''}
                ${statusInfo.color === 'green' ? 'text-green-600' : ''}
                ${statusInfo.color === 'red' ? 'text-red-600' : ''}
                ${statusInfo.color === 'gray' ? 'text-gray-600' : ''}
              `}
            >
              {statusInfo.icon}
            </div>
          )}
          <div className="flex-1">
            <p
              className={`
                font-medium
                ${statusInfo.color === 'blue' ? 'text-blue-900' : ''}
                ${statusInfo.color === 'green' ? 'text-green-900' : ''}
                ${statusInfo.color === 'red' ? 'text-red-900' : ''}
                ${statusInfo.color === 'gray' ? 'text-gray-900' : ''}
              `}
            >
              {statusInfo.text}
            </p>
            {model.status === ModelStatus.FAILED && model.errorMessage && (
              <p className="text-sm text-red-600 mt-1">{model.errorMessage}</p>
            )}
            {isPolling && (
              <p className="text-xs text-gray-500 mt-1">
                正在轮询任务状态 (每 {pollInterval / 1000} 秒)...
              </p>
            )}
          </div>
        </div>
      </div>

      <div className="space-y-2">
        <div className="flex justify-between text-sm text-gray-600">
          <span>进度</span>
          <span>{progress}%</span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2 overflow-hidden">
          <div
            className={`
              h-full rounded-full transition-all duration-500
              ${statusInfo.color === 'blue' ? 'bg-blue-600' : ''}
              ${statusInfo.color === 'green' ? 'bg-green-600' : ''}
              ${statusInfo.color === 'red' ? 'bg-red-600' : ''}
              ${statusInfo.color === 'gray' ? 'bg-gray-600' : ''}
            `}
            style={{ width: `${progress}%` }}
          />
        </div>
      </div>

      {error && (
        <div className="p-3 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-sm text-red-600">{error}</p>
        </div>
      )}

      {model.status === ModelStatus.COMPLETED && model.metadata && (
        <div className="p-4 bg-gray-50 rounded-lg space-y-2">
          <h4 className="text-sm font-medium text-gray-700">模型信息</h4>
          <div className="grid grid-cols-2 gap-2 text-sm">
            {model.metadata.dimensions && (
              <div>
                <span className="text-gray-500">尺寸:</span>{' '}
                <span className="text-gray-900">
                  {model.metadata.dimensions.x.toFixed(1)} × {model.metadata.dimensions.y.toFixed(1)} × {model.metadata.dimensions.z.toFixed(1)} mm
                </span>
              </div>
            )}
            {model.metadata.triangleCount && (
              <div>
                <span className="text-gray-500">三角面数:</span>{' '}
                <span className="text-gray-900">{model.metadata.triangleCount.toLocaleString()}</span>
              </div>
            )}
            {model.metadata.volume && (
              <div>
                <span className="text-gray-500">体积:</span>{' '}
                <span className="text-gray-900">{model.metadata.volume.toFixed(2)} mm³</span>
              </div>
            )}
            {model.metadata.isManifold !== undefined && (
              <div>
                <span className="text-gray-500">可打印:</span>{' '}
                <span className={model.metadata.isManifold ? 'text-green-600' : 'text-red-600'}>
                  {model.metadata.isManifold ? '是' : '否'}
                </span>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default GenerationProgress;
