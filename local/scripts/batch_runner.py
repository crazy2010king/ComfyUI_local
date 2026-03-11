#!/usr/bin/env python3
import websocket
import uuid
import json
import urllib.request
import urllib.parse
import os
import time
import argparse
from typing import Dict, List, Any
from pathlib import Path
import sys

# 添加当前目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from hardware_detector import detect_hardware

server_address = "127.0.0.1:8188"
client_id = str(uuid.uuid4())

def queue_prompt(prompt: Dict, prompt_id: str):
    """提交工作流到ComfyUI"""
    p = {"prompt": prompt, "client_id": client_id, "prompt_id": prompt_id}
    data = json.dumps(p).encode('utf-8')
    req = urllib.request.Request(f"http://{server_address}/prompt", data=data)
    return json.loads(urllib.request.urlopen(req).read())

def get_image(filename: str, subfolder: str, folder_type: str):
    """获取生成的图片"""
    data = {"filename": filename, "subfolder": subfolder, "type": folder_type}
    url_values = urllib.parse.urlencode(data)
    with urllib.request.urlopen(f"http://{server_address}/view?{url_values}") as response:
        return response.read()

def get_history(prompt_id: str):
    """获取执行历史"""
    with urllib.request.urlopen(f"http://{server_address}/history/{prompt_id}") as response:
        return json.loads(response.read())

def run_workflow(ws: websocket.WebSocket, workflow: Dict, example_id: str) -> Dict[str, Any]:
    """运行单个工作流"""
    start_time = time.time()
    prompt_id = str(uuid.uuid4())

    try:
        queue_prompt(workflow, prompt_id)

        while True:
            out = ws.recv()
            if isinstance(out, str):
                message = json.loads(out)
                if message['type'] == 'executing':
                    data = message['data']
                    if data['node'] is None and data['prompt_id'] == prompt_id:
                        break  # 执行完成
            else:
                continue  # 预览数据忽略

        # 获取执行结果
        history = get_history(prompt_id)[prompt_id]
        execution_time = round(time.time() - start_time, 2)

        # 检查是否有错误
        if 'errors' in history and history['errors']:
            return {
                "success": False,
                "error": str(history['errors']),
                "execution_time": execution_time,
                "images": []
            }

        # 收集输出图片
        images = []
        for node_id in history['outputs']:
            node_output = history['outputs'][node_id]
            if 'images' in node_output:
                for image in node_output['images']:
                    image_data = get_image(image['filename'], image['subfolder'], image['type'])
                    # 保存图片到output目录
                    output_path = f"../output/{example_id}_{int(time.time())}.png"
                    with open(output_path, "wb") as f:
                        f.write(image_data)
                    images.append(output_path)

        # 获取显存使用情况
        try:
            import torch
            vram_used = round(torch.cuda.max_memory_allocated() / (1024**3), 2)
            torch.cuda.reset_peak_memory_stats()
        except:
            vram_used = 0

        return {
            "success": True,
            "execution_time": execution_time,
            "vram_used_gb": vram_used,
            "images": images,
            "prompt_id": prompt_id
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "execution_time": round(time.time() - start_time, 2),
            "images": []
        }

def load_workflows(workflow_dir: str = "../workflows", category: str = None) -> List[Dict]:
    """加载所有工作流文件"""
    workflows = []
    base_path = Path(workflow_dir)

    for root, _, files in os.walk(base_path):
        for file in files:
            if file.endswith('.json'):
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, workflow_dir)
                cat = os.path.dirname(rel_path)

                if category and cat != category:
                    continue

                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        workflow = json.load(f)

                    workflows.append({
                        "id": os.path.splitext(file)[0],
                        "name": os.path.splitext(file)[0].replace('_', ' ').title(),
                        "category": cat,
                        "path": file_path,
                        "workflow": workflow
                    })
                except Exception as e:
                    print(f"加载工作流失败 {file_path}: {e}")

    return workflows

def check_compatibility(workflow: Dict, hardware_info: Dict) -> str:
    """检查工作流与当前硬件的兼容性"""
    # 这里可以根据工作流的模型类型、分辨率等判断兼容性
    # 简化实现，根据分类判断
    category = workflow["category"]

    if category == "sd1.5":
        return "compatible"
    elif category == "sdxl":
        return "compatible"
    elif category == "flux":
        return "compatible" if hardware_info["gpu"]["devices"][0]["total_memory_gb"] >= 12 else "optimization_required"
    elif category == "video":
        return "optimization_required"
    else:
        return "compatible"

def generate_html_report(results: List[Dict], output_path: str = "../test_report.html"):
    """生成HTML测试报告"""
    hardware_info = detect_hardware()

    html = f"""
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <title>ComfyUI 批量测试报告</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }}
            .header {{ background-color: #2c3e50; color: white; padding: 20px; border-radius: 8px; }}
            .stats {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; margin: 20px 0; }}
            .stat-card {{ background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
            .success {{ color: #27ae60; font-weight: bold; }}
            .failed {{ color: #e74c3c; font-weight: bold; }}
            .compatible {{ color: #27ae60; }}
            .optimization {{ color: #f39c12; }}
            .incompatible {{ color: #e74c3c; }}
            table {{ width: 100%; border-collapse: collapse; background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
            th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
            th {{ background-color: #34495e; color: white; }}
            tr:hover {{ background-color: #f5f5f5; }}
            .thumbnail {{ max-width: 200px; max-height: 150px; border-radius: 4px; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>ComfyUI 批量测试报告</h1>
            <p>生成时间: {time.strftime("%Y-%m-%d %H:%M:%S")}</p>
            <p>硬件配置: {hardware_info['gpu']['devices'][0]['name']} ({hardware_info['gpu']['devices'][0]['total_memory_gb']} GB) / {hardware_info['cpu']['name']} / {hardware_info['memory']['total_gb']} GB RAM</p>
        </div>

        <div class="stats">
            <div class="stat-card">
                <h3>总示例数</h3>
                <p style="font-size: 24px; font-weight: bold;">{len(results)}</p>
            </div>
            <div class="stat-card">
                <h3>成功</h3>
                <p style="font-size: 24px;" class="success">{sum(1 for r in results if r['result']['success'])}</p>
            </div>
            <div class="stat-card">
                <h3>失败</h3>
                <p style="font-size: 24px;" class="failed">{sum(1 for r in results if not r['result']['success'])}</p>
            </div>
            <div class="stat-card">
                <h3>平均运行时间</h3>
                <p style="font-size: 24px; font-weight: bold;">{round(sum(r['result']['execution_time'] for r in results if r['result']['success']) / max(1, sum(1 for r in results if r['result']['success'])), 2)}s</p>
            </div>
        </div>

        <h2>测试详情</h2>
        <table>
            <thead>
                <tr>
                    <th>示例名称</th>
                    <th>分类</th>
                    <th>兼容性</th>
                    <th>状态</th>
                    <th>运行时间</th>
                    <th>显存占用</th>
                    <th>输出图片</th>
                    <th>错误信息</th>
                </tr>
            </thead>
            <tbody>
    """

    for result in results:
        status_class = "success" if result['result']['success'] else "failed"
        status_text = "✅ 成功" if result['result']['success'] else "❌ 失败"
        compat_class = {
            "compatible": "compatible",
            "optimization_required": "optimization",
            "incompatible": "incompatible"
        }[result['compatibility']]
        compat_text = {
            "compatible": "✅ 兼容",
            "optimization_required": "⚠️ 需优化",
            "incompatible": "❌ 不兼容"
        }[result['compatibility']]

        images_html = ""
        if result['result']['success'] and result['result']['images']:
            for img_path in result['result']['images']:
                images_html += f'<img src="{img_path}" class="thumbnail" alt="输出图片">'

        error_html = result['result'].get('error', '') if not result['result']['success'] else ''

        html += f"""
                <tr>
                    <td>{result['name']}</td>
                    <td>{result['category']}</td>
                    <td class="{compat_class}">{compat_text}</td>
                    <td class="{status_class}">{status_text}</td>
                    <td>{result['result']['execution_time']}s</td>
                    <td>{result['result'].get('vram_used_gb', 0)} GB</td>
                    <td>{images_html}</td>
                    <td>{error_html}</td>
                </tr>
        """

    html += """
            </tbody>
        </table>
    </body>
    </html>
    """

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"测试报告已生成: {os.path.abspath(output_path)}")

def main():
    parser = argparse.ArgumentParser(description='ComfyUI 工作流批量测试脚本')
    parser.add_argument('--list', action='store_true', help='仅列出所有可用工作流')
    parser.add_argument('--category', type=str, help='仅运行指定分类的工作流 (sd1.5/sdxl/flux/video/multimodal)')
    parser.add_argument('--include-optimization', action='store_true', help='包含需要优化的工作流')
    parser.add_argument('--server', type=str, default='127.0.0.1:8188', help='ComfyUI 服务器地址')
    args = parser.parse_args()

    global server_address
    server_address = args.server

    # 加载工作流
    workflows = load_workflows(category=args.category)

    if not workflows:
        print("未找到任何工作流文件")
        return

    # 检测硬件信息
    hardware_info = detect_hardware()

    # 检查兼容性
    for wf in workflows:
        wf['compatibility'] = check_compatibility(wf, hardware_info)

    if args.list:
        print("\n可用工作流列表:")
        print("-" * 80)
        for wf in workflows:
            compat_symbol = {
                "compatible": "✅",
                "optimization_required": "⚠️",
                "incompatible": "❌"
            }[wf['compatibility']]
            print(f"{compat_symbol} [{wf['category']}] {wf['name']}")
        print(f"\n总计: {len(workflows)} 个工作流")
        return

    # 筛选要运行的工作流
    runnable = []
    for wf in workflows:
        if wf['compatibility'] == "compatible":
            runnable.append(wf)
        elif wf['compatibility'] == "optimization_required" and args.include_optimization:
            runnable.append(wf)

    if not runnable:
        print("没有可运行的工作流")
        return

    print(f"即将运行 {len(runnable)} 个工作流...")

    # 连接WebSocket
    try:
        ws = websocket.WebSocket()
        ws.connect(f"ws://{server_address}/ws?clientId={client_id}")
    except Exception as e:
        print(f"连接ComfyUI服务器失败: {e}")
        print("请确保ComfyUI已经启动并运行在 {server_address}")
        return

    # 运行所有工作流
    results = []
    for i, wf in enumerate(runnable, 1):
        print(f"\n[{i}/{len(runnable)}] 运行工作流: {wf['name']} ({wf['category']})")
        result = run_workflow(ws, wf['workflow'], wf['id'])
        wf['result'] = result
        results.append(wf)

        if result['success']:
            print(f"✅ 成功! 耗时: {result['execution_time']}s, 显存占用: {result.get('vram_used_gb', 0)} GB")
            if result['images']:
                print(f"   输出图片: {', '.join(result['images'])}")
        else:
            print(f"❌ 失败! 错误: {result['error']}")

    ws.close()

    # 生成报告
    generate_html_report(results)

    # 统计结果
    success_count = sum(1 for r in results if r['result']['success'])
    print(f"\n运行完成! 成功: {success_count}/{len(results)}")

if __name__ == "__main__":
    main()
