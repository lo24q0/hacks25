#!/usr/bin/env python3
"""
数据库初始化脚本

创建所有数据库表
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from infrastructure.persistence.database import init_database
from infrastructure.persistence.models import PrintTaskModel, PrinterModel, Model3DRecord


async def main():
    """
    主函数
    """
    print("正在初始化数据库...")
    
    try:
        await init_database()
        print("数据库初始化成功!")
        print(f"已创建表:")
        print(f"  - {PrintTaskModel.__tablename__}")
        print(f"  - {PrinterModel.__tablename__}")
        print(f"  - {Model3DRecord.__tablename__}")
    except Exception as e:
        print(f"数据库初始化失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
