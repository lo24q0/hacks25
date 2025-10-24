import asyncio
import logging
from datetime import datetime

from ..storage.local_storage import LocalStorageService

logger = logging.getLogger(__name__)


async def cleanup_expired_files_task() -> int:
    """
    清理过期文件的后台任务。
    
    扫描存储系统中的所有文件,删除已过期的临时文件。
    
    Returns:
        int: 清理的文件数量
    """
    logger.info("Starting expired files cleanup task")
    
    try:
        storage_service = LocalStorageService(base_path="./storage")
        cleaned_count = await storage_service.cleanup_expired_files()
        
        logger.info(f"Cleanup task completed. Cleaned {cleaned_count} files")
        return cleaned_count
        
    except Exception as e:
        logger.error(f"Cleanup task failed: {str(e)}", exc_info=True)
        return 0


def run_cleanup_task_sync() -> None:
    """
    同步方式运行清理任务。
    
    用于定时任务调度器(如 cron 或 APScheduler)。
    """
    asyncio.run(cleanup_expired_files_task())


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    print(f"Running cleanup task at {datetime.now()}")
    cleaned = asyncio.run(cleanup_expired_files_task())
    print(f"Cleaned {cleaned} expired files")
