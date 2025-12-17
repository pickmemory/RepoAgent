"""
简化的性能优化功能测试
"""

import time
from repo_agent.utils.performance import PerformanceOptimizer, PerformanceAnalyzer


def test_basic_performance():
    """基本性能测试"""
    print("=" * 60)
    print("性能优化功能测试")
    print("=" * 60)

    optimizer = PerformanceOptimizer()

    # 模拟操作并记录性能
    with optimizer.measure_performance("test_operation"):
        time.sleep(0.1)
        result = list(range(100))

    # 再次执行
    with optimizer.measure_performance("fast_operation"):
        time.sleep(0.01)
        result = list(range(10))

    # 获取统计
    stats = optimizer.get_performance_stats()
    print(f"\n性能统计:")
    print(f"  总操作数: {stats['total_operations']}")
    print(f"  最近操作数: {stats['recent_operations']}")

    if 'avg_duration' in stats:
        print(f"  平均耗时: {stats['avg_duration']:.3f}秒")
        print(f"  最大耗时: {stats['max_duration']:.3f}秒")
        print(f"  成功率: {stats['success_rate']:.1%}")

    # 缓存统计
    for cache_name, cache_stats in stats['cache_stats'].items():
        print(f"\n{cache_name} 缓存:")
        print(f"  大小: {cache_stats['size']}")
        print(f"  命中率: {cache_stats['hit_rate']:.1%}")

    # 内存统计
    mem_stats = stats['memory_stats']
    print(f"\n内存统计:")
    print(f"  当前使用: {mem_stats['current_mb']:.1f}MB")
    print(f"  峰值使用: {mem_stats['peak_mb']:.1f}MB")

    print("\n基本性能测试完成")


def test_dotnet_parser_with_optimization():
    """测试 .NET 解析器的性能优化"""
    print("\n" + "=" * 60)
    print(".NET 解析器性能测试")
    print("=" * 60)

    # 使用现有的 RoslynAnalyzer 项目进行测试
    parser = DotNetProjectParser(".")

    print("解析 RoslynAnalyzer 项目...")

    # 解析项目
    start_time = time.time()
    project = parser.parse_project("tools/roslyn_analyzer/RoslynAnalyzer.csproj")
    end_time = time.time()

    if project:
        print(f"解析成功: {project.name}")
        print(f"  项目类型: {project.project_type.value}")
        print(f"  目标框架: {[fw.value for fw in project.target_frameworks]}")
        print(f"  包引用数: {len(project.package_references)}")
        print(f"  源文件数: {len(project.source_files)}")
        print(f"  解析耗时: {end_time - start_time:.3f}秒")

        # 再次解析（应该使用缓存）
        print("\n再次解析（测试缓存）:")
        start_time = time.time()
        cached_project = parser.parse_project("tools/roslyn_analyzer/RoslynAnalyzer.csproj")
        end_time = time.time()
        print(f"  缓存解析耗时: {end_time - start_time:.3f}秒")

        # 显示性能统计
        stats = parser.optimizer.get_performance_stats()
        cache_stats = stats['cache_stats']['parse_cache']
        print(f"\n缓存统计:")
        print(f"  命中率: {cache_stats['hit_rate']:.1%}")
        print(f"  缓存大小: {cache_stats['size']}")
    else:
        print("解析失败")


def test_memory_optimization():
    """测试内存优化"""
    print("\n" + "=" * 60)
    print("内存优化测试")
    print("=" * 60)

    optimizer = PerformanceOptimizer()

    # 记录初始内存
    initial_memory = optimizer.memory_monitor.get_memory_mb()
    print(f"初始内存: {initial_memory:.1f}MB")

    # 分配一些内存
    big_data = []
    for i in range(1000):
        big_data.append(list(range(100)))

    allocated_memory = optimizer.memory_monitor.get_memory_mb()
    print(f"分配后内存: {allocated_memory:.1f}MB")
    print(f"内存增加: {allocated_memory - initial_memory:.1f}MB")

    # 执行内存优化
    optimized_memory = optimizer.optimize_memory()
    del big_data  # 释放内存

    final_memory = optimizer.memory_monitor.get_memory_mb()
    print(f"优化后内存: {final_memory:.1f}MB")
    print(f"内存回收: {allocated_memory - final_memory:.1f}MB")

    print("\n内存优化测试完成")


def main():
    """运行所有测试"""
    print("开始性能优化功能测试")

    try:
        test_basic_performance()
        test_dotnet_parser_with_optimization()
        test_memory_optimization()

        print("\n" + "=" * 60)
        print("所有性能测试完成 [SUCCESS]")
        print("=" * 60)

    except Exception as e:
        print(f"\n测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # 导入需要的模块
    from repo_agent.project.dotnet_project import DotNetProjectParser
    main()