#!/usr/bin/env python
"""测试 Roslyn 包装器"""

import sys
import os
sys.path.insert(0, '.')

# 设置临时的 API 密钥以避免验证错误
os.environ['OPENAI_API_KEY'] = 'test-key-for-configuration-testing'

try:
    from repo_agent.parsers.roslyn_wrapper import RoslynWrapper, RoslynAnalysisResult
    from pathlib import Path

    print("[OK] Roslyn 包装器模块导入成功")

    # 创建包装器实例
    print("\n=== 初始化 Roslyn 包装器 ===")
    try:
        wrapper = RoslynWrapper()
        print("[OK] Roslyn 包装器初始化成功")
        print(f"  分析器路径: {wrapper.analyzer_path}")
    except Exception as e:
        print(f"[ERROR] 初始化失败: {e}")
        sys.exit(1)

    # 检查可用性
    print("\n=== 检查分析器可用性 ===")
    if wrapper.is_available():
        print("[OK] Roslyn 分析器可用")
    else:
        print("[WARNING] Roslyn 分析器不可用")

    # 获取版本信息
    version = wrapper.get_version()
    if version:
        print(f"版本信息: {version}")
    else:
        print("无法获取版本信息")

    # 测试分析一个文件
    print("\n=== 测试文件分析 ===")
    test_file = Path(r"D:\code\dotnet-common\demo\DemoLogic\Adapter\DaprAppEventPublisher.cs")

    if test_file.exists():
        print(f"测试文件: {test_file}")

        try:
            # 使用内存返回方式
            print("\n--- 使用内存返回方式 ---")
            result = wrapper.analyze_file(test_file, verbose=True)

            print(f"[OK] 分析成功")
            print(f"  文件路径: {result.file_path}")
            print(f"  语言: {result.language}")
            print(f"  语言版本: {result.language_version}")
            print(f"  命名空间数量: {len(result.namespaces)}")
            print(f"  导入语句数量: {len(result.imports)}")
            print(f"  类数量: {len(result.classes)}")
            print(f"  委托数量: {len(result.delegates)}")
            print(f"  枚举数量: {len(result.enums)}")

            # 显示一些详细信息
            if result.namespaces:
                print(f"  命名空间: {result.namespaces}")

            if result.classes:
                print(f"  类信息:")
                for cls in result.classes[:3]:  # 只显示前3个
                    print(f"    - {cls['name']} ({cls['kind']})")
                    methods = cls.get('methods', [])
                    if methods:
                        print(f"      方法: {[m['name'] for m in methods[:3]]}")

            # 显示 .NET 特性
            features = result.dotnet_features
            print(f"\n  .NET 特性:")
            print(f"    特性: {len(features.get('attributes', []))}")
            print(f"    LINQ 查询: {len(features.get('linqQueries', []))}")
            print(f"    LINQ 方法调用: {len(features.get('linqMethodCalls', []))}")
            print(f"    异步方法: {len(features.get('asyncMethods', []))}")
            print(f"    Lambda 表达式: {len(features.get('lambdaExpressions', []))}")

        except Exception as e:
            print(f"[ERROR] 分析失败: {e}")
            import traceback
            traceback.print_exc()

        # 测试输出到文件方式
        print("\n--- 测试输出到文件方式 ---")
        try:
            output_file = wrapper.analyze_file_to_json(
                test_file,
                output_path="test_output.json",
                verbose=True
            )
            print(f"[OK] 分析结果已保存到: {output_file}")

            # 检查文件大小
            if output_file.exists():
                size = output_file.stat().st_size
                print(f"  文件大小: {size} 字节")

                # 不清理测试文件，方便查看
                print("  [保留] 测试输出文件")

        except Exception as e:
            print(f"[ERROR] 输出到文件失败: {e}")

    else:
        print(f"[WARNING] 测试文件不存在: {test_file}")

        # 尝试使用 Roslyn 分析器的测试文件
        fallback_test = Path("tools/roslyn_analyzer/test.cs")
        if fallback_test.exists():
            print(f"\n使用备用测试文件: {fallback_test}")
            try:
                result = wrapper.analyze_file(fallback_test)
                print(f"[OK] 备用文件分析成功")
                print(f"  类数量: {len(result.classes)}")
                print(f"  方法总数: {sum(len(c.get('methods', [])) for c in result.classes)}")
            except Exception as e:
                print(f"[ERROR] 备用文件分析失败: {e}")

    print("\n=== 测试上下文管理器 ===")
    try:
        with RoslynWrapper() as w:
            print("[OK] 上下文管理器工作正常")
            if w.is_available():
                print("[OK] 分析器在上下文中可用")
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