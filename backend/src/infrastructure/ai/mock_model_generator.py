"""
Mock 模型生成器实现。

在 Meshy AI API 不可用时，提供 mock 数据用于开发和测试。
"""

import asyncio
import logging
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

from src.infrastructure.config.settings import settings

logger = logging.getLogger(__name__)


class MockModelGenerator:
    """
    Mock 模型生成器。
    
    在 mock 模式下，复制预设的 STL 文件作为生成的模型，
    模拟真实的模型生成流程。
    """

    def __init__(self):
        """初始化 Mock 模型生成器"""
        self.storage_path = Path(settings.storage_path)
        self.mock_model_path = self.storage_path / "models" / "test-model.obj"
        
    async def generate_text_to_3d(
        self,
        prompt: str,
        model_id: str,
        art_style: str = "realistic",
        target_polycount: int = 30000,
        seed: Optional[int] = None,
    ) -> Dict:
        """
        模拟文本转3D模型生成。
        
        Args:
            prompt: 文本描述
            model_id: 模型ID
            art_style: 艺术风格
            target_polycount: 目标面数
            seed: 随机种子
            
        Returns:
            Dict: 模拟的任务结果
        """
        logger.info(f"Mock text-to-3d generation for model {model_id}")
        logger.info(f"Prompt: {prompt[:50]}...")
        
        # 模拟生成过程
        await asyncio.sleep(2)  # 模拟网络延迟
        
        # 确保存储目录存在
        models_dir = self.storage_path / "models"
        models_dir.mkdir(parents=True, exist_ok=True)
        
        # 复制 mock 模型文件
        model_files = {}
        if self.mock_model_path.exists():
            # 复制为不同格式的文件
            stl_path = models_dir / f"{model_id}.stl"
            obj_path = models_dir / f"{model_id}.obj"
            
            shutil.copy2(self.mock_model_path, stl_path)
            shutil.copy2(self.mock_model_path, obj_path)
            
            model_files = {
                "stl": f"/storage/models/{model_id}.stl",
                "obj": f"/storage/models/{model_id}.obj",
            }
            
            logger.info(f"Mock model files created: {model_files}")
        else:
            logger.warning(f"Mock model file not found: {self.mock_model_path}")
        
        return {
            "model_id": model_id,
            "meshy_task_id": f"mock_task_{model_id}",
            "status": "completed",
            "model_files": model_files,
            "thumbnail_path": None,
            "completed_at": datetime.utcnow().isoformat(),
            "mock_mode": True,
        }

    async def generate_image_to_3d(
        self,
        image_url: str,
        model_id: str,
        target_polycount: int = 30000,
        enable_pbr: bool = False,
    ) -> Dict:
        """
        模拟图片转3D模型生成。
        
        Args:
            image_url: 图片URL
            model_id: 模型ID
            target_polycount: 目标面数
            enable_pbr: 是否生成PBR贴图
            
        Returns:
            Dict: 模拟的任务结果
        """
        logger.info(f"Mock image-to-3d generation for model {model_id}")
        logger.info(f"Image URL: {image_url}")
        
        # 模拟生成过程
        await asyncio.sleep(3)  # 模拟更长的处理时间
        
        # 确保存储目录存在
        models_dir = self.storage_path / "models"
        models_dir.mkdir(parents=True, exist_ok=True)
        
        # 复制 mock 模型文件
        model_files = {}
        if self.mock_model_path.exists():
            # 复制为不同格式的文件
            stl_path = models_dir / f"{model_id}.stl"
            obj_path = models_dir / f"{model_id}.obj"
            glb_path = models_dir / f"{model_id}.glb"
            
            shutil.copy2(self.mock_model_path, stl_path)
            shutil.copy2(self.mock_model_path, obj_path)
            shutil.copy2(self.mock_model_path, glb_path)
            
            model_files = {
                "stl": f"/storage/models/{model_id}.stl",
                "obj": f"/storage/models/{model_id}.obj",
                "glb": f"/storage/models/{model_id}.glb",
            }
            
            logger.info(f"Mock model files created: {model_files}")
        else:
            logger.warning(f"Mock model file not found: {self.mock_model_path}")
        
        # 模拟纹理文件（如果启用PBR）
        texture_files = {}
        if enable_pbr:
            texture_dir = self.storage_path / "textures"
            texture_dir.mkdir(parents=True, exist_ok=True)
            
            # 创建空的纹理文件占位符
            texture_files = {
                "base_color": f"/storage/textures/{model_id}_base_color.png",
                "normal": f"/storage/textures/{model_id}_normal.png",
                "metallic": f"/storage/textures/{model_id}_metallic.png",
                "roughness": f"/storage/textures/{model_id}_roughness.png",
            }
            
            # 创建空文件
            for texture_path in texture_files.values():
                Path(texture_path).touch()
        
        return {
            "model_id": model_id,
            "meshy_task_id": f"mock_task_{model_id}",
            "status": "completed",
            "model_files": model_files,
            "thumbnail_path": None,
            "texture_files": texture_files,
            "completed_at": datetime.utcnow().isoformat(),
            "mock_mode": True,
        }

    async def get_task_status(self, task_id: str) -> Dict:
        """
        模拟获取任务状态。
        
        Args:
            task_id: 任务ID
            
        Returns:
            Dict: 任务状态信息
        """
        logger.info(f"Mock task status for {task_id}")
        
        return {
            "task_id": task_id,
            "status": "SUCCEEDED",
            "progress": 100,
            "model_urls": {
                "stl": f"/models/{task_id}.stl",
                "obj": f"/models/{task_id}.obj",
                "glb": f"/models/{task_id}.glb",
            },
            "thumbnail_url": None,
            "error": None,
            "mock_mode": True,
        }
