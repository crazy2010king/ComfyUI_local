# 示例名称: {{example_name}}

## 📋 概述
- **分类**: {{category}}
- **功能**: {{function_description}}
- **适用场景**: {{use_cases}}
- **预计运行时间**: {{estimated_time}} (RTX 4070 SUPER)

## 🧠 原理说明
{{principle_explanation}}

### 工作流架构
![工作流节点图](../assets/images/{{example_id}}_workflow.png)

## ⚙️ 硬件要求
| 配置类型 | 显存要求 | 内存要求 | CUDA |
|---------|---------|---------|------|
| 最低配置 | {{min_vram}} GB | {{min_ram}} GB | ✅ 必需 |
| 推荐配置 | {{rec_vram}} GB | {{rec_ram}} GB | ✅ 必需 |
| 当前硬件 | ⚡ RTX 4070 SUPER 12GB | 💾 62GB | ✅ 支持 |

**兼容性**: {{compatibility_status}}
{{optimization_tip}}

## 📦 模型依赖
| 模型名称 | 文件大小 | 下载地址 | 必需 |
|---------|---------|---------|------|
{{#dependencies}}
| {{model_name}} | {{size_gb}} GB | [下载]({{download_url}}) | {{required}} |
{{/dependencies}}

## 🚀 使用方法

### 界面操作
1. 打开ComfyUI
2. 点击"Load"按钮，选择工作流文件: `workflows/{{category}}/{{example_id}}.json`
3. 调整提示词参数
4. 点击"Queue Prompt"运行

### API调用
```python
import json
import urllib.request

server_address = "127.0.0.1:8188"
client_id = "test-client"

# 加载工作流
with open("../workflows/{{category}}/{{example_id}}.json", "r") as f:
    workflow = json.load(f)

# 修改提示词
workflow["6"]["inputs"]["text"] = "{{sample_prompt}}"
workflow["3"]["inputs"]["seed"] = 12345

# 提交任务
def queue_prompt(prompt):
    p = {"prompt": prompt, "client_id": client_id}
    data = json.dumps(p).encode('utf-8')
    req =  urllib.request.Request(f"http://{server_address}/prompt", data=data)
    return json.loads(urllib.request.urlopen(req).read())

queue_prompt(workflow)
```

## 🎨 效果展示

### 输入
```
提示词: {{sample_prompt}}
负提示词: {{sample_negative_prompt}}
```

### 输出
![示例输出](../assets/images/{{example_id}}_output.png)

## 💡 RTX 4070 SUPER 专属优化
{{rtx_optimization_tips}}

## ❓ 常见问题
{{faq_content}}
