#!/usr/bin/env python3
import json
import os
import platform
import psutil
import torch
import subprocess
from typing import Dict, Any

def get_gpu_info() -> Dict[str, Any]:
    """获取GPU信息"""
    gpu_info = {
        "available": False,
        "count": 0,
        "devices": []
    }

    if not torch.cuda.is_available():
        return gpu_info

    gpu_info["available"] = True
    gpu_info["count"] = torch.cuda.device_count()
    gpu_info["cuda_version"] = torch.version.cuda

    for i in range(gpu_info["count"]):
        device = torch.cuda.get_device_properties(i)
        gpu_info["devices"].append({
            "id": i,
            "name": device.name,
            "total_memory_gb": round(device.total_memory / (1024**3), 2),
            "compute_capability": f"{device.major}.{device.minor}"
        })

    return gpu_info

def get_cpu_info() -> Dict[str, Any]:
    """获取CPU信息"""
    cpu_info = {
        "name": platform.processor(),
        "physical_cores": psutil.cpu_count(logical=False),
        "logical_cores": psutil.cpu_count(logical=True),
        "max_frequency_ghz": round(psutil.cpu_freq().max / 1000, 2) if psutil.cpu_freq() else None
    }

    # 尝试获取更详细的CPU型号
    try:
        if platform.system() == "Linux":
            with open("/proc/cpuinfo", "r") as f:
                for line in f:
                    if line.startswith("model name"):
                        cpu_info["name"] = line.split(":")[1].strip()
                        break
        elif platform.system() == "Windows":
            import wmi
            c = wmi.WMI()
            for processor in c.Win32_Processor():
                cpu_info["name"] = processor.Name.strip()
                break
    except:
        pass

    return cpu_info

def get_memory_info() -> Dict[str, Any]:
    """获取内存信息"""
    mem = psutil.virtual_memory()
    return {
        "total_gb": round(mem.total / (1024**3), 2),
        "available_gb": round(mem.available / (1024**3), 2),
        "used_percent": mem.percent
    }

def get_system_info() -> Dict[str, Any]:
    """获取系统信息"""
    return {
        "os": platform.system(),
        "os_version": platform.version(),
        "platform": platform.platform(),
        "python_version": platform.python_version()
    }

def detect_hardware() -> Dict[str, Any]:
    """检测所有硬件信息"""
    hardware_info = {
        "system": get_system_info(),
        "cpu": get_cpu_info(),
        "memory": get_memory_info(),
        "gpu": get_gpu_info(),
        "detection_time": os.popen("date -Iseconds").read().strip()
    }

    # 判断硬件适配等级
    hardware_info["compatibility_level"] = get_compatibility_level(hardware_info)

    return hardware_info

def get_compatibility_level(hardware_info: Dict[str, Any]) -> str:
    """判断硬件兼容性等级
    返回: "high" (高端配置), "medium" (中端配置), "low" (低端配置)
    """
    if not hardware_info["gpu"]["available"]:
        return "low"

    main_gpu = hardware_info["gpu"]["devices"][0]
    vram = main_gpu["total_memory_gb"]
    ram = hardware_info["memory"]["total_gb"]

    # RTX 4070 SUPER 12GB属于高端配置
    if vram >= 12 and ram >= 32:
        return "high"
    elif vram >= 8 and ram >= 16:
        return "medium"
    else:
        return "low"

def save_hardware_config(output_path: str = "../hardware_config.json"):
    """保存硬件配置到文件"""
    hardware_info = detect_hardware()

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(hardware_info, f, indent=2, ensure_ascii=False)

    print(f"硬件配置已保存到: {os.path.abspath(output_path)}")
    print("\n检测到的硬件信息:")
    print(f"CPU: {hardware_info['cpu']['name']}")
    print(f"内存: {hardware_info['memory']['total_gb']} GB")
    if hardware_info['gpu']['available']:
        for i, gpu in enumerate(hardware_info['gpu']['devices']):
            print(f"GPU {i}: {gpu['name']} (显存: {gpu['total_memory_gb']} GB)")
        print(f"CUDA版本: {hardware_info['gpu']['cuda_version']}")
    print(f"兼容性等级: {hardware_info['compatibility_level']}")

    return hardware_info

if __name__ == "__main__":
    save_hardware_config()
