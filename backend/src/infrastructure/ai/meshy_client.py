"""
Meshy AI API 客户端实现。

提供与 Meshy AI API 交互的基础功能,包括认证、请求重试、错误处理。
"""

import logging
from typing import Optional

import httpx
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from infrastructure.ai.meshy_models import (
    ImageTo3DRequest,
    MeshyTaskListResponse,
    MeshyTaskResponse,
    TextTo3DPreviewRequest,
    TextTo3DRefineRequest,
)
from infrastructure.config.settings import settings

logger = logging.getLogger(__name__)


class MeshyAPIError(Exception):
    """Meshy API 错误基类"""

    def __init__(self, message: str, status_code: Optional[int] = None):
        """
        初始化 API 错误。

        Args:
            message: 错误消息
            status_code: HTTP 状态码
        """
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class MeshyAuthenticationError(MeshyAPIError):
    """认证错误"""

    pass


class MeshyRateLimitError(MeshyAPIError):
    """速率限制错误"""

    pass


class MeshyValidationError(MeshyAPIError):
    """请求验证错误"""

    pass


class MeshyServerError(MeshyAPIError):
    """服务器错误"""

    pass


class MeshyClient:
    """
    Meshy AI API 客户端。

    提供文本转3D、图片转3D等功能的基础 HTTP 客户端。
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: Optional[int] = None,
        max_retries: Optional[int] = None,
    ):
        """
        初始化 Meshy 客户端。

        Args:
            api_key: API 密钥,默认从 settings 读取
            base_url: API 基础 URL,默认从 settings 读取
            timeout: 请求超时时间(秒),默认从 settings 读取
            max_retries: 最大重试次数,默认从 settings 读取
        """
        self.api_key = api_key or settings.meshy_api_key
        self.base_url = (base_url or settings.meshy_base_url).rstrip("/")
        self.timeout = timeout or settings.meshy_timeout
        self.max_retries = max_retries or settings.meshy_max_retries

        if not self.api_key:
            raise MeshyAuthenticationError("Meshy API key is required")

        self._client: Optional[httpx.AsyncClient] = None

    async def __aenter__(self):
        """异步上下文管理器入口"""
        await self._ensure_client()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        await self.close()

    async def _ensure_client(self):
        """确保 HTTP 客户端已初始化"""
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=self.timeout,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
            )

    async def close(self):
        """
        关闭 HTTP 客户端。

        释放连接资源。
        """
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    def _handle_response_error(self, response: httpx.Response):
        """
        处理 HTTP 响应错误。

        Args:
            response: HTTP 响应对象

        Raises:
            MeshyAPIError: 各种 API 错误
        """
        status_code = response.status_code

        try:
            error_data = response.json()
            error_message = error_data.get("message", response.text)
        except Exception:
            error_message = response.text

        if status_code == 401:
            raise MeshyAuthenticationError(
                f"Authentication failed: {error_message}", status_code
            )
        elif status_code == 429:
            raise MeshyRateLimitError(
                f"Rate limit exceeded: {error_message}", status_code
            )
        elif status_code == 400:
            raise MeshyValidationError(
                f"Validation error: {error_message}", status_code
            )
        elif status_code >= 500:
            raise MeshyServerError(
                f"Server error: {error_message}", status_code
            )
        else:
            raise MeshyAPIError(
                f"API error: {error_message}", status_code
            )

    @retry(
        retry=retry_if_exception_type((httpx.TimeoutException, MeshyServerError)),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True,
    )
    async def _request(
        self,
        method: str,
        endpoint: str,
        json_data: Optional[dict] = None,
        params: Optional[dict] = None,
    ) -> dict:
        """
        发送 HTTP 请求(带重试机制)。

        Args:
            method: HTTP 方法
            endpoint: API 端点
            json_data: JSON 请求体
            params: URL 查询参数

        Returns:
            dict: 响应 JSON 数据

        Raises:
            MeshyAPIError: 各种 API 错误
        """
        await self._ensure_client()

        try:
            logger.info(
                f"Requesting {method} {endpoint}",
                extra={"json": json_data, "params": params},
            )

            response = await self._client.request(
                method=method,
                url=endpoint,
                json=json_data,
                params=params,
            )

            if not response.is_success:
                self._handle_response_error(response)

            return response.json()

        except httpx.TimeoutException as e:
            logger.error(f"Request timeout: {endpoint}")
            raise MeshyAPIError(f"Request timeout: {str(e)}")
        except httpx.RequestError as e:
            logger.error(f"Request error: {endpoint}, {str(e)}")
            raise MeshyAPIError(f"Request error: {str(e)}")

    async def create_text_to_3d_task(
        self, request: TextTo3DPreviewRequest
    ) -> MeshyTaskResponse:
        """
        创建文本转3D预览任务。

        Args:
            request: 预览任务请求参数

        Returns:
            MeshyTaskResponse: 任务响应
        """
        response_data = await self._request(
            method="POST",
            endpoint="/openapi/v2/text-to-3d",
            json_data=request.model_dump(exclude_none=True),
        )
        return MeshyTaskResponse(**response_data)

    async def create_refine_task(
        self, request: TextTo3DRefineRequest
    ) -> MeshyTaskResponse:
        """
        创建文本转3D细化任务。

        Args:
            request: 细化任务请求参数

        Returns:
            MeshyTaskResponse: 任务响应
        """
        response_data = await self._request(
            method="POST",
            endpoint="/openapi/v2/text-to-3d",
            json_data=request.model_dump(exclude_none=True),
        )
        return MeshyTaskResponse(**response_data)

    async def create_image_to_3d_task(
        self, request: ImageTo3DRequest
    ) -> MeshyTaskResponse:
        """
        创建图片转3D任务。

        Args:
            request: 图片转3D请求参数

        Returns:
            MeshyTaskResponse: 任务响应
        """
        response_data = await self._request(
            method="POST",
            endpoint="/openapi/v1/image-to-3d",
            json_data=request.model_dump(exclude_none=True),
        )
        return MeshyTaskResponse(**response_data)

    async def get_task(self, task_id: str) -> MeshyTaskResponse:
        """
        查询任务状态。

        Args:
            task_id: 任务 ID

        Returns:
            MeshyTaskResponse: 任务响应
        """
        response_data = await self._request(
            method="GET",
            endpoint=f"/openapi/v2/text-to-3d/{task_id}",
        )
        return MeshyTaskResponse(**response_data)

    async def get_image_to_3d_task(self, task_id: str) -> MeshyTaskResponse:
        """
        查询图片转3D任务状态。

        Args:
            task_id: 任务 ID

        Returns:
            MeshyTaskResponse: 任务响应
        """
        response_data = await self._request(
            method="GET",
            endpoint=f"/openapi/v1/image-to-3d/{task_id}",
        )
        return MeshyTaskResponse(**response_data)

    async def delete_task(self, task_id: str) -> dict:
        """
        删除任务。

        Args:
            task_id: 任务 ID

        Returns:
            dict: 删除响应
        """
        return await self._request(
            method="DELETE",
            endpoint=f"/openapi/v2/text-to-3d/{task_id}",
        )

    async def list_tasks(
        self,
        page: int = 1,
        page_size: int = 10,
        sort_by: str = "created_at",
        order: str = "desc",
    ) -> MeshyTaskListResponse:
        """
        查询任务列表。

        Args:
            page: 页码,从1开始
            page_size: 每页大小
            sort_by: 排序字段
            order: 排序方式(asc/desc)

        Returns:
            MeshyTaskListResponse: 任务列表响应
        """
        params = {
            "page": page,
            "pageSize": page_size,
            "sortBy": sort_by,
            "order": order,
        }

        response_data = await self._request(
            method="GET",
            endpoint="/openapi/v2/text-to-3d",
            params=params,
        )

        return MeshyTaskListResponse(**response_data)

    async def wait_for_task_completion(
        self,
        task_id: str,
        check_interval: int = 5,
        max_wait_time: int = 600,
    ) -> MeshyTaskResponse:
        """
        等待任务完成。

        Args:
            task_id: 任务 ID
            check_interval: 检查间隔(秒)
            max_wait_time: 最大等待时间(秒)

        Returns:
            MeshyTaskResponse: 完成后的任务响应

        Raises:
            MeshyAPIError: 任务失败或超时
        """
        import asyncio

        elapsed_time = 0

        while elapsed_time < max_wait_time:
            task = await self.get_task(task_id)

            if task.status == "SUCCEEDED":
                logger.info(f"Task {task_id} completed successfully")
                return task
            elif task.status == "FAILED":
                error_msg = task.task_error or "Unknown error"
                logger.error(f"Task {task_id} failed: {error_msg}")
                raise MeshyAPIError(f"Task failed: {error_msg}")
            elif task.status == "EXPIRED":
                logger.error(f"Task {task_id} expired")
                raise MeshyAPIError("Task expired")

            logger.debug(
                f"Task {task_id} status: {task.status}, progress: {task.progress}%"
            )

            await asyncio.sleep(check_interval)
            elapsed_time += check_interval

        raise MeshyAPIError(
            f"Task {task_id} did not complete within {max_wait_time} seconds"
        )
