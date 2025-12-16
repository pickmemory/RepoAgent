#!/usr/bin/env python
"""测试 Tree-sitter 环境设置"""

import sys
import os
sys.path.insert(0, '.')

# 设置临时的 API 密钥以避免验证错误
os.environ['OPENAI_API_KEY'] = 'test-key-for-configuration-testing'

try:
    # 尝试导入 tree-sitter
    import tree_sitter
    print("[OK] tree-sitter 导入成功")

    # 尝试导入语言绑定
    try:
        from tree_sitter_languages import get_language, get_parser
        print("[OK] tree-sitter-languages 导入成功")
    except ImportError as e:
        print(f"[WARNING] tree-sitter-languages 导入失败: {e}")
        print("将尝试使用内置的语言包")

    # 测试 C# 语言支持
    try:
        # 尝试获取 C# 语言
        csharp_lang = None

        # 方法1: 使用 tree_sitter_languages
        try:
            csharp_lang = get_language('c_sharp')
            print("[OK] 通过 tree_sitter_languages 获取 C# 语言成功")
        except:
            pass

        # 方法2: 手动创建语言
        if csharp_lang is None:
            try:
                # 尝试直接导入
                from tree_sitter import Language
                # 这里需要先构建语言库，暂时跳过
                print("[INFO] 需要手动构建 C# 语言库")
            except Exception as e:
                print(f"[WARNING] 无法创建 C# 语言: {e}")

    except Exception as e:
        print(f"[WARNING] C# 语言支持测试失败: {e}")

    # 创建测试脚本用于后续测试
    print("\n--- Tree-sitter 环境信息 ---")
    print(f"Python 版本: {sys.version}")
    print(f"tree-sitter 可用: {tree_sitter is not None}")

    # 尝试获取语言列表
    try:
        import tree_sitter_languages as tsl
        print(f"tree-sitter-languages 可用: {tsl is not None}")

        # 常见语言列表
        common_langs = ['python', 'javascript', 'c', 'cpp', 'java', 'go', 'rust']
        available_langs = []

        for lang in common_langs:
            try:
                get_language(lang)
                available_langs.append(lang)
            except:
                pass

        print(f"可用的常见语言: {available_langs}")

    except ImportError:
        print("tree-sitter-languages 不可用")

    print("\n环境设置完成！")

except ImportError as e:
    print(f"[ERROR] 导入错误: {e}")
    print("请确保已正确安装 tree-sitter 依赖")
except Exception as e:
    print(f"[ERROR] 运行错误: {e}")
    import traceback
    traceback.print_exc()