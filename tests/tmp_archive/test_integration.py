#!/usr/bin/env python
"""测试 .NET 支持集成到现有流程"""

import sys
import os
sys.path.insert(0, '.')

# 设置临时的 API 密钥以避免验证错误
os.environ['OPENAI_API_KEY'] = 'test-key-for-configuration-testing'

try:
    from repo_agent.file_handler_factory import (
        create_file_handler,
        get_supported_file_extensions,
        is_dotnet_file,
        is_python_file,
        should_process_file
    )
    from pathlib import Path

    print("[OK] 文件处理器工厂模块导入成功")

    # 测试支持的文件扩展名
    print("\n=== 测试支持的文件扩展名 ===")
    extensions = get_supported_file_extensions()
    print(f"支持的扩展名: {extensions}")
    print(f"数量: {len(extensions)}")

    # 测试文件类型检查
    print("\n=== 测试文件类型检查 ===")
    test_files = [
        "test.py",
        "test.cs",
        "test.fs",
        "test.vb",
        "test.js",
        "test.txt"
    ]
    for file in test_files:
        is_dotnet = is_dotnet_file(file)
        is_python = is_python_file(file)
        should_process = should_process_file(file)
        print(f"  {file}: .NET={is_dotnet}, Python={is_python}, 应处理={should_process}")

    # 测试文件处理器创建
    print("\n=== 测试文件处理器创建 ===")
    repo_path = "D:/code/dotnet-common"

    # Python 文件
    py_handler = create_file_handler(repo_path, "test.py")
    print(f"Python 文件处理器类型: {type(py_handler).__name__}")

    # .NET 文件
    cs_handler = create_file_handler(repo_path, "test.cs")
    print(f".NET 文件处理器类型: {type(cs_handler).__name__}")

    # 不支持的文件
    js_handler = create_file_handler(repo_path, "test.js")
    print(f"不支持的文件处理器类型: {type(js_handler).__name__}")

    # None 文件路径（用于整体结构生成）
    none_handler = create_file_handler(repo_path, None)
    print(f"None 路径处理器类型: {type(none_handler).__name__}")

    # 测试真实 .NET 文件处理
    print("\n=== 测试真实 .NET 文件处理 ===")
    real_cs_file = "src/Inno.CorePlatform.Common/AssemblyInfo.cs"
    real_handler = create_file_handler(repo_path, real_cs_file)

    print(f"真实文件处理器类型: {type(real_handler).__name__}")

    # 检查是否有多语言支持
    if hasattr(real_handler, 'get_capabilities'):
        capabilities = real_handler.get_capabilities()
        print(f"多语言能力: {capabilities}")
    else:
        print("使用传统文件处理器")

    # 测试文件读取和解析
    try:
        content = real_handler.read_file()
        print(f"文件读取成功: {len(content)} 字符")

        # 尝试获取函数和类
        functions_classes = real_handler.get_functions_and_classes()
        print(f"解析结果: {len(functions_classes)} 个结构元素")
    except Exception as e:
        print(f"处理失败: {e}")

    print("\n集成测试完成！")

except ImportError as e:
    print(f"[ERROR] 导入错误: {e}")
    import traceback
    traceback.print_exc()
except Exception as e:
    print(f"[ERROR] 运行错误: {e}")
    import traceback
    traceback.print_exc()