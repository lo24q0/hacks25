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
    x: number;
    y: number;
    z: number;
  };
  volume?: number;
  triangle_count?: number;
  vertex_count?: number;
  is_manifold?: boolean;
  bounding_box?: {
    min_point: [number, number, number];
    max_point: [number, number, number];
  };
}

export interface Model3D {
  id: string;
  source_type: SourceType;
  status: ModelStatus;
  file_path?: string;
  thumbnail_path?: string;
  metadata?: ModelMetadata;
  error_message?: string;
  created_at: string;
  updated_at: string;
}

export interface GenerateModelResponse {
  id: string;
  source_type: SourceType;
  status: ModelStatus;
  file_path?: string;
  thumbnail_path?: string;
  metadata?: ModelMetadata;
  error_message?: string;
  created_at: string;
  updated_at: string;
}
