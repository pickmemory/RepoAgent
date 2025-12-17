"""
测试性能优化功能
"""

import time
import tempfile
from pathlib import Path

from repo_agent.utils.performance import (
    PerformanceOptimizer,
    performance_monitor,
    cached_operation,
    memory_efficient,
    PerformanceAnalyzer
)
from repo_agent.project.dotnet_project import DotNetProjectParser


def test_performance_monitoring():
    """测试性能监控功能"""
    print("=" * 60)
    print("测试性能监控功能")
    print("=" * 60)

    optimizer = PerformanceOptimizer()

    # 模拟一些操作
    @performance_monitor("test_operation")
    def test_operation():
        time.sleep(0.1)  # 模拟耗时操作
        return list(range(100))

    @performance_monitor("fast_operation")
    def fast_operation():
        return list(range(10))

    # 执行操作
    result1 = test_operation()
    result2 = fast_operation()
    result3 = test_operation()  # 再次执行

    # 获取性能统计
    stats = optimizer.get_performance_stats()

    print(f"\n性能统计:")
    print(f"  总操作数: {stats['total_operations']}")
    print(f"  最近操作数: {stats['recent_operations']}")

    if 'avg_duration' in stats:
        print(f"  平均耗时: {stats['avg_duration']:.3f}秒")
        print(f"  最大耗时: {stats['max_duration']:.3f}秒")
        print(f"  平均吞吐量: {stats['avg_throughput']:.1f} 项/秒")
        print(f"  成功率: {stats['success_rate']:.1%}")

    # 显示慢操作
    slow_ops = optimizer.get_slow_operations(0.05)  # 降低阈值以显示操作
    if slow_ops:
        print(f"\n慢操作 (>0.05秒):")
        for op in slow_ops:
            print(f"  {op['operation']}: {op['duration']:.3f}秒")

    print("\n性能监控测试完成 [OK]")


def test_caching():
    """测试缓存功能"""
    print("\n" + "=" * 60)
    print("测试缓存功能")
    print("=" * 60)

    optimizer = PerformanceOptimizer(cache_size=10, cache_ttl=60)

    # 测试文件缓存
    @cached_operation('parse')
    def parse_function(file_path: str):
        print(f"  解析文件: {file_path}")
        time.sleep(0.01)  # 模拟解析耗时
        return f"parsed_content_of_{file_path}"

    # 第一次调用（应该执行解析）
    print("\n第一次调用:")
    start = time.time()
    result1 = parse_function("test_file.txt")
    time1 = time.time() - start

    # 第二次调用（应该从缓存获取）
    print("\n第二次调用:")
    start = time.time()
    result2 = parse_function("test_file.txt")
    time2 = time.time() - start

    # 验证结果
    print(f"\n结果对比:")
    print(f"  第一次耗时: {time1:.3f}秒")
    print(f"  第二次耗时: {time2:.3f}秒")
    print(f"  结果一致: {result1 == result2}")
    print(f"  性能提升: {((time1 - time2) / time1 * 100):.1f}%")

    # 显示缓存统计
    stats = optimizer.get_performance_stats()
    parse_cache_stats = stats['cache_stats']['parse_cache']
    print(f"\n缓存统计:")
    print(f"  缓存大小: {parse_cache_stats['size']}")
    print(f"  命中次数: {parse_cache_stats['hits']}")
    print(f"  未命中次数: {parse_cache_stats['misses']}")
    print(f"  命中率: {parse_cache_stats['hit_rate']:.1%}")

    print("\n缓存测试完成 ✅")


def test_memory_monitoring():
    """测试内存监控功能"""
    print("\n" + "=" * 60)
    print("测试内存监控功能")
    print("=" * 60)

    optimizer = PerformanceOptimizer()

    # 获取初始内存状态
    initial_memory = optimizer.memory_monitor.get_memory_mb()
    print(f"\n初始内存使用: {initial_memory:.1f}MB")

    # 分配一些内存
    big_list = []
    for i in range(10000):
        big_list.append([j for j in range(100)])

    # 获取峰值内存
    peak_memory = optimizer.memory_monitor.get_peak_memory()
    current_memory = optimizer.memory_monitor.get_memory_mb()
    print(f"\n分配后内存使用: {current_memory:.1f}MB")
    print(f"峰值内存使用: {peak_memory / (1024 * 1024):.1f}MB")

    # 执行内存优化
    optimized_memory = optimizer.optimize_memory()
    del big_list  # 释放内存

    final_memory = optimizer.memory_monitor.get_memory_mb()
    print(f"\n优化后内存使用: {final_memory:.1f}MB")
    print(f"内存减少: {current_memory - final_memory:.1f}MB")

    # 显示内存统计
    mem_stats = optimizer.memory_monitor.get_memory_stats()
    print(f"\n内存统计:")
    print(f"  当前: {mem_stats['current_mb']:.1f}MB")
    print(f"  峰值: {mem_stats['peak_mb']:.1f}MB")
    print(f"  进程内存占比: {mem_stats['process_memory_percent']:.1f}%")

    print("\n内存监控测试完成 ✅")


def test_dotnet_parser_performance():
    """测试 .NET 解析器的性能优化"""
    print("\n" + "=" * 60)
    print("测试 .NET 解析器性能优化")
    print("=" * 60)

    # 创建临时目录和测试项目
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # 创建多个 .csproj 文件
        project_content = """<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <TargetFramework>net8.0</TargetFramework>
  </PropertyGroup>
</Project>"""

        projects = []
        for i in range(5):
            proj_dir = temp_path / f"Project{i}"
            proj_dir.mkdir()
            proj_file = proj_dir / f"Project{i}.csproj"
            proj_file.write_text(project_content)
            projects.append(f"Project{i}/Project{i}.csproj")

        # 创建解析器
        parser = DotNetProjectParser(str(temp_path))

        print(f"\n创建了 {len(projects)} 个测试项目")

        # 测试解析性能
        start_time = time.time()
        parsed_projects = []
        for proj_path in projects:
            project = parser.parse_project(proj_path)
            if project:
                parsed_projects.append(project)
        end_time = time.time()

        print(f"\n解析结果:")
        print(f"  成功解析: {len(parsed_projects)}/{len(projects)} 个项目")
        print(f"  总耗时: {end_time - start_time:.3f}秒")
        print(f"  平均每个项目: {(end_time - start_time) / len(projects):.3f}秒")

        # 再次解析（应该使用缓存）
        print("\n再次解析（测试缓存）:")
        start_time = time.time()
        cached_projects = []
        for proj_path in projects:
            project = parser.parse_project(proj_path)
            if project:
                cached_projects.append(project)
        end_time = time.time()

        print(f"  缓存解析耗时: {end_time - start_time:.3f}秒")

        # 显示性能统计
        stats = parser.optimizer.get_performance_stats()
        print(f"\n性能统计:")
        if 'avg_duration' in stats:
            print(f"  平均耗时: {stats['avg_duration']:.3f}秒")
            print(f"  最大耗时: {stats['max_duration']:.3f}秒")

        cache_stats = stats['cache_stats']['parse_cache']
        print(f"\n缓存统计:")
        print(f"  解析缓存命中率: {cache_stats['hit_rate']:.1%}")
        print(f"  缓存大小: {cache_stats['size']}")

    print("\n .NET 解析器性能测试完成 ✅")


def test_performance_report():
    """测试性能报告生成"""
    print("\n" + "=" * 60)
    print("测试性能报告生成")
    print("=" * 60)

    # 创建一些性能数据
    optimizer = PerformanceOptimizer()

    @performance_monitor("operation_1")
    def op1():
        time.sleep(0.05)
        return list(range(50))

    @performance_monitor("operation_2")
    def op2():
        time.sleep(0.02)
        return list(range(20))

    @performance_monitor("slow_operation")
    def slow_op():
        time.sleep(0.15)
        return list(range(100))

    # 执行操作
    for i in range(3):
        op1()
        op2()
    slow_op()

    # 生成报告
    analyzer = PerformanceAnalyzer(optimizer)
    report = analyzer.generate_report()

    print("\n性能报告:")
    print(report)

    # 保存报告到文件
    report_path = "performance_report.txt"
    analyzer.save_report(report_path)
    print(f"\n报告已保存到: {report_path}")

    print("\n性能报告测试完成 ✅")


def main():
    """运行所有性能测试"""
    print("开始性能优化功能测试")
    print("=" * 80)

    try:
        test_performance_monitoring()
        test_caching()
        test_memory_monitoring()
        test_dotnet_parser_performance()
        test_performance_report()

        print("\n" + "=" * 80)
        print("所有性能测试完成！ ✅")
        print("=" * 80)

    except Exception as e:
        print(f"\n测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()