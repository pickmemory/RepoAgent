#!/usr/bin/env python
"""测试 .NET 项目检测"""

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

        # 创建检测器
        detector = LanguageDetector(dotnet_path)

        # 检测语言
        languages = detector.detect_languages()
        print(f"[OK] 检测到的语言: {[lang.value for lang in languages]}")

        # 获取语言统计
        stats = detector.get_language_statistics()
        print("\n--- 语言统计 ---")
        for lang, count in sorted(stats.items(), key=lambda x: x[1], reverse=True):
            print(f"  {lang.value}: {count} 个文件")

        # 显示 C# 文件示例
        if Language.CSHARP in languages:
            csharp_files = detector.get_files_by_language(Language.CSHARP)
            print(f"\n--- C# 文件示例 (共 {len(csharp_files)} 个) ---")
            for i, file_path in enumerate(csharp_files[:10]):
                print(f"  {i+1:2d}. {file_path}")
            if len(csharp_files) > 10:
                print(f"  ... 还有 {len(csharp_files) - 10} 个 C# 文件")

        # 显示项目文件
        print("\n--- 项目文件 ---")
        project_files = []
        for file_path in detector._get_all_files():
            suffix = file_path.suffix.lower()
            if suffix in ['.sln', '.csproj', '.vbproj', '.fsproj']:
                project_files.append(file_path)

        project_files.sort()
        for file_path in project_files:
            lang = detector.get_language_for_file(file_path)
            print(f"  {file_path} -> {lang.value if lang else 'Unknown'}")

        # 检查项目结构
        print("\n--- 项目结构 ---")
        src_path = dotnet_path / "src"
        test_path = dotnet_path / "test"

        if src_path.exists():
            src_detector = LanguageDetector(src_path, respect_gitignore=False)
            src_files = src_detector.get_files_by_language(Language.CSHARP)
            print(f"  src/: {len(src_files)} 个 C# 文件")

        if test_path.exists():
            test_detector = LanguageDetector(test_path, respect_gitignore=False)
            test_files = test_detector.get_files_by_language(Language.CSHARP)
            print(f"  test/: {len(test_files)} 个 C# 文件")

        # 建议的配置
        print("\n--- 建议配置 ---")
        suggested = detector.suggest_enabled_languages(min_files=1)
        print(f"  启用的语言: {[lang.value for lang in suggested]}")
        print(f"  自动检测: True")
        print(f"  .NET 框架版本: 根据项目文件确定")

    else:
        print(f"[ERROR] .NET 项目路径不存在: {dotnet_path}")

except Exception as e:
    print(f"[ERROR] 运行错误: {e}")
    import traceback
    traceback.print_exc()