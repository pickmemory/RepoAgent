#!/usr/bin/env python
"""修复后的语言检测器测试"""

import sys
import os
sys.path.insert(0, '.')

# 设置临时的 API 密钥以避免验证错误
os.environ['OPENAI_API_KEY'] = 'test-key-for-configuration-testing'

try:
    from repo_agent.language.detector import LanguageDetector
    from repo_agent.language import Language
    from pathlib import Path

    dotnet_path = Path(r"D:\code\dotnet-common")

    if dotnet_path.exists():
        print(f"[OK] .NET 项目路径存在: {dotnet_path}")

        # 创建检测器（不遵守 .gitignore）
        detector = LanguageDetector(dotnet_path, respect_gitignore=False)

        # 手动检测一些文件
        test_files = [
            "dotnet-common.sln",
            "src/Inno.CorePlatform.Common/AssemblyInfo.cs",
            "src/Inno.CorePlatform.Common/Clients/ApiRoutes.cs",
        ]

        print("\n--- 测试特定文件 ---")
        for file_str in test_files:
            file_path = Path(file_str)
            if (dotnet_path / file_path).exists():
                lang = detector.get_language_for_file(file_path)
                supported = detector.is_supported_file(file_path)
                print(f"  {file_str}: {lang.value if lang else 'None'} (支持: {supported})")

        # 直接遍历 src 目录
        print("\n--- 扫描 src 目录 ---")
        src_path = dotnet_path / "src"
        if src_path.exists():
            csharp_count = 0
            project_count = 0

            for root, dirs, files in os.walk(src_path):
                # 跳过 bin, obj, packages 等目录
                dirs[:] = [d for d in dirs if d.lower() not in ['bin', 'obj', 'packages', 'node_modules']]

                for file in files:
                    file_path = Path(root) / file
                    relative_path = file_path.relative_to(dotnet_path)

                    if file_path.suffix.lower() == '.cs':
                        csharp_count += 1
                        if csharp_count <= 10:
                            print(f"  C# 文件: {relative_path}")
                    elif file_path.suffix.lower() in ['.csproj', '.vbproj', '.fsproj']:
                        project_count += 1
                        print(f"  项目文件: {relative_path}")

            print(f"\n总计: {csharp_count} 个 C# 文件, {project_count} 个项目文件")

        # 测试解决方案文件
        sln_path = dotnet_path / "dotnet-common.sln"
        if sln_path.exists():
            print(f"\n--- 解决方案文件分析 ---")
            print(f"解决方案文件存在: {sln_path}")
            with open(sln_path, 'r', encoding='utf-8') as f:
                content = f.read()
                print(f"文件大小: {len(content)} 字符")
                if 'Project' in content:
                    print("包含项目定义")

    else:
        print(f"[ERROR] .NET 项目路径不存在: {dotnet_path}")

except Exception as e:
    print(f"[ERROR] 运行错误: {e}")
    import traceback
    traceback.print_exc()