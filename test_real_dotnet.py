#!/usr/bin/env python
"""使用真实 .NET 项目测试提取器"""

import sys
import os
sys.path.insert(0, '.')

# 设置临时的 API 密钥以避免验证错误
os.environ['OPENAI_API_KEY'] = 'test-key-for-configuration-testing'

try:
    from repo_agent.parsers.dotnet_extractor import DotNetStructureExtractor
    from pathlib import Path

    print("[OK] .NET 结构提取器模块导入成功")

    # 创建提取器
    extractor = DotNetStructureExtractor()

    # 测试真实的 .NET 项目文件
    dotnet_path = Path(r"D:\code\dotnet-common")

    if dotnet_path.exists():
        print(f"\n=== 测试真实 .NET 项目文件: {dotnet_path} ===")

        # 查找并测试前几个 C# 文件
        cs_files = list(dotnet_path.rglob("*.cs"))[:5]  # 只测试前5个文件

        for file_path in cs_files:
            print(f"\n--- 文件: {file_path.relative_to(dotnet_path)} ---")

            try:
                # 读取文件内容
                with open(file_path, 'r', encoding='utf-8') as f:
                    source_code = f.read()

                # 提取结构
                structure = extractor.extract_from_source(source_code, file_path)

                print(f"  语言: {structure.language.value}")
                print(f"  文件大小: {file_path.stat().st_size} 字节")
                print(f"  命名空间: {len(structure.namespaces)}")
                print(f"  函数/方法: {len(structure.functions)}")
                print(f"  类/接口/结构体: {len(structure.classes)}")
                print(f"  导入语句: {len(structure.imports)}")

                # 提取 .NET 特有特性
                features = extractor.extract_dotnet_specific_features(source_code)
                total_features = sum(len(v) if isinstance(v, list) else len(str(v)) for v in features.values())
                print(f"  .NET 特性总数: {total_features}")

                # 显示一些具体内容
                if structure.functions:
                    print(f"  方法示例: {structure.functions[0].name}")
                if structure.classes:
                    print(f"  类示例: {structure.classes[0].name}")

            except Exception as e:
                print(f"  [ERROR] 处理失败: {e}")

    else:
        print("[WARNING] .NET 项目路径不存在")

    print("\n所有测试完成！")

except ImportError as e:
    print(f"[ERROR] 导入错误: {e}")
    import traceback
    traceback.print_exc()
except Exception as e:
    print(f"[ERROR] 运行错误: {e}")
    import traceback
    traceback.print_exc()