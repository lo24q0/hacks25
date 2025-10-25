import { useState, useCallback } from 'react';
import { modelApi } from '../api/modelApi';
import type { Model3D } from '../types/model.types';

export const useModelGeneration = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [model, setModel] = useState<Model3D | null>(null);
  const [taskId, setTaskId] = useState<string | null>(null);

  const generateFromText = useCallback(async (textPrompt: string) => {
    try {
      setLoading(true);
      setError(null);
      const response = await modelApi.generateFromText(textPrompt);
      setTaskId(response.taskId);
      setModel(response.model || null);
      return response;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to generate model';
      setError(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const generateFromImage = useCallback(async (imagePaths: string[]) => {
    try {
      setLoading(true);
      setError(null);
      const response = await modelApi.generateFromImage(imagePaths);
      setTaskId(response.taskId);
      setModel(response.model || null);
      return response;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to generate model';
      setError(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const pollModelStatus = useCallback(async (id: string) => {
    try {
      const updatedModel = await modelApi.getModel(id);
      setModel(updatedModel);
      return updatedModel;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to fetch model status';
      setError(errorMessage);
      throw err;
    }
  }, []);

  const downloadModel = useCallback(async (id: string) => {
    try {
      setLoading(true);
      const blob = await modelApi.downloadModel(id);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `model-${id}.stl`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to download model';
      setError(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  return {
    loading,
    error,
    model,
    taskId,
    generateFromText,
    generateFromImage,
    pollModelStatus,
    downloadModel,
  };
};
