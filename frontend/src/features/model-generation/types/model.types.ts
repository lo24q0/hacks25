export enum SourceType {
  TEXT = 'text',
  IMAGE = 'image',
}

export enum ModelStatus {
  PENDING = 'pending',
  PROCESSING = 'processing',
  COMPLETED = 'completed',
  FAILED = 'failed',
}

export interface ModelMetadata {
  dimensions?: {
    x: number;
    y: number;
    z: number;
  };
  volume?: number;
  triangleCount?: number;
  vertexCount?: number;
  isManifold?: boolean;
}

export interface Model3D {
  id: string;
  sourceType: SourceType;
  sourceData: {
    textPrompt?: string;
    imagePaths?: string[];
    stylePreset?: string;
  };
  status: ModelStatus;
  filePath?: string;
  thumbnailPath?: string;
  metadata?: ModelMetadata;
  errorMessage?: string;
  createdAt: string;
  updatedAt: string;
}

export interface GenerateModelRequest {
  sourceType: SourceType;
  textPrompt?: string;
  imagePaths?: string[];
  stylePreset?: string;
}

export interface GenerateModelResponse {
  taskId: string;
  status: ModelStatus;
  model?: Model3D;
}
