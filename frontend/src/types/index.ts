/**
 * Type Definitions
 */

export enum ProjectStatus {
  DRAFT = 'draft',
  PROCESSING_SCRIPT = 'processing_script',
  GENERATING_IMAGES = 'generating_images',
  CREATING_VIDEO = 'creating_video',
  COMPLETED = 'completed',
  FAILED = 'failed',
}

export interface Project {
  id: string
  title: string
  description?: string
  original_script: string
  status: ProjectStatus
  style?: string
  duration_target?: number
  created_at: string
  updated_at: string
}

export interface Scene {
  id: string
  project_id: string
  order: number
  duration?: number
  title?: string
  description: string
  dialogue?: string
  image_prompt?: string
  image_asset_id?: string
  video_asset_id?: string
  created_at: string
  updated_at?: string
}

export enum AssetType {
  IMAGE = 'image',
  VIDEO = 'video',
  AUDIO = 'audio',
  DOCUMENT = 'document',
}

export enum AssetStatus {
  PENDING = 'pending',
  PROCESSING = 'processing',
  READY = 'ready',
  FAILED = 'failed',
}

export interface Asset {
  id: string
  project_id: string
  type: AssetType
  status: AssetStatus
  filename: string
  original_filename?: string
  file_path?: string
  file_size?: number
  mime_type?: string
  width?: number
  height?: number
  duration?: number
  metadata?: Record<string, any>
  generated_by?: string
  generation_prompt?: string
  generation_params?: Record<string, any>
  created_at: string
  updated_at?: string
}

export interface CreateProjectData {
  title: string
  description?: string
  original_script: string
  style?: string
  duration_target?: number
}
