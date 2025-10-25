# 腾讯云图像风格化 API 配置指南

## 📋 配置步骤概览

1. ✅ 注册腾讯云账号
2. ✅ 开通智能创作引擎服务
3. ✅ 获取 API 密钥（SecretId 和 SecretKey）
4. ✅ 配置环境变量
5. ✅ 验证配置
6. ✅ 运行测试

预计时间：10-15 分钟

---

## 步骤 1：注册腾讯云账号

### 1.1 访问腾讯云官网

打开浏览器，访问：https://cloud.tencent.com/

### 1.2 注册账号

- 如果已有账号，直接登录
- 如果没有账号：
  1. 点击右上角【免费注册】
  2. 使用手机号或微信注册
  3. 完成实名认证（需要身份证）

> **注意**：实名认证是使用腾讯云 API 的必要条件

---

## 步骤 2：开通智能创作引擎服务

### 2.1 搜索服务

1. 登录腾讯云控制台：https://console.cloud.tencent.com/
2. 在顶部搜索框输入："智能创作引擎" 或 "aiart"
3. 点击搜索结果中的【智能创作引擎】

**直达链接**：https://console.cloud.tencent.com/aiart

### 2.2 开通服务

1. 点击【立即开通】按钮
2. 阅读并同意服务协议
3. 确认开通

### 2.3 查看免费额度

开通后可以看到：
- ✅ 每月 100 次免费调用额度
- ✅ 超出部分按量计费（约 0.1 元/次）

---

## 步骤 3：获取 API 密钥

### 3.1 访问访问管理

1. 在控制台顶部，点击右上角【账号名称】
2. 在下拉菜单中选择【访问管理】
3. 或直接访问：https://console.cloud.tencent.com/cam/capi

### 3.2 创建 API 密钥

#### 方式一：使用主账号密钥（快速测试）

1. 在【API 密钥管理】页面，点击【新建密钥】
2. 点击【确定】
3. **立即复制并保存 SecretId 和 SecretKey**

> ⚠️ **重要提示**：SecretKey 只会显示一次，请务必保存好！

#### 方式二：使用子账号密钥（推荐生产环境）

1. 创建子账号：【用户】-> 【新建用户】
2. 授予权限：【智能创作引擎 (aiart) 全读写访问权限】
3. 创建 API 密钥
4. 保存 SecretId 和 SecretKey

---

## 步骤 4：配置环境变量

### 4.1 复制环境变量模板

在项目根目录执行：

```bash
# 如果 .env 文件不存在，从模板复制
cp .env.example .env
```

### 4.2 编辑 .env 文件

打开 `.env` 文件，找到腾讯云配置部分：

```bash
# ----------------------------------------
# 腾讯云 API 配置 (图片风格化)
# ----------------------------------------
# 腾讯云 SecretId (访问管理 -> 访问密钥获取)
TENCENT_CLOUD_SECRET_ID=your_secret_id_here

# 腾讯云 SecretKey
TENCENT_CLOUD_SECRET_KEY=your_secret_key_here

# 腾讯云地域: ap-guangzhou | ap-beijing | ap-shanghai
TENCENT_CLOUD_REGION=ap-guangzhou
```

### 4.3 替换密钥信息

将第 3 步获取的密钥填入：

```bash
TENCENT_CLOUD_SECRET_ID=your_secret_id_from_step3_here
TENCENT_CLOUD_SECRET_KEY=your_secret_key_from_step3_here
TENCENT_CLOUD_REGION=ap-guangzhou
```

**地域选择建议**：
- `ap-guangzhou`：广州（推荐，延迟最低）
- `ap-beijing`：北京
- `ap-shanghai`：上海

### 4.4 保存文件

保存 `.env` 文件（注意：`.env` 文件不要提交到 Git）

---

## 步骤 5：安装依赖

### 5.1 安装腾讯云 SDK

在项目根目录执行：

```bash
# 进入后端目录
cd backend

# 安装依赖
pip install tencentcloud-sdk-python-aiart

# 或安装全部依赖
pip install -r requirements.txt
```

### 5.2 验证安装

```bash
python -c "from tencentcloud.aiart.v20221229 import aiart_client; print('SDK 安装成功')"
```

如果没有报错，说明安装成功。

---

## 步骤 6：验证配置

### 6.1 准备测试图片

在 `example/tencent_cloud/` 目录下放一张测试图片，命名为 `test_input.jpg`

**图片要求**：
- 格式：JPG、PNG、WEBP
- 大小：< 10 MB
- 分辨率：建议 1024x1024 或更小
- 内容：人物照片效果最佳（用于动漫风格）

### 6.2 运行测试脚本

创建测试脚本 `test_api.py`：

```python
# example/tencent_cloud/test_api.py
import os
from dotenv import load_dotenv
from image_style_transfer_example import TencentCloudStyleTransfer

# 加载环境变量
load_dotenv()

# 获取密钥
secret_id = os.getenv("TENCENT_CLOUD_SECRET_ID")
secret_key = os.getenv("TENCENT_CLOUD_SECRET_KEY")
region = os.getenv("TENCENT_CLOUD_REGION", "ap-guangzhou")

# 检查配置
if not secret_id or secret_id == "your_secret_id_here":
    print("❌ 错误：请先配置 TENCENT_CLOUD_SECRET_ID")
    exit(1)

if not secret_key or secret_key == "your_secret_key_here":
    print("❌ 错误：请先配置 TENCENT_CLOUD_SECRET_KEY")
    exit(1)

print("✅ 环境变量配置正确")
print(f"   SecretId: {secret_id[:10]}...")
print(f"   Region: {region}")

# 初始化客户端
print("\n🔧 初始化腾讯云客户端...")
client = TencentCloudStyleTransfer(
    secret_id=secret_id,
    secret_key=secret_key,
    region=region
)
print("✅ 客户端初始化成功")

# 测试风格转换
print("\n🎨 开始测试图片风格化...")
print("   输入图片: test_input.jpg")
print("   风格类型: anime (动漫风格)")
print("   输出图片: test_output_anime.jpg")

try:
    result = client.transfer_style(
        image_path="test_input.jpg",
        style_type="anime",
        output_path="test_output_anime.jpg"
    )

    print("\n🎉 测试成功！")
    print(f"   请求ID: {result['request_id']}")
    print(f"   输出文件: {result.get('output_path')}")

    if result.get('image_url'):
        print(f"   临时URL: {result['image_url']}")

    print("\n✅ 配置验证完成，可以开始使用腾讯云图像风格化 API！")

except FileNotFoundError:
    print("\n❌ 错误：找不到 test_input.jpg")
    print("   请在 example/tencent_cloud/ 目录下放置测试图片")

except Exception as e:
    print(f"\n❌ 测试失败: {e}")
    print("\n请检查:")
    print("1. SecretId 和 SecretKey 是否正确")
    print("2. 是否已开通智能创作引擎服务")
    print("3. 账户余额是否充足（或免费额度是否用完）")
    print("4. 网络连接是否正常")
```

### 6.3 执行测试

```bash
cd example/tencent_cloud
python test_api.py
```

**预期输出**：

```
✅ 环境变量配置正确
   SecretId: your_id...
   Region: ap-guangzhou

🔧 初始化腾讯云客户端...
✅ 客户端初始化成功

🎨 开始测试图片风格化...
   输入图片: test_input.jpg
   风格类型: anime (动漫风格)
   输出图片: test_output_anime.jpg

图片已保存到: test_output_anime.jpg

🎉 测试成功！
   请求ID: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
   输出文件: test_output_anime.jpg
   临时URL: https://...

✅ 配置验证完成，可以开始使用腾讯云图像风格化 API！
```

---

## 常见问题和解决方案

### ❌ 问题 1：提示 "SecretId 不存在"

**原因**：密钥错误或未激活

**解决方案**：
1. 检查复制的密钥是否完整（注意空格）
2. 确认密钥状态为"启用"
3. 等待 1-2 分钟后重试（新密钥需要生效时间）

---

### ❌ 问题 2：提示 "余额不足"

**原因**：免费额度用完或账户欠费

**解决方案**：
1. 登录控制台查看费用中心
2. 查看智能创作引擎的用量统计
3. 充值或等待下月免费额度刷新

---

### ❌ 问题 3：提示 "图片解码失败"

**原因**：图片格式不支持或损坏

**解决方案**：
1. 确保图片格式为 JPG、PNG 或 WEBP
2. 检查图片是否能正常打开
3. 尝试使用更小的图片（< 2048x2048）

---

### ❌ 问题 4：提示 "请求超时"

**原因**：网络问题或图片过大

**解决方案**：
1. 检查网络连接
2. 压缩图片至 1024x1024 左右
3. 更换地域（region）重试

---

### ❌ 问题 5：ImportError: No module named 'tencentcloud'

**原因**：SDK 未安装

**解决方案**：
```bash
pip install tencentcloud-sdk-python-aiart
```

---

## 安全建议

### ✅ DO（推荐做法）

1. **使用子账号密钥**
   - 创建专门的子账号用于 API 调用
   - 只授予必要的权限（智能创作引擎）

2. **密钥轮换**
   - 定期更换 API 密钥（建议 3-6 个月）
   - 删除不再使用的密钥

3. **使用环境变量**
   - 密钥存储在 `.env` 文件
   - `.env` 文件加入 `.gitignore`
   - 不要硬编码密钥到代码中

4. **监控用量**
   - 定期查看 API 调用量
   - 设置费用告警

### ❌ DON'T（禁止做法）

1. **不要泄露密钥**
   - 不要提交到 Git
   - 不要分享给他人
   - 不要打印到日志

2. **不要使用主账号**
   - 主账号权限过大，风险高
   - 应该使用子账号并限制权限

3. **不要使用硬编码**
   ```python
   # ❌ 错误示例
   secret_id = "AKIDxxxxxxxx"

   # ✅ 正确示例
   secret_id = os.getenv("TENCENT_CLOUD_SECRET_ID")
   ```

---

## 下一步

配置完成后，你可以：

1. **查看使用文档**
   - [README.md](./README.md) - 完整使用指南
   - [API_STYLE.md](../../docs/API_STYLE.md) - API 设计文档

2. **运行示例代码**
   ```bash
   cd example/tencent_cloud
   python image_style_transfer_example.py
   ```

3. **集成到项目**
   - 参考 README.md 中的"集成到项目"章节
   - 实现后端 API 和前端界面

---

## 技术支持

### 官方文档
- 产品文档：https://cloud.tencent.com/document/product/1668
- API 文档：https://cloud.tencent.com/document/api/1668/55923
- SDK 文档：https://cloud.tencent.com/document/sdk/Python

### 在线工具
- API Explorer：https://console.cloud.tencent.com/api/explorer
  （可在线调试 API，无需编写代码）

### 问题反馈
- 腾讯云工单：https://console.cloud.tencent.com/workorder
- 项目 Issue：https://github.com/your-repo/issues

---

**文档版本**: v1.0
**创建日期**: 2025-10-25
**最后更新**: 2025-10-25
**维护者**: AI Assistant
