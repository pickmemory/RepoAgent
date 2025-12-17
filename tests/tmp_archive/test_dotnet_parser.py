#!/usr/bin/env python
"""测试 .NET 混合解析器"""

import sys
import os
sys.path.insert(0, '.')

# 设置临时的 API 密钥以避免验证错误
os.environ['OPENAI_API_KEY'] = 'test-key-for-configuration-testing'

try:
    from repo_agent.parsers.dotnet_parser import DotNetParser, AnalysisStrategy
    from pathlib import Path
    import time

    print("[OK] .NET 混合解析器模块导入成功")

    # 测试解析器能力
    print("\n=== 解析器能力检查 ===")
    parser = DotNetParser()
    capabilities = parser.get_capabilities()

    for name, cap in capabilities.items():
        print(f"\n{name}:")
        print(f"  速度: {cap.speed}")
        print(f"  准确性: {cap.accuracy}")
        print(f"  可用性: {'YES' if cap.availability else 'NO'}")
        print(f"  特性: {', '.join(cap.features[:3])}{'...' if len(cap.features) > 3 else ''}")

    # 测试不同策略
    print("\n=== 测试解析策略 ===")
    test_file = Path("tools/roslyn_analyzer/test.cs")

    if test_file.exists():
        strategies = [
            (AnalysisStrategy.AUTO, "自动策略"),
            (AnalysisStrategy.TREESITTER, "Tree-sitter 策略"),
            (AnalysisStrategy.ROSLYN, "Roslyn 策略")
        ]

        # 如果混合模式可用，添加到测试
        if capabilities["tree-sitter"].availability and capabilities["roslyn"].availability:
            strategies.append((AnalysisStrategy.HYBRID, "混合策略"))

        for strategy, name in strategies:
            print(f"\n--- {name} ---")
            try:
                start_time = time.time()
                parser = DotNetParser(strategy=strategy)

                # 检查策略是否实际可用
                try:
                    result = parser.parse_file(test_file)
                    end_time = time.time()

                    print(f"[OK] 解析成功")
                    print(f"  耗时: {(end_time - start_time):.3f} 秒")
                    print(f"  语言: {result.language.value}")
                    print(f"  命名空间: {len(result.namespaces)}")
                    print(f"  函数: {len(result.functions)}")
                    print(f"  类: {len(result.classes)}")
                    print(f"  导入: {len(result.imports)}")

                    # 显示一些详细信息
                    if result.classes:
                        print(f"  类示例: {result.classes[0].name}")

                except RuntimeError as e:
                    print(f"[SKIP] {e}")

            except Exception as e:
                print(f"[ERROR] {name} 测试失败: {e}")

    # 测试文件大小策略选择
    print("\n=== 测试文件大小策略选择 ===")

    # 创建不同大小的测试文件
    test_files = []

    # 小文件（使用 Roslyn）
    small_content = "public class Small { public void Method() {} }"
    small_file = Path("test_small.cs")
    with open(small_file, 'w') as f:
        f.write(small_content)
    test_files.append((small_file, "小文件"))

    # 大文件（使用 Tree-sitter）
    large_content = "public class Large {\n"
    for i in range(1000):
        large_content += f"    public void Method{i}() {{ /* Method {i} */ }}\n"
    large_content += "}\n"
    large_file = Path("test_large.cs")
    with open(large_file, 'w') as f:
        f.write(large_content)
    test_files.append((large_file, "大文件"))

    try:
        for test_file, description in test_files:
            print(f"\n--- {description} ({test_file.stat().st_size} 字节) ---")

            parser = DotNetParser(strategy=AnalysisStrategy.AUTO)
            start_time = time.time()

            try:
                result = parser.parse_file(test_file)
                end_time = time.time()

                print(f"[OK] 解析成功")
                print(f"  耗时: {(end_time - start_time):.3f} 秒")
                print(f"  类数量: {len(result.classes)}")
                print(f"  方法数量: {len(result.functions)}")

            except Exception as e:
                print(f"[ERROR] 解析失败: {e}")

    finally:
        # 清理测试文件
        for test_file, _ in test_files:
            if test_file.exists():
                test_file.unlink()

    # 测试缓存功能
    print("\n=== 测试缓存功能 ===")
    if parser.enable_caching:
        print("缓存已启用")

        # 第一次解析
        start_time = time.time()
        result1 = parser.parse_file(test_file)
        first_time = time.time() - start_time

        # 第二次解析（应该从缓存获取）
        start_time = time.time()
        result2 = parser.parse_file(test_file)
        second_time = time.time() - start_time

        print(f"首次解析: {first_time:.3f} 秒")
        print(f"缓存解析: {second_time:.3f} 秒")
        print(f"加速比: {first_time/second_time:.1f}x" if second_time > 0 else "缓存无效")

        # 显示缓存信息
        cache_info = parser.get_cache_info()
        print(f"缓存文件数: {cache_info['size']}")

        # 清除缓存
        parser.clear_cache()
        print("缓存已清除")
    else:
        print("缓存未启用")

    # 测试上下文管理器
    print("\n=== 测试上下文管理器 ===")
    try:
        with DotNetParser() as parser:
            print("[OK] 上下文管理器工作正常")
            result = parser.parse_file(test_file)
            print(f"[OK] 在上下文中解析成功: {len(result.classes)} 个类")
    except Exception as e:
        print(f"[ERROR] 上下文管理器测试失败: {e}")

    print("\n所有测试完成！")

except ImportError as e:
    print(f"[ERROR] 导入错误: {e}")
    import traceback
    traceback.print_exc()
except Exception as e:
    print(f"[ERROR] 运行错误: {e}")
    import traceback
    traceback.print_exc()