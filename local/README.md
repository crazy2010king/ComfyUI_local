# ComfyUI 本地示例库

## 🎯 简介
这是专为ComfyUI打造的本地示例库，适配当前硬件平台（RTX 4070 SUPER 12GB + i7-14700K + 62GB内存），收集整理了各类高质量工作流示例，提供通俗易懂的使用说明和优化技巧。

## ⚡ 硬件配置
| 组件 | 型号 | 参数 |
|------|------|------|
| GPU | NVIDIA RTX 4070 SUPER | 12GB GDDR6X |
| CPU | Intel i7-14700K | 20核 (8P+12E) |
| 内存 | DDR5 | 62GB |
| CUDA版本 | 12.8 | 支持FP8加速 |

**兼容性等级**: ⭐⭐⭐⭐⭐ 高配置，可流畅运行绝大多数工作流

## 📁 目录结构
```
local/
├── README.md                          # 本文件
├── INDEX.md                           # 示例索引和快速导航
├── hardware_config.json               # 硬件配置检测结果
├── workflows/                         # 工作流文件（按模型分类）
│   ├── sd1.5/                         # Stable Diffusion 1.5 示例
│   ├── sdxl/                          # Stable Diffusion XL 示例
│   ├── flux/                          # FLUX 系列示例
│   ├── video/                         # 视频生成示例
│   └── multimodal/                    # 多模态示例
├── docs/                              # 示例说明文档
├── assets/                            # 文档资源（图片、模板）
├── scripts/                           # 工具脚本
│   ├── hardware_detector.py           # 硬件检测模块
│   ├── workflow_validator.py          # 工作流验证模块
│   ├── batch_runner.py                # 批量测试脚本
│   ├── generate_index.py              # 索引生成脚本
│   └── update_metadata.py             # 元数据更新脚本
├── metadata/                          # 配置元数据
├── input/                             # 示例输入资源
└── output/                            # 示例输出目录
```

## 🚀 快速开始

### 1. 查看示例列表
打开 [INDEX.md](./INDEX.md) 查看所有可用示例，按兼容性分类展示：
- ✅ 兼容：当前硬件可直接流畅运行
- ⚠️ 需优化：需要调整参数或启用优化选项
- ❌ 不兼容：硬件配置不足无法运行

### 2. 运行单个示例
1. 在INDEX.md中找到感兴趣的示例
2. 点击文档链接查看详细说明和使用方法
3. 在ComfyUI中加载对应的工作流文件（`workflows/`目录下）
4. 调整参数后点击运行

### 3. 批量测试所有示例
```bash
cd local/scripts
python batch_runner.py
```
脚本会自动运行所有兼容的示例，生成包含运行结果和效果图的HTML报告。

## 🔧 工具脚本说明

### 硬件检测
```bash
python hardware_detector.py
```
重新检测硬件配置，更新hardware_config.json文件。

### 工作流验证
```bash
python workflow_validator.py --check-all
```
检查所有工作流的模型依赖是否存在，配置是否正确。

### 生成索引
```bash
python generate_index.py
```
自动更新INDEX.md文件，添加新的示例。

## 📝 示例文档标准
每个示例都包含：
- 详细的功能说明和适用场景
- 硬件要求和当前硬件兼容性检查
- 完整的模型依赖和下载地址
- 界面操作和API调用两种使用方式
- 输入输出效果对比
- 针对RTX 4070 SUPER的专属优化技巧
- 常见问题解答

## 🤝 贡献指南
1. 在对应分类目录下添加工作流文件
2. 按照模板编写说明文档
3. 添加效果图到assets/images目录
4. 运行generate_index.py更新索引
5. 提交PR

## 📄 许可证
本示例库中的工作流文件遵循各自源项目的许可证，文档部分采用CC BY-SA 4.0协议。
