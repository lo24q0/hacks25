import * as THREE from 'three';
import { STLLoader } from 'three/examples/jsm/loaders/STLLoader.js';

export interface LoadProgress {
  loaded: number;
  total: number;
  percentage: number;
}

export type ProgressCallback = (progress: LoadProgress) => void;
export type ErrorCallback = (error: Error) => void;

export class ModelLoader {
  private stlLoader: STLLoader;

  constructor() {
    this.stlLoader = new STLLoader();
  }

  public async loadSTL(
    url: string,
    onProgress?: ProgressCallback
  ): Promise<THREE.Mesh> {
    return new Promise((resolve, reject) => {
      this.stlLoader.load(
        url,
        (geometry) => {
          geometry.computeVertexNormals();
          geometry.center();

          const material = new THREE.MeshPhongMaterial({
            color: 0x4a90e2,
            specular: 0x111111,
            shininess: 100,
            flatShading: false,
          });

          const mesh = new THREE.Mesh(geometry, material);
          mesh.castShadow = true;
          mesh.receiveShadow = true;

          resolve(mesh);
        },
        (xhr) => {
          if (onProgress && xhr.lengthComputable) {
            const progress: LoadProgress = {
              loaded: xhr.loaded,
              total: xhr.total,
              percentage: (xhr.loaded / xhr.total) * 100,
            };
            onProgress(progress);
          }
        },
        (error) => {
          reject(new Error(`Failed to load STL file: ${error}`));
        }
      );
    });
  }

  public async loadSTLFromFile(
    file: File,
    onProgress?: ProgressCallback
  ): Promise<THREE.Mesh> {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();

      reader.onload = (event) => {
        const arrayBuffer = event.target?.result as ArrayBuffer;
        
        try {
          const geometry = this.stlLoader.parse(arrayBuffer);
          geometry.computeVertexNormals();
          geometry.center();

          const material = new THREE.MeshPhongMaterial({
            color: 0x4a90e2,
            specular: 0x111111,
            shininess: 100,
            flatShading: false,
          });

          const mesh = new THREE.Mesh(geometry, material);
          mesh.castShadow = true;
          mesh.receiveShadow = true;

          resolve(mesh);
        } catch (error) {
          reject(new Error(`Failed to parse STL file: ${error}`));
        }
      };

      reader.onerror = () => {
        reject(new Error('Failed to read file'));
      };

      reader.onprogress = (event) => {
        if (onProgress && event.lengthComputable) {
          const progress: LoadProgress = {
            loaded: event.loaded,
            total: event.total,
            percentage: (event.loaded / event.total) * 100,
          };
          onProgress(progress);
        }
      };

      reader.readAsArrayBuffer(file);
    });
  }

  public getModelInfo(mesh: THREE.Mesh): {
    vertexCount: number;
    triangleCount: number;
    boundingBox: THREE.Box3;
    dimensions: THREE.Vector3;
  } {
    const geometry = mesh.geometry;
    const box = new THREE.Box3().setFromObject(mesh);
    const dimensions = box.getSize(new THREE.Vector3());

    const vertexCount = geometry.attributes.position?.count || 0;
    const triangleCount = geometry.index
      ? geometry.index.count / 3
      : vertexCount / 3;

    return {
      vertexCount,
      triangleCount,
      boundingBox: box,
      dimensions,
    };
  }
}
