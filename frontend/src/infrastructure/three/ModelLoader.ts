import * as THREE from 'three';
import { STLLoader } from 'three/examples/jsm/loaders/STLLoader.js';
import { OBJLoader } from 'three/examples/jsm/loaders/OBJLoader.js';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';
import { MTLLoader } from 'three/examples/jsm/loaders/MTLLoader.js';

export interface LoadProgress {
  loaded: number
  total: number
  percentage: number
}

export type ProgressCallback = (progress: LoadProgress) => void
export type ErrorCallback = (error: Error) => void

export type ModelFormat = 'stl' | 'obj' | 'glb' | 'gltf';

export class ModelLoader {
  private stlLoader: STLLoader;
  private objLoader: OBJLoader;
  private gltfLoader: GLTFLoader;
  private mtlLoader: MTLLoader;

  constructor() {
    this.stlLoader = new STLLoader();
    this.objLoader = new OBJLoader();
    this.gltfLoader = new GLTFLoader();
    this.mtlLoader = new MTLLoader();
  }

  public async loadSTL(url: string, onProgress?: ProgressCallback): Promise<THREE.Mesh> {
    return new Promise((resolve, reject) => {
      this.stlLoader.load(
        url,
        (geometry) => {
          geometry.computeVertexNormals()
          geometry.center()

          const material = new THREE.MeshPhongMaterial({
            color: 0x4a90e2,
            specular: 0x111111,
            shininess: 100,
            flatShading: false,
          })

          const mesh = new THREE.Mesh(geometry, material)
          mesh.castShadow = true
          mesh.receiveShadow = true

          resolve(mesh)
        },
        (xhr) => {
          if (onProgress && xhr.lengthComputable) {
            const progress: LoadProgress = {
              loaded: xhr.loaded,
              total: xhr.total,
              percentage: (xhr.loaded / xhr.total) * 100,
            }
            onProgress(progress)
          }
        },
        (error) => {
          reject(new Error(`Failed to load STL file: ${error}`))
        }
      )
    })
  }

  public async loadSTLFromFile(file: File, onProgress?: ProgressCallback): Promise<THREE.Mesh> {
    return new Promise((resolve, reject) => {
      const reader = new FileReader()

      reader.onload = (event) => {
        const arrayBuffer = event.target?.result as ArrayBuffer

        try {
          const geometry = this.stlLoader.parse(arrayBuffer)
          geometry.computeVertexNormals()
          geometry.center()

          const material = new THREE.MeshPhongMaterial({
            color: 0x4a90e2,
            specular: 0x111111,
            shininess: 100,
            flatShading: false,
          })

          const mesh = new THREE.Mesh(geometry, material)
          mesh.castShadow = true
          mesh.receiveShadow = true

          resolve(mesh)
        } catch (error) {
          reject(new Error(`Failed to parse STL file: ${error}`))
        }
      }

      reader.onerror = () => {
        reject(new Error('Failed to read file'))
      }

      reader.onprogress = (event) => {
        if (onProgress && event.lengthComputable) {
          const progress: LoadProgress = {
            loaded: event.loaded,
            total: event.total,
            percentage: (event.loaded / event.total) * 100,
          }
          onProgress(progress)
        }
      }

      reader.readAsArrayBuffer(file)
    })
  }

<<<<<<< HEAD
  public async loadOBJ(
    url: string,
    mtlUrl?: string,
    onProgress?: ProgressCallback
  ): Promise<THREE.Group> {
    return new Promise(async (resolve, reject) => {
      try {
        if (mtlUrl) {
          const materials = await new Promise<MTLLoader.MaterialCreator>((resolveMtl, rejectMtl) => {
            this.mtlLoader.load(
              mtlUrl,
              (mtl) => {
                mtl.preload();
                resolveMtl(mtl);
              },
              undefined,
              (error) => rejectMtl(new Error(`Failed to load MTL file: ${error}`))
            );
          });

          this.objLoader.setMaterials(materials);
        }

        this.objLoader.load(
          url,
          (object) => {
            object.traverse((child) => {
              if (child instanceof THREE.Mesh) {
                child.castShadow = true;
                child.receiveShadow = true;
                child.geometry.computeVertexNormals();
              }
            });

            const box = new THREE.Box3().setFromObject(object);
            const center = box.getCenter(new THREE.Vector3());
            object.position.sub(center);

            resolve(object);
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
            reject(new Error(`Failed to load OBJ file: ${error}`));
          }
        );
      } catch (error) {
        reject(error);
      }
    });
  }

  public async loadGLB(
    url: string,
    onProgress?: ProgressCallback
  ): Promise<THREE.Group> {
    return new Promise((resolve, reject) => {
      this.gltfLoader.load(
        url,
        (gltf) => {
          const scene = gltf.scene;

          scene.traverse((child) => {
            if (child instanceof THREE.Mesh) {
              child.castShadow = true;
              child.receiveShadow = true;
            }
          });

          const box = new THREE.Box3().setFromObject(scene);
          const center = box.getCenter(new THREE.Vector3());
          scene.position.sub(center);

          resolve(scene);
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
          reject(new Error(`Failed to load GLB file: ${error}`));
        }
      );
    });
  }

  public async loadModel(
    url: string,
    format?: ModelFormat,
    mtlUrl?: string,
    onProgress?: ProgressCallback
  ): Promise<THREE.Mesh | THREE.Group> {
    const detectedFormat = format || this.detectFormat(url);

    switch (detectedFormat) {
      case 'stl':
        return this.loadSTL(url, onProgress);
      case 'obj':
        return this.loadOBJ(url, mtlUrl, onProgress);
      case 'glb':
      case 'gltf':
        return this.loadGLB(url, onProgress);
      default:
        throw new Error(`Unsupported model format: ${detectedFormat}`);
    }
  }

  private detectFormat(url: string): ModelFormat {
    const extension = url.split('.').pop()?.toLowerCase();
    
    switch (extension) {
      case 'stl':
        return 'stl';
      case 'obj':
        return 'obj';
      case 'glb':
        return 'glb';
      case 'gltf':
        return 'gltf';
      default:
        return 'stl';
    }
  }

  public getModelInfo(object: THREE.Mesh | THREE.Group): {
    vertexCount: number;
    triangleCount: number;
    boundingBox: THREE.Box3;
    dimensions: THREE.Vector3;
  } {
    const box = new THREE.Box3().setFromObject(object);
    const dimensions = box.getSize(new THREE.Vector3());

    let vertexCount = 0;
    let triangleCount = 0;

    object.traverse((child) => {
      if (child instanceof THREE.Mesh) {
        const geometry = child.geometry;
        vertexCount += geometry.attributes.position?.count || 0;
        triangleCount += geometry.index
          ? geometry.index.count / 3
          : (geometry.attributes.position?.count || 0) / 3;
      }
    });

    return {
      vertexCount,
      triangleCount,
      boundingBox: box,
      dimensions,
    }
  }
}
