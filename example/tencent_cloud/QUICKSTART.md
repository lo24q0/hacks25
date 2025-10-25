# 🚀 腾讯云图像风格化 API - 5分钟快速开始

如果你已经有腾讯云账号和 API 密钥，这份文档可以帮你在 5 分钟内完成配置和测试。

---

## 步骤 1：配置环境变量（2 分钟）

### 复制配置文件

```bash
# 在项目根目录执行
cp .env.example .env
```

### 编辑 .env 文件

打开 `.env` 文件，找到腾讯云配置部分，填入你的密钥：

```bash
# 腾讯云 API 配置 (图片风格化)
TENCENT_CLOUD_SECRET_ID=your_tencent_cloud_secret_id_here  # 替换为你的 SecretId
TENCENT_CLOUD_SECRET_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx    # 替换为你的 SecretKey
TENCENT_CLOUD_REGION=ap-guangzhou                           # 地域选择（广州/北京/上海）
```

> **如何获取密钥？** 访问 https://console.cloud.tencent.com/cam/capi

---

## 步骤 2：安装依赖（1 分钟）

```bash
cd backend
pip install tencentcloud-sdk-python-aiart
```

或安装全部依赖：

```bash
pip install -r requirements.txt
```

---

## 步骤 3：准备测试图片（1 分钟）

在 `example/tencent_cloud/` 目录放一张测试图片：

```bash
cd example/tencent_cloud

# 如果有测试图片，复制并重命名
cp /path/to/your/photo.jpg test_input.jpg
```

**图片要求**：
- 格式：JPG、PNG 或 WEBP
- 大小：< 10 MB
- 推荐：人物照片（动漫风格效果最佳）

---

## 步骤 4：运行测试（1 分钟）

```bash
cd example/tencent_cloud
python test_api.py
```

**预期输出**：

```
============================================================
🚀 腾讯云图像风格化 API 配置验证工具
============================================================

============================================================
🔍 步骤 1: 检查环境变量配置
============================================================
✅ 找到 .env 文件: /path/to/.env
✅ 环境变量配置正确
   SecretId: your_id...here
   SecretKey: xxxxxxxxxx...xxxx
   Region: ap-guangzhou

============================================================
📦 步骤 2: 检查依赖包
============================================================
✅ tencentcloud-sdk-python-aiart 已安装

============================================================
🖼️  步骤 3: 检查测试图片
============================================================
✅ 找到测试图片: test_input.jpg
   文件大小: 2.34 MB

============================================================
🎨 步骤 4: 测试 API 调用
============================================================

🔧 初始化腾讯云客户端...
✅ 客户端初始化成功

🎨 开始测试图片风格化...
   输入图片: test_input.jpg
   风格类型: anime (动漫风格)
   输出图片: test_output_anime.jpg

   ⏳ 处理中，预计需要 10-30 秒...

图片已保存到: test_output_anime.jpg

============================================================
🎉 测试成功！
============================================================
✅ 请求ID: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
✅ 输出文件: test_output_anime.jpg

============================================================
✅ 配置验证完成！
============================================================
你现在可以:
1. 查看生成的图片: test_output_anime.jpg
2. 查看使用文档: README.md
3. 开始集成到项目中
============================================================
```

---

## 步骤 5：查看结果

测试成功后，你会在 `example/tencent_cloud/` 目录看到生成的图片：

- `test_output_anime.jpg` - 动漫风格转换结果

打开图片查看效果！

---

## 🎨 尝试更多风格

编辑 `test_api.py`，修改 `style_type` 参数：

```python
result = client.transfer_style(
    image_path="test_input.jpg",
    style_type="cartoon_3d",  # 改为其他风格
    output_path="test_output_cartoon.jpg"
)
```

**可用风格**：
- `anime` - 动漫风格
- `cartoon_3d` - 3D卡通
- `sketch` - 素描
- `watercolor` - 水彩画
- `oil_painting` - 油画

---

## ❌ 遇到问题？

### 问题 1：找不到 .env 文件

```bash
# 从模板复制
cp .env.example .env
```

### 问题 2：提示 "SecretId 不存在"

- 检查密钥是否复制完整（包括 AKID 前缀）
- 确认密钥状态为"启用"
- 等待 1-2 分钟后重试

### 问题 3：提示 "余额不足"

- 检查免费额度：https://console.cloud.tencent.com/aiart
- 每月有 100 次免费额度

### 问题 4：ImportError

```bash
pip install tencentcloud-sdk-python-aiart
```

### 问题 5：找不到测试图片

```bash
# 确保文件名正确
ls example/tencent_cloud/test_input.jpg
```

---

## 📚 下一步

✅ **配置完成后，查看完整文档**：

- [SETUP.md](./SETUP.md) - 详细配置指南（首次使用必读）
- [README.md](./README.md) - 完整使用文档和最佳实践
- [API_STYLE.md](../../docs/API_STYLE.md) - API 设计规范

✅ **开始集成到项目**：

参考 [README.md](./README.md) 的"集成到项目"章节。

---

## 🔐 安全提醒

- ✅ `.env` 文件不要提交到 Git
- ✅ 不要在代码中硬编码密钥
- ✅ 定期更换 API 密钥
- ✅ 使用子账号密钥（而非主账号）

---

**快速上手时间**：约 5 分钟
**首次配置（含账号注册）**：约 15 分钟

祝你使用愉快！🎉
