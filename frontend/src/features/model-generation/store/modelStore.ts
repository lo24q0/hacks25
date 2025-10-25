import { create } from 'zustand'
import type { Model3D, ModelStatus } from '../types/model.types'

interface ModelState {
  currentModel: Model3D | null
  models: Model3D[]
  isGenerating: boolean
  error: string | null

  setCurrentModel: (model: Model3D | null) => void
  addModel: (model: Model3D) => void
  updateModel: (id: string, updates: Partial<Model3D>) => void
  removeModel: (id: string) => void
  setIsGenerating: (generating: boolean) => void
  setError: (error: string | null) => void
  clearModels: () => void
}

export const useModelStore = create<ModelState>((set) => ({
  currentModel: null,
  models: [],
  isGenerating: false,
  error: null,

  setCurrentModel: (model) => set({ currentModel: model }),

  addModel: (model) =>
    set((state) => ({
      models: [model, ...state.models],
      currentModel: model,
    })),

  updateModel: (id, updates) =>
    set((state) => {
      const updatedModels = state.models.map((model) =>
        model.id === id ? { ...model, ...updates } : model
      )

      const updatedCurrentModel =
        state.currentModel?.id === id ? { ...state.currentModel, ...updates } : state.currentModel

      return {
        models: updatedModels,
        currentModel: updatedCurrentModel,
      }
    }),

  removeModel: (id) =>
    set((state) => ({
      models: state.models.filter((model) => model.id !== id),
      currentModel: state.currentModel?.id === id ? null : state.currentModel,
    })),

  setIsGenerating: (generating) => set({ isGenerating: generating }),

  setError: (error) => set({ error }),

  clearModels: () => set({ models: [], currentModel: null, error: null }),
}))
