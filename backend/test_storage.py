"""
简单的存储服务测试脚本。

验证存储服务的基本功能是否正常工作。
"""

import asyncio
import sys
from datetime import timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.infrastructure.storage.local_storage import LocalStorageService  # noqa: E402


async def test_storage() -> None:
    """
    测试存储服务基本功能。
    """
    print("🧪 测试存储服务...")

    storage = LocalStorageService(base_path="./test_storage")

    print("\n1. 测试文件上传...")
    test_content = b"Hello, World! This is a test file."
    file_obj = await storage.upload_file(
        file_content=test_content, filename="test.txt", content_type="text/plain"
    )
    print(f"✅ 文件上传成功: {file_obj.object_key}")
    print(f"   - 文件大小: {file_obj.size_bytes} 字节")
    print(f"   - 存储后端: {file_obj.storage_backend.value}")

    print("\n2. 测试文件下载...")
    downloaded_content = await storage.download_file(file_obj.object_key)
    assert downloaded_content == test_content
    print("✅ 文件下载成功,内容匹配")

    print("\n3. 测试文件存在检查...")
    exists = await storage.file_exists(file_obj.object_key)
    assert exists is True
    print("✅ 文件存在检查成功")

    print("\n4. 测试获取元数据...")
    metadata = await storage.get_file_metadata(file_obj.object_key)
    assert metadata is not None
    assert metadata.original_filename == "test.txt"
    print("✅ 获取元数据成功")
    print(f"   - 原始文件名: {metadata.original_filename}")
    print(f"   - 内容类型: {metadata.content_type}")

    print("\n5. 测试文件删除...")
    deleted = await storage.delete_file(file_obj.object_key)
    assert deleted is True
    exists_after_delete = await storage.file_exists(file_obj.object_key)
    assert exists_after_delete is False
    print("✅ 文件删除成功")

    print("\n6. 测试临时文件(TTL)...")

    temp_file = await storage.upload_file(
        file_content=b"Temporary file",
        filename="temp.txt",
        content_type="text/plain",
        ttl=timedelta(hours=1),
    )
    print(f"✅ 临时文件上传成功: {temp_file.object_key}")
    print("   - TTL: 1小时")

    print("\n7. 测试清理过期文件...")
    cleaned = await storage.cleanup_expired_files()
    print(f"✅ 清理任务完成,清理了 {cleaned} 个过期文件")

    await storage.delete_file(temp_file.object_key)

    print("\n✅ 所有测试通过!")


if __name__ == "__main__":
    try:
        asyncio.run(test_storage())
    except Exception as e:
        print(f"\n❌ 测试失败: {str(e)}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
