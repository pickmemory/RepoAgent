#!/usr/bin/env python
"""简化的 Tree-sitter 测试"""

import sys
import os
sys.path.insert(0, '.')

# 设置临时的 API 密钥以避免验证错误
os.environ['OPENAI_API_KEY'] = 'test-key-for-configuration-testing'

try:
    from repo_agent.parsers.tree_sitter_parser import get_tree_sitter_wrapper, is_tree_sitter_available
    from repo_agent.language import Language
    from pathlib import Path

    print("[OK] Tree-sitter 解析器模块导入成功")

    # 检查可用性
    if is_tree_sitter_available():
        print("[OK] Tree-sitter 可用")
    else:
        print("[WARNING] Tree-sitter 不可用")

    # 获取包装器
    wrapper = get_tree_sitter_wrapper()

    # 测试解析一个 C# 文件
    dotnet_path = Path(r"D:\code\dotnet-common")
    if dotnet_path.exists():
        print("\n=== 测试 C# 文件解析 ===")

        # 查找第一个 C# 文件
        for file_path in dotnet_path.rglob("*.cs"):
            print(f"测试文件: {file_path.relative_to(dotnet_path)}")

            # 尝试解析
            structure = wrapper.parse_file(file_path, Language.CSHARP)
            if structure:
                print("[OK] 解析成功")
                print(f"  语言: {structure.language.value}")
                print(f"  文件大小: {file_path.stat().st_size} 字节")
            else:
                print("[WARNING] 解析失败")
            break
    else:
        print("[WARNING] .NET 项目路径不存在")

    print("\n测试完成！")

except Exception as e:
    print(f"[ERROR] 运行错误: {e}")
    import traceback
    traceback.print_exc()