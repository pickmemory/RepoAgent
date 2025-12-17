#!/usr/bin/env python
"""测试扩展文件处理器"""

import sys
import os
sys.path.insert(0, '.')

# 设置临时的 API 密钥以避免验证错误
os.environ['OPENAI_API_KEY'] = 'test-key-for-configuration-testing'

try:
    from repo_agent.file_handler_extended import (
        MultiLanguageFileHandler,
        MultiLanguageConfig,
        create_multilang_file_handler,
        is_multilang_supported_file
    )
    from pathlib import Path

    print("[OK] 扩展文件处理器模块导入成功")

    # 测试配置
    print("\n=== 测试多语言配置 ===")
    config = MultiLanguageConfig(
        enable_dotnet=True,
        enable_treesitter=True,
        dotnet_strategy="auto"
    )
    print(f"[OK] 配置创建成功: .NET={config.enable_dotnet}, Tree-sitter={config.enable_treesitter}")

    # 测试文件支持检查
    print("\n=== 测试文件支持检查 ===")
    test_files = [
        "test.cs",
        "test.py",
        "test.fs",
        "test.vb",
        "test.js"
    ]
    for file in test_files:
        supported = is_multilang_supported_file(file)
        print(f"  {file}: {'支持' if supported else '不支持'}")

    # 测试创建处理器
    print("\n=== 测试创建多语言文件处理器 ===")

    # 使用真实的.NET项目文件进行测试
    repo_path = "D:/code/dotnet-common"
    test_file = "src/Inno.CorePlatform.Common/AssemblyInfo.cs"  # 真实存在的文件

    # 创建处理器
    handler = create_multilang_file_handler(repo_path, test_file, config)
    print(f"[OK] 文件处理器创建成功: {test_file}")

    # 获取能力信息
    capabilities = handler.get_capabilities()
    print(f"  支持的语言: {capabilities['supported_languages']}")
    print(f"  .NET 解析器可用: {capabilities['dotnet_enabled']}")
    print(f"  Tree-sitter 可用: {capabilities['treesitter_enabled']}")

    # 获取语言统计
    stats = handler.get_language_statistics()
    print(f"  检测到的语言: {stats['detected_language']}")
    print(f"  支持多语言: {stats['supports_multilang']}")

    # 测试语言检测
    print("\n=== 测试语言检测 ===")
    detected_lang = handler.detect_language()
    if detected_lang:
        print(f"[OK] 语言检测成功: {detected_lang.value}")
    else:
        print("[WARN] 语言检测失败")

    # 测试文件读取
    print("\n=== 测试文件读取 ===")
    try:
        content = handler.read_file()
        print(f"[OK] 文件读取成功: {len(content)} 字符")
        print(f"  内容预览: {repr(content[:100])}")
    except Exception as e:
        print(f"[WARN] 文件读取失败: {e}")

    # 测试结构解析
    print("\n=== 测试结构解析 ===")
    try:
        structure = handler.parse_file_structure()
        if structure:
            print(f"[OK] 结构解析成功:")
            print(f"  类数量: {len(structure.classes)}")
            print(f"  函数数量: {len(structure.functions)}")
            print(f"  命名空间: {structure.namespaces}")

            # 显示类信息
            for cls in structure.classes[:3]:  # 只显示前3个
                print(f"    类: {cls.name}")
                print(f"      基类: {cls.base_classes}")
                print(f"      方法数: {len(cls.methods)}")

            # 显示函数信息
            for func in structure.functions[:3]:  # 只显示前3个
                print(f"    函数: {func.name} ({func.return_type})")
        else:
            print("[WARN] 结构解析返回 None")
    except Exception as e:
        print(f"[WARN] 结构解析失败: {e}")
        import traceback
        traceback.print_exc()

    # 测试get_functions_and_classes兼容方法
    print("\n=== 测试兼容方法 ===")
    try:
        functions_classes = handler.get_functions_and_classes()
        print(f"[OK] 兼容方法成功: 返回 {len(functions_classes)} 个元素")

        for item in functions_classes[:3]:  # 显示前3个
            print(f"  {item}")
    except Exception as e:
        print(f"[WARN] 兼容方法失败: {e}")

    print("\n扩展文件处理器测试完成！")

except ImportError as e:
    print(f"[ERROR] 导入错误: {e}")
    import traceback
    traceback.print_exc()
except Exception as e:
    print(f"[ERROR] 运行错误: {e}")
    import traceback
    traceback.print_exc()