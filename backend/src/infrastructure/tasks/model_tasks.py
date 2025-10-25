"""
模型生成异步任务模块。

包含 Meshy AI 文本转3D、图片转3D 的 Celery 异步任务实现。
"""

import asyncio
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

import httpx
from celery import Task

from infrastructure.ai.meshy_client import MeshyAPIError, MeshyClient
from infrastructure.ai.meshy_models import GenerationConfig, MeshyTaskResponse
from infrastructure.ai.text_to_3d_service import TextTo3DService
from infrastructure.ai.image_to_3d_service import ImageTo3DService
from infrastructure.config.settings import settings
from src.infrastructure.tasks.celery_app import celery_app

logger = logging.getLogger(__name__)


async def download_model_file(url: str, save_path: Path) -> None:
    """
    从 URL 下载模型文件到本地。

    Args:
        url: 模型文件 URL
        save_path: 本地保存路径

    Raises:
        httpx.HTTPError: 下载失败
    """
    save_path.parent.mkdir(parents=True, exist_ok=True)

    async with httpx.AsyncClient(timeout=300.0) as client:
        logger.info(f"Downloading model from {url} to {save_path}")
        response = await client.get(url)
        response.raise_for_status()

        with open(save_path, "wb") as f:
            f.write(response.content)

        logger.info(f"Model downloaded successfully: {save_path}")


@celery_app.task(
    bind=True,
    name="model_tasks.generate_text_to_3d",
    max_retries=3,
    default_retry_delay=60,
)
def generate_text_to_3d(
    self: Task,
    prompt: str,
    model_id: str,
    art_style: str = "realistic",
    target_polycount: int = 30000,
    seed: Optional[int] = None,
) -> dict:
    """
    文本转3D模型生成任务。

    Args:
        self: Celery 任务实例
        prompt: 文本描述
        model_id: 模型ID(用于保存文件)
        art_style: 艺术风格
        target_polycount: 目标面数
        seed: 随机种子

    Returns:
        dict: 任务结果,包含文件路径和元数据

    Raises:
        MeshyAPIError: Meshy API 调用失败
    """
    task_id = self.request.id
    logger.info(f"Starting text-to-3d task {task_id} for model {model_id}")

    try:
        async def run_generation():
            config = GenerationConfig(
                art_style=art_style,
                target_polycount=target_polycount,
            )

            async with TextTo3DService() as service:
                self.update_state(
                    state="PROGRESS",
                    meta={
                        "stage": "creating_preview",
                        "progress": 10,
                        "status": "Creating preview task",
                    },
                )

                preview_task = await service.create_preview_task(
                    prompt=prompt, config=config, seed=seed
                )

                logger.info(
                    f"Preview task created: {preview_task.id} for model {model_id}"
                )

                def progress_callback(meshy_task_id, status, progress):
                    self.update_state(
                        state="PROGRESS",
                        meta={
                            "stage": "generating_preview",
                            "progress": 10 + int(progress * 0.4),
                            "status": f"Generating preview: {progress}%",
                            "meshy_task_id": meshy_task_id,
                        },
                    )

                completed_preview = await service.wait_for_completion(
                    task_id=preview_task.id,
                    max_wait_time=600,
                    progress_callback=progress_callback,
                )

                self.update_state(
                    state="PROGRESS",
                    meta={
                        "stage": "downloading_files",
                        "progress": 60,
                        "status": "Downloading model files",
                    },
                )

                storage_dir = Path(settings.storage_path) / "models"
                model_files = {}

                if completed_preview.model_urls:
                    if completed_preview.model_urls.glb:
                        glb_path = storage_dir / f"{model_id}.glb"
                        await download_model_file(
                            completed_preview.model_urls.glb, glb_path
                        )
                        model_files["glb"] = str(glb_path)

                    if completed_preview.model_urls.obj:
                        obj_path = storage_dir / f"{model_id}.obj"
                        await download_model_file(
                            completed_preview.model_urls.obj, obj_path
                        )
                        model_files["obj"] = str(obj_path)

                    if completed_preview.model_urls.fbx:
                        fbx_path = storage_dir / f"{model_id}.fbx"
                        await download_model_file(
                            completed_preview.model_urls.fbx, fbx_path
                        )
                        model_files["fbx"] = str(fbx_path)

                    if completed_preview.model_urls.mtl:
                        mtl_path = storage_dir / f"{model_id}.mtl"
                        await download_model_file(
                            completed_preview.model_urls.mtl, mtl_path
                        )
                        model_files["mtl"] = str(mtl_path)

                thumbnail_path = None
                if completed_preview.thumbnail_url:
                    thumbnail_dir = Path(settings.storage_path) / "thumbnails"
                    thumbnail_path = thumbnail_dir / f"{model_id}.png"
                    await download_model_file(
                        completed_preview.thumbnail_url, thumbnail_path
                    )

                self.update_state(
                    state="PROGRESS",
                    meta={
                        "stage": "completed",
                        "progress": 100,
                        "status": "Model generation completed",
                    },
                )

                return {
                    "model_id": model_id,
                    "meshy_task_id": completed_preview.id,
                    "status": "completed",
                    "model_files": model_files,
                    "thumbnail_path": str(thumbnail_path) if thumbnail_path else None,
                    "completed_at": datetime.utcnow().isoformat(),
                }

        return asyncio.run(run_generation())

    except MeshyAPIError as e:
        logger.error(f"Meshy API error in task {task_id}: {str(e)}")
        self.update_state(
            state="FAILURE",
            meta={
                "error": str(e),
                "error_type": "MeshyAPIError",
            },
        )
        raise

    except Exception as e:
        logger.error(f"Unexpected error in task {task_id}: {str(e)}")
        self.update_state(
            state="FAILURE",
            meta={
                "error": str(e),
                "error_type": type(e).__name__,
            },
        )
        raise self.retry(exc=e, countdown=60)


@celery_app.task(
    bind=True,
    name="model_tasks.generate_image_to_3d",
    max_retries=3,
    default_retry_delay=60,
)
def generate_image_to_3d(
    self: Task,
    image_url: str,
    model_id: str,
    target_polycount: int = 30000,
    enable_pbr: bool = False,
) -> dict:
    """
    图片转3D模型生成任务。

    Args:
        self: Celery 任务实例
        image_url: 图片 URL
        model_id: 模型ID(用于保存文件)
        target_polycount: 目标面数
        enable_pbr: 是否生成 PBR 贴图

    Returns:
        dict: 任务结果,包含文件路径和元数据

    Raises:
        MeshyAPIError: Meshy API 调用失败
    """
    task_id = self.request.id
    logger.info(f"Starting image-to-3d task {task_id} for model {model_id}")

    try:
        async def run_generation():
            config = GenerationConfig(
                target_polycount=target_polycount,
                enable_pbr=enable_pbr,
            )

            async with ImageTo3DService() as service:
                self.update_state(
                    state="PROGRESS",
                    meta={
                        "stage": "creating_task",
                        "progress": 10,
                        "status": "Creating image-to-3d task",
                    },
                )

                task = await service.create_task(image_url=image_url, config=config)

                logger.info(f"Image-to-3d task created: {task.id} for model {model_id}")

                def progress_callback(meshy_task_id, status, progress):
                    self.update_state(
                        state="PROGRESS",
                        meta={
                            "stage": "generating",
                            "progress": 10 + int(progress * 0.8),
                            "status": f"Generating model: {progress}%",
                            "meshy_task_id": meshy_task_id,
                        },
                    )

                completed_task = await service.wait_for_completion(
                    task_id=task.id,
                    max_wait_time=600,
                    progress_callback=progress_callback,
                )

                self.update_state(
                    state="PROGRESS",
                    meta={
                        "stage": "downloading_files",
                        "progress": 90,
                        "status": "Downloading model files",
                    },
                )

                storage_dir = Path(settings.storage_path) / "models"
                model_files = {}

                if completed_task.model_urls:
                    if completed_task.model_urls.glb:
                        glb_path = storage_dir / f"{model_id}.glb"
                        await download_model_file(
                            completed_task.model_urls.glb, glb_path
                        )
                        model_files["glb"] = str(glb_path)

                    if completed_task.model_urls.obj:
                        obj_path = storage_dir / f"{model_id}.obj"
                        await download_model_file(
                            completed_task.model_urls.obj, obj_path
                        )
                        model_files["obj"] = str(obj_path)

                    if completed_task.model_urls.fbx:
                        fbx_path = storage_dir / f"{model_id}.fbx"
                        await download_model_file(
                            completed_task.model_urls.fbx, fbx_path
                        )
                        model_files["fbx"] = str(fbx_path)

                    if completed_task.model_urls.mtl:
                        mtl_path = storage_dir / f"{model_id}.mtl"
                        await download_model_file(
                            completed_task.model_urls.mtl, mtl_path
                        )
                        model_files["mtl"] = str(mtl_path)

                thumbnail_path = None
                if completed_task.thumbnail_url:
                    thumbnail_dir = Path(settings.storage_path) / "thumbnails"
                    thumbnail_path = thumbnail_dir / f"{model_id}.png"
                    await download_model_file(completed_task.thumbnail_url, thumbnail_path)

                texture_files = {}
                if completed_task.texture_urls:
                    texture_dir = Path(settings.storage_path) / "textures"
                    if completed_task.texture_urls.base_color:
                        base_color_path = texture_dir / f"{model_id}_base_color.png"
                        await download_model_file(
                            completed_task.texture_urls.base_color, base_color_path
                        )
                        texture_files["base_color"] = str(base_color_path)

                    if completed_task.texture_urls.normal:
                        normal_path = texture_dir / f"{model_id}_normal.png"
                        await download_model_file(
                            completed_task.texture_urls.normal, normal_path
                        )
                        texture_files["normal"] = str(normal_path)

                    if completed_task.texture_urls.metallic:
                        metallic_path = texture_dir / f"{model_id}_metallic.png"
                        await download_model_file(
                            completed_task.texture_urls.metallic, metallic_path
                        )
                        texture_files["metallic"] = str(metallic_path)

                    if completed_task.texture_urls.roughness:
                        roughness_path = texture_dir / f"{model_id}_roughness.png"
                        await download_model_file(
                            completed_task.texture_urls.roughness, roughness_path
                        )
                        texture_files["roughness"] = str(roughness_path)

                self.update_state(
                    state="PROGRESS",
                    meta={
                        "stage": "completed",
                        "progress": 100,
                        "status": "Model generation completed",
                    },
                )

                return {
                    "model_id": model_id,
                    "meshy_task_id": completed_task.id,
                    "status": "completed",
                    "model_files": model_files,
                    "thumbnail_path": str(thumbnail_path) if thumbnail_path else None,
                    "texture_files": texture_files,
                    "completed_at": datetime.utcnow().isoformat(),
                }

        return asyncio.run(run_generation())

    except MeshyAPIError as e:
        logger.error(f"Meshy API error in task {task_id}: {str(e)}")
        self.update_state(
            state="FAILURE",
            meta={
                "error": str(e),
                "error_type": "MeshyAPIError",
            },
        )
        raise

    except Exception as e:
        logger.error(f"Unexpected error in task {task_id}: {str(e)}")
        self.update_state(
            state="FAILURE",
            meta={
                "error": str(e),
                "error_type": type(e).__name__,
            },
        )
        raise self.retry(exc=e, countdown=60)
