import * as THREE from 'three'
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js'

export interface SceneConfig {
  antialias?: boolean
  backgroundColor?: number
  enableShadows?: boolean
}

export class SceneManager {
  private scene: THREE.Scene
  private camera: THREE.PerspectiveCamera
  private renderer: THREE.WebGLRenderer
  private controls: OrbitControls
  private animationFrameId: number | null = null
  private container: HTMLElement | null = null

  constructor(container: HTMLElement, config: SceneConfig = {}) {
    this.container = container

    this.scene = new THREE.Scene()
    this.scene.background = new THREE.Color(config.backgroundColor ?? 0xf0f0f0)

    const width = container.clientWidth
    const height = container.clientHeight

    this.camera = new THREE.PerspectiveCamera(75, width / height, 0.1, 1000)
    this.camera.position.set(0, 5, 10)
    this.camera.lookAt(0, 0, 0)

    this.renderer = new THREE.WebGLRenderer({
      antialias: config.antialias ?? true,
    })
    this.renderer.setSize(width, height)
    this.renderer.setPixelRatio(window.devicePixelRatio)

    if (config.enableShadows) {
      this.renderer.shadowMap.enabled = true
      this.renderer.shadowMap.type = THREE.PCFSoftShadowMap
    }

    container.appendChild(this.renderer.domElement)

    this.controls = new OrbitControls(this.camera, this.renderer.domElement)
    this.controls.enableDamping = true
    this.controls.dampingFactor = 0.05
    this.controls.screenSpacePanning = false
    this.controls.minDistance = 1
    this.controls.maxDistance = 100
    this.controls.maxPolarAngle = Math.PI / 2

    this.setupLights()
    this.setupGrid()

    window.addEventListener('resize', this.handleResize)

    this.animate()
  }

  private setupLights(): void {
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.6)
    this.scene.add(ambientLight)

    const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8)
    directionalLight.position.set(5, 10, 7.5)
    directionalLight.castShadow = true
    directionalLight.shadow.mapSize.width = 2048
    directionalLight.shadow.mapSize.height = 2048
    this.scene.add(directionalLight)

    const hemisphereLight = new THREE.HemisphereLight(0xffffff, 0x444444, 0.4)
    this.scene.add(hemisphereLight)
  }

  private setupGrid(): void {
    const gridHelper = new THREE.GridHelper(20, 20, 0x888888, 0xcccccc)
    this.scene.add(gridHelper)
  }

  private handleResize = (): void => {
    if (!this.container) return

    const width = this.container.clientWidth
    const height = this.container.clientHeight

    this.camera.aspect = width / height
    this.camera.updateProjectionMatrix()

    this.renderer.setSize(width, height)
  }

  private animate = (): void => {
    this.animationFrameId = requestAnimationFrame(this.animate)
    this.controls.update()
    this.renderer.render(this.scene, this.camera)
  }

  public addModel(model: THREE.Object3D): void {
    this.removeAllModels()

    this.scene.add(model)

    const box = new THREE.Box3().setFromObject(model)
    const center = box.getCenter(new THREE.Vector3())
    const size = box.getSize(new THREE.Vector3())

    model.position.sub(center)

    const maxDim = Math.max(size.x, size.y, size.z)
    const fov = this.camera.fov * (Math.PI / 180)
    let cameraZ = Math.abs(maxDim / 2 / Math.tan(fov / 2))
    cameraZ *= 1.5

    this.camera.position.set(cameraZ, cameraZ, cameraZ)
    this.camera.lookAt(0, 0, 0)

    this.controls.target.set(0, 0, 0)
    this.controls.update()
  }

  public removeAllModels(): void {
    const objectsToRemove: THREE.Object3D[] = []

    this.scene.traverse((object) => {
      if (
        object.type === 'Mesh' ||
        object.type === 'Group' ||
        (object.type === 'Object3D' && object.children.length > 0)
      ) {
        if (object !== this.scene) {
          objectsToRemove.push(object)
        }
      }
    })

    objectsToRemove.forEach((object) => {
      this.scene.remove(object)

      if (object instanceof THREE.Mesh) {
        object.geometry?.dispose()
        if (Array.isArray(object.material)) {
          object.material.forEach((material) => material.dispose())
        } else {
          object.material?.dispose()
        }
      }
    })
  }

  public getScene(): THREE.Scene {
    return this.scene
  }

  public getCamera(): THREE.PerspectiveCamera {
    return this.camera
  }

  public getRenderer(): THREE.WebGLRenderer {
    return this.renderer
  }

  public getControls(): OrbitControls {
    return this.controls
  }

  public dispose(): void {
    window.removeEventListener('resize', this.handleResize)

    if (this.animationFrameId !== null) {
      cancelAnimationFrame(this.animationFrameId)
    }

    this.removeAllModels()

    this.controls.dispose()
    this.renderer.dispose()

    if (this.container && this.renderer.domElement.parentElement === this.container) {
      this.container.removeChild(this.renderer.domElement)
    }
  }
}
