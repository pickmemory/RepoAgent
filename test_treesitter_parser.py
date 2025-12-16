#!/usr/bin/env python
"""测试 Tree-sitter 解析器"""

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
        sys.exit(1)

    # 获取包装器
    wrapper = get_tree_sitter_wrapper()

    # 检查支持的语言
    supported_langs = wrapper.get_supported_languages()
    print(f"[OK] 支持的语言: {[lang.value for lang in supported_langs]}")

    # 测试 Python 解析
    if Language.PYTHON in supported_langs:
        print("\n=== 测试 Python 解析 ===")

        # 创建一个临时的 Python 文件
        test_py_content = '''
def calculate_sum(a, b):
    """Calculate sum of two numbers"""
    return a + b

class Calculator:
    def __init__(self):
        self.history = []

    def add(self, x, y):
        result = x + y
        self.history.append(f"{x} + {y} = {result}")
        return result

import math
from typing import Optional
'''

        test_py_path = Path("test_temp.py")
        with open(test_py_path, 'w', encoding='utf-8') as f:
            f.write(test_py_content)

        # 解析 Python 文件
        structure = wrapper.parse_file(test_py_path, Language.PYTHON)
        if structure:
            print(f"[OK] Python 解析成功")
            print(f"  函数: {len(structure.functions)} 个")
            for func in structure.functions:
                print(f"    - {func.name} (async: {func.is_async})")
            print(f"  类: {len(structure.classes)} 个")
            for cls in structure.classes:
                print(f"    - {cls.name} (interface: {cls.is_interface})")
            print(f"  导入: {len(structure.imports)} 个")
        else:
            print("[ERROR] Python 解析失败")

        # 清理测试文件
        test_py_path.unlink()

    # 测试 C# 解析
    if Language.CSHARP in supported_langs:
        print("\n=== 测试 C# 解析 ===")

        # 创建一个临时的 C# 文件
        test_cs_content = '''
using System;
using System.Collections.Generic;

namespace MyNamespace
{
    public class Calculator
    {
        private List<string> history = new List<string>();

        public Calculator()
        {
        }

        public int Add(int x, int y)
        {
            int result = x + y;
            history.Add($"{x} + {y} = {result}");
            return result;
        }

        public async Task<int> AddAsync(int x, int y)
        {
            await Task.Delay(100);
            return x + y;
        }
    }

    public interface ICalculator
    {
        int Add(int x, int y);
    }
}
'''

        test_cs_path = Path("test_temp.cs")
        with open(test_cs_path, 'w', encoding='utf-8') as f:
            f.write(test_cs_content)

        # 解析 C# 文件
        structure = wrapper.parse_file(test_cs_path, Language.CSHARP)
        if structure:
            print(f"[OK] C# 解析成功")
            print(f"  函数: {len(structure.functions)} 个")
            for func in structure.functions:
                print(f"    - {func.name} (async: {func.is_async}, access: {func.access_level})")
            print(f"  类: {len(structure.classes)} 个")
            for cls in structure.classes:
                print(f"    - {cls.name} (interface: {cls.is_interface}, abstract: {cls.is_abstract})")
            print(f"  导入: {len(structure.imports)} 个")
            for imp in structure.imports:
                print(f"    - {imp.module}{' as ' + imp.alias if imp.alias else ''}")
            print(f"  命名空间: {structure.namespaces}")
        else:
            print("[WARNING] C# 解析失败（可能是语言包不可用）")

        # 清理测试文件
        test_cs_path.unlink()

    # 测试 .NET 项目文件
    dotnet_path = Path(r"D:\code\dotnet-common")
    if dotnet_path.exists() and Language.CSHARP in supported_langs:
        print("\n=== 测试 .NET 项目文件解析 ===")

        # 查找 C# 文件
        for file_path in dotnet_path.rglob("*.cs"):
            # 只测试前几个文件
            if len(file_path.parts) > 5:  # 避免太深的路径
                continue

            print(f"\n测试文件: {file_path.relative_to(dotnet_path)}")
            structure = wrapper.parse_file(file_path, Language.CSHARP)
            if structure:
                print(f"  [OK] 解析成功")
                print(f"  函数: {len(structure.functions)}, 类: {len(structure.classes)}")
            else:
                print(f"  [WARNING] 解析失败")
            break

    print("\n所有测试完成！")

except ImportError as e:
    print(f"[ERROR] 导入错误: {e}")
    import traceback
    traceback.print_exc()
except Exception as e:
    print(f"[ERROR] 运行错误: {e}")
    import traceback
    traceback.print_exc()