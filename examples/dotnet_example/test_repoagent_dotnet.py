#!/usr/bin/env python3
"""
测试 RepoAgent 对 .NET 示例项目的处理
验证 .NET 支持功能是否正常工作
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到 Python 路径
repo_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(repo_root))

def test_dotnet_project_detection():
    """测试 .NET 项目检测功能"""
    print("=" * 60)
    print("测试 .NET 项目检测")
    print("=" * 60)

    try:
        from repo_agent.project.dotnet_project import DotNetProjectParser

        parser = DotNetProjectParser(".")

        # 查找项目文件
        projects = parser.find_project_files()
        print(f"找到 {len(projects)} 个 .NET 项目文件:")
        for proj in projects:
            print(f"  - {proj}")

        # 查找解决方案文件
        solutions = parser.find_solution_files()
        print(f"\n找到 {len(solutions)} 个解决方案文件:")
        for sln in solutions:
            print(f"  - {sln}")

        return len(projects) > 0

    except Exception as e:
        print(f"项目检测失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_project_parsing():
    """测试项目解析功能"""
    print("\n" + "=" * 60)
    print("测试 .NET 项目解析")
    print("=" * 60)

    try:
        from repo_agent.project.dotnet_project import DotNetProjectParser

        parser = DotNetProjectParser(".")

        # 解析 WebAppSample 项目
        web_project = parser.parse_project("WebAppSample/WebAppSample.csproj")
        if web_project:
            print(f"✓ WebAppSample 项目解析成功:")
            print(f"  - 项目类型: {web_project.project_type.value}")
            print(f"  - 语言: {web_project.language}")
            print(f"  - 目标框架: {[fw.value for fw in web_project.target_frameworks]}")
            print(f"  - 包引用数: {len(web_project.package_references)}")
            print(f"  - 源文件数: {len(web_project.source_files)}")
        else:
            print("✗ WebAppSample 项目解析失败")
            return False

        # 解析 MathLibrary 项目
        math_project = parser.parse_project("MathLibrary/MathLibrary.csproj")
        if math_project:
            print(f"\n✓ MathLibrary 项目解析成功:")
            print(f"  - 项目类型: {math_project.project_type.value}")
            print(f"  - 语言: {math_project.language}")
            print(f"  - 目标框架: {[fw.value for fw in math_project.target_frameworks]}")
            print(f"  - 包引用数: {len(math_project.package_references)}")
            print(f"  - 源文件数: {len(math_project.source_files)}")
        else:
            print("✗ MathLibrary 项目解析失败")
            return False

        return True

    except Exception as e:
        print(f"项目解析失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_solution_parsing():
    """测试解决方案解析功能"""
    print("\n" + "=" * 60)
    print("测试 .NET 解决方案解析")
    print("=" * 60)

    try:
        from repo_agent.project.dotnet_project import DotNetProjectParser

        parser = DotNetProjectParser(".")

        solution = parser.parse_solution("DotnetExample.sln")
        if solution:
            print(f"✓ 解决方案解析成功:")
            print(f"  - 名称: {solution.name}")
            print(f"  - 项目数: {len(solution.projects)}")
            print(f"  - 构建配置: {len(solution.build_configurations)}")

            for guid, project in solution.projects.items():
                print(f"\n  项目: {project.name}")
                print(f"    - 路径: {project.path}")
                print(f"    - 类型: {project.project_type.value}")
                print(f"    - 语言: {project.language}")
        else:
            print("✗ 解决方案解析失败")
            return False

        return True

    except Exception as e:
        print(f"解决方案解析失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_performance_optimization():
    """测试性能优化功能"""
    print("\n" + "=" * 60)
    print("测试性能优化功能")
    print("=" * 60)

    try:
        from repo_agent.utils.performance import get_global_optimizer

        optimizer = get_global_optimizer()
        stats = optimizer.get_performance_stats()

        print(f"✓ 性能优化器已初始化:")
        print(f"  - 文件缓存大小: {stats['cache_stats']['file_cache']['size']}")
        print(f"  - 解析缓存大小: {stats['cache_stats']['parse_cache']['size']}")
        print(f"  - 内存使用: {stats['memory_stats']['current_mb']:.1f}MB")

        return True

    except Exception as e:
        print(f"性能优化测试失败: {e}")
        return False

def main():
    """运行所有测试"""
    print("RepoAgent .NET 支持功能测试")
    print("=" * 80)

    tests = [
        ("项目检测", test_dotnet_project_detection),
        ("项目解析", test_project_parsing),
        ("解决方案解析", test_solution_parsing),
        ("性能优化", test_performance_optimization)
    ]

    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ {test_name} 测试出现异常: {e}")
            results.append((test_name, False))

    # 显示测试结果
    print("\n" + "=" * 80)
    print("测试结果汇总")
    print("=" * 80)

    passed = 0
    for test_name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{test_name}: {status}")
        if result:
            passed += 1

    print(f"\n总计: {passed}/{len(results)} 测试通过")

    if passed == len(results):
        print("🎉 所有测试通过！.NET 支持功能工作正常。")
        return 0
    else:
        print("⚠️  部分测试失败，请检查相关功能。")
        return 1

if __name__ == "__main__":
    exit(main())