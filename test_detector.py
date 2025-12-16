#!/usr/bin/env python
"""测试语言检测器"""

import sys
import os
sys.path.insert(0, '.')

# 设置临时的 API 密钥以避免验证错误
os.environ['OPENAI_API_KEY'] = 'test-key-for-configuration-testing'

try:
    from repo_agent.language.detector import LanguageDetector, detect_project_languages
    from repo_agent.language import Language
    from pathlib import Path

    print("[OK] 语言检测器模块导入成功")

    # 测试当前项目
    print("\n=== 测试当前项目 (RepoAgent) ===")
    detector = LanguageDetector(Path("."))

    detected_languages = detector.detect_languages()
    print(f"[OK] 检测到的语言: {[lang.value for lang in detected_languages]}")

    # 获取语言统计
    stats = detector.get_language_statistics()
    for lang, count in stats.items():
        print(f"  - {lang.value}: {count} 个文件")

    # 建议启用的语言
    suggested = detector.suggest_enabled_languages()
    print(f"[OK] 建议启用的语言: {[lang.value for lang in suggested]}")

    # 测试 .NET 项目（如果路径存在）
    dotnet_path = Path(r"D:\code\dotnet-common")
    if dotnet_path.exists():
        print("\n=== 测试 .NET 项目 (dotnet-common) ===")
        dotnet_detector = LanguageDetector(dotnet_path)

        dotnet_languages = dotnet_detector.detect_languages()
        print(f"[OK] 检测到的语言: {[lang.value for lang in dotnet_languages]}")

        # 获取 C# 文件
        if Language.CSHARP in dotnet_languages:
            csharp_files = dotnet_detector.get_files_by_language(Language.CSHARP)
            print(f"[OK] 找到 {len(csharp_files)} 个 C# 文件")
            # 显示前5个文件
            for i, file_path in enumerate(csharp_files[:5]):
                print(f"  - {file_path}")
            if len(csharp_files) > 5:
                print(f"  ... 还有 {len(csharp_files) - 5} 个文件")

        # 项目文件检测
        print("\n--- 项目文件检测 ---")
        for file_path in dotnet_detector._get_all_files():
            if file_path.suffix.lower() in ['.csproj', '.sln', '.vbproj', '.fsproj']:
                lang = dotnet_detector.get_language_for_file(file_path)
                print(f"  项目文件: {file_path} -> {lang.value if lang else 'Unknown'}")
    else:
        print(f"\n[WARNING] .NET 项目路径不存在: {dotnet_path}")

    # 测试文件类型检测
    print("\n=== 测试文件类型检测 ===")
    test_files = [
        "test.py",
        "Program.cs",
        "Main.vb",
        "App.fs",
        "project.csproj",
        "solution.sln",
        "setup.py",
        "unknown.xyz"
    ]

    for filename in test_files:
        file_path = Path(filename)
        lang = detector.get_language_for_file(file_path)
        supported = detector.is_supported_file(file_path)
        print(f"  {filename}: {lang.value if lang else 'None'} (支持: {supported})")

    print("\n所有测试通过！")

except ImportError as e:
    print(f"[ERROR] 导入错误: {e}")
    import traceback
    traceback.print_exc()
except Exception as e:
    print(f"[ERROR] 运行错误: {e}")
    import traceback
    traceback.print_exc()