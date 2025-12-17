#!/usr/bin/env python
"""测试 GitignoreChecker 是否能检测到 .NET 文件"""

import sys
import os
sys.path.insert(0, '.')

try:
    from repo_agent.utils.gitignore_checker import GitignoreChecker

    print("[OK] GitignoreChecker 导入成功")

    # 测试 .NET 项目
    dotnet_path = "D:/code/dotnet-common"
    gitignore_path = os.path.join(dotnet_path, ".gitignore")

    checker = GitignoreChecker(dotnet_path, gitignore_path)
    files = checker.check_files_and_folders()

    print(f"\n找到 {len(files)} 个文件")

    # 显示前10个文件
    for i, file in enumerate(files[:10]):
        print(f"  {i+1}. {file}")

    # 统计文件类型
    py_files = [f for f in files if f.endswith('.py')]
    cs_files = [f for f in files if f.endswith('.cs')]

    print(f"\n文件统计:")
    print(f"  Python 文件: {len(py_files)}")
    print(f"  C# 文件: {len(cs_files)}")
    print(f"  其他文件: {len(files) - len(py_files) - len(cs_files)}")

except ImportError as e:
    print(f"[ERROR] 导入错误: {e}")
    import traceback
    traceback.print_exc()
except Exception as e:
    print(f"[ERROR] 运行错误: {e}")
    import traceback
    traceback.print_exc()