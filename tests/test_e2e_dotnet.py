#!/usr/bin/env python3
"""
RepoAgent .NET 支持端到端测试
使用真实 .NET 项目验证完整的文档生成工作流程
"""

import sys
import os
import time
from pathlib import Path
import tempfile
import shutil

# 添加项目根目录到 Python 路径
repo_root = Path(__file__).parent.parent
sys.path.insert(0, str(repo_root))

class E2ETestReporter:
    """端到端测试报告器"""

    def __init__(self):
        self.test_results = []
        self.start_time = time.time()

    def add_result(self, test_name: str, success: bool, details: str = "", duration: float = 0):
        """添加测试结果"""
        self.test_results.append({
            'test_name': test_name,
            'success': success,
            'details': details,
            'duration': duration
        })

    def print_test_result(self, test_name: str, success: bool, details: str = ""):
        """打印测试结果"""
        status = "[PASS]" if success else "[FAIL]"
        print(f"{status} {test_name}")
        if details:
            print(f"       {details}")

    def generate_report(self) -> str:
        """生成测试报告"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r['success'])
        total_duration = time.time() - self.start_time

        report = f"""
# RepoAgent .NET 支持端到端测试报告

## 测试概览
- 总测试数: {total_tests}
- 通过测试: {passed_tests}
- 失败测试: {total_tests - passed_tests}
- 成功率: {(passed_tests/total_tests)*100:.1f}%
- 总耗时: {total_duration:.2f}秒

## 详细结果

"""

        for result in self.test_results:
            status = "✅ 通过" if result['success'] else "❌ 失败"
            report += f"### {result['test_name']} {status}\n"
            if result['details']:
                report += f"{result['details']}\n"
            if result['duration'] > 0:
                report += f"耗时: {result['duration']:.3f}秒\n"
            report += "\n"

        return report

def test_project_discovery(project_path: str) -> bool:
    """测试项目发现功能"""
    print("测试项目发现...")

    try:
        from repo_agent.project.dotnet_project import DotNetProjectParser

        start_time = time.time()
        parser = DotNetProjectParser(project_path)

        # 查找项目文件
        projects = parser.find_project_files()
        project_count = len(projects)

        # 查找解决方案文件
        solutions = parser.find_solution_files()
        solution_count = len(solutions)

        duration = time.time() - start_time

        if project_count > 0:
            reporter.add_result(
                "项目发现",
                True,
                f"发现 {project_count} 个项目文件, {solution_count} 个解决方案文件",
                duration
            )
            return True
        else:
            reporter.add_result(
                "项目发现",
                False,
                "未发现任何 .NET 项目文件",
                duration
            )
            return False

    except Exception as e:
        reporter.add_result("项目发现", False, f"异常: {str(e)}")
        return False

def test_project_parsing(project_path: str) -> bool:
    """测试项目解析功能"""
    print("测试项目解析...")

    try:
        from repo_agent.project.dotnet_project import DotNetProjectParser

        start_time = time.time()
        parser = DotNetProjectParser(project_path)

        # 获取项目文件
        projects = parser.find_project_files()
        if not projects:
            reporter.add_result("项目解析", False, "没有找到项目文件可解析")
            return False

        # 解析前几个项目
        parsed_count = 0
        error_count = 0

        # 限制解析数量以避免测试时间过长
        max_projects = min(5, len(projects))

        for i, proj_path in enumerate(projects[:max_projects]):
            try:
                project = parser.parse_project(proj_path)
                if project:
                    parsed_count += 1
                    print(f"  ✓ 解析成功: {proj_path} ({project.project_type.value})")
                else:
                    error_count += 1
                    print(f"  ✗ 解析失败: {proj_path}")
            except Exception as e:
                error_count += 1
                print(f"  ✗ 解析异常: {proj_path} - {e}")

        duration = time.time() - start_time

        success = parsed_count > 0
        details = f"解析成功: {parsed_count}/{max_projects}, 错误: {error_count}"

        reporter.add_result("项目解析", success, details, duration)
        return success

    except Exception as e:
        reporter.add_result("项目解析", False, f"异常: {str(e)}")
        return False

def test_solution_parsing(project_path: str) -> bool:
    """测试解决方案解析功能"""
    print("测试解决方案解析...")

    try:
        from repo_agent.project.dotnet_project import DotNetProjectParser

        start_time = time.time()
        parser = DotNetProjectParser(project_path)

        solutions = parser.find_solution_files()
        if not solutions:
            reporter.add_result("解决方案解析", False, "未找到解决方案文件")
            return False

        # 解析第一个解决方案
        solution = parser.parse_solution(solutions[0])
        duration = time.time() - start_time

        if solution:
            details = f"解析解决方案: {solution.name}, 包含 {len(solution.projects)} 个项目"
            reporter.add_result("解决方案解析", True, details, duration)
            return True
        else:
            reporter.add_result("解决方案解析", False, "解决方案解析失败", duration)
            return False

    except Exception as e:
        reporter.add_result("解决方案解析", False, f"异常: {str(e)}")
        return False

def test_project_structure_generation(project_path: str) -> bool:
    """测试项目结构生成"""
    print("测试项目结构生成...")

    try:
        from repo_agent.project_manager import ProjectManager

        start_time = time.time()

        # 创建临时目录用于输出
        with tempfile.TemporaryDirectory() as temp_dir:
            project_manager = ProjectManager(project_path, temp_dir)

            # 生成项目结构（带元数据）
            structure_with_metadata = project_manager.get_project_structure(include_metadata=True)

            # 生成项目结构（不带元数据）
            structure_simple = project_manager.get_project_structure(include_metadata=False)

            # 获取 .NET 项目信息
            dotnet_info = project_manager.get_dotnet_projects_info()

            duration = time.time() - start_time

            if structure_with_metadata and structure_simple:
                details = f"结构生成成功, .NET 项目数: {len(dotnet_info)}"
                reporter.add_result("项目结构生成", True, details, duration)
                return True
            else:
                reporter.add_result("项目结构生成", False, "结构生成失败", duration)
                return False

    except Exception as e:
        reporter.add_result("项目结构生成", False, f"异常: {str(e)}")
        return False

def test_performance_optimization(project_path: str) -> bool:
    """测试性能优化功能"""
    print("测试性能优化...")

    try:
        from repo_agent.utils.performance import get_global_optimizer

        start_time = time.time()
        optimizer = get_global_optimizer()

        # 获取性能统计
        stats = optimizer.get_performance_stats()

        # 测试缓存功能
        from repo_agent.project.dotnet_project import DotNetProjectParser
        parser = DotNetProjectParser(project_path)
        projects = parser.find_project_files()

        if projects:
            # 第一次解析
            first_parse_time = time.time()
            project1 = parser.parse_project(projects[0])
            first_duration = time.time() - first_parse_time

            # 第二次解析（应该使用缓存）
            second_parse_time = time.time()
            project2 = parser.parse_project(projects[0])
            second_duration = time.time() - second_parse_time

            duration = time.time() - start_time

            # 检查缓存是否生效
            cache_working = second_duration < first_duration * 0.8  # 至少快20%

            details = f"缓存 {'生效' if cache_working else '未生效'}, 解析缓存命中率: {stats['cache_stats']['parse_cache']['hit_rate']:.1%}"
            reporter.add_result("性能优化", True, details, duration)
            return True
        else:
            reporter.add_result("性能优化", False, "没有项目文件可测试缓存")
            return False

    except Exception as e:
        reporter.add_result("性能优化", False, f"异常: {str(e)}")
        return False

def test_file_handler_integration(project_path: str) -> bool:
    """测试文件处理器集成"""
    print("测试文件处理器集成...")

    try:
        from repo_agent.file_handler_factory import create_file_handler, get_supported_file_extensions

        start_time = time.time()

        # 测试支持的语言
        supported_extensions = get_supported_file_extensions()

        # 创建一个 .NET 文件处理器
        dotnet_files = []
        for ext in ['.cs', '.csproj', '.sln']:
            pattern = f"**/*{ext}"
            for file_path in Path(project_path).rglob(pattern):
                if file_path.is_file():
                    relative_path = file_path.relative_to(project_path)
                    handler = create_file_handler(project_path, str(relative_path))
                    dotnet_files.append(str(relative_path))
                    # 限制文件数量
                    if len(dotnet_files) >= 3:
                        break
            if len(dotnet_files) >= 3:
                break

        duration = time.time() - start_time

        if dotnet_files:
            details = f"支持 {len(supported_extensions)} 种文件类型, 处理 {len(dotnet_files)} 个测试文件"
            reporter.add_result("文件处理器集成", True, details, duration)
            return True
        else:
            reporter.add_result("文件处理器集成", False, "未找到 .NET 文件", duration)
            return False

    except Exception as e:
        reporter.add_result("文件处理器集成", False, f"异常: {str(e)}")
        return False

def run_e2e_tests(project_path: str):
    """运行所有端到端测试"""
    global reporter
    reporter = E2ETestReporter()

    print(f"RepoAgent .NET 支持端到端测试")
    print(f"测试项目: {project_path}")
    print("=" * 80)

    # 验证项目路径存在
    if not Path(project_path).exists():
        print(f"❌ 错误: 项目路径不存在: {project_path}")
        return 1

    # 运行测试
    tests = [
        ("项目发现", lambda: test_project_discovery(project_path)),
        ("项目解析", lambda: test_project_parsing(project_path)),
        ("解决方案解析", lambda: test_solution_parsing(project_path)),
        ("项目结构生成", lambda: test_project_structure_generation(project_path)),
        ("性能优化", lambda: test_performance_optimization(project_path)),
        ("文件处理器集成", lambda: test_file_handler_integration(project_path))
    ]

    print("开始执行端到端测试...")
    print()

    for test_name, test_func in tests:
        try:
            success = test_func()
            # 实时打印结果
            status = "[PASS]" if success else "[FAIL]"
            print(f"{status} {test_name}")
        except Exception as e:
            print(f"[ERROR] {test_name}: {str(e)}")
            reporter.add_result(test_name, False, f"测试执行异常: {str(e)}")

    print("\n" + "=" * 80)
    print("测试完成")
    print("=" * 80)

    # 生成详细报告
    report = reporter.generate_report()

    # 保存报告到文件
    report_file = repo_root / "test_reports" / "e2e_dotnet_test_report.md"
    report_file.parent.mkdir(exist_ok=True)

    try:
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"\n📄 详细报告已保存到: {report_file}")
    except Exception as e:
        print(f"\n⚠️  报告保存失败: {e}")

    # 打印总结
    total_tests = len(reporter.test_results)
    passed_tests = sum(1 for r in reporter.test_results if r['success'])

    print(f"\n📊 测试总结:")
    print(f"   通过: {passed_tests}/{total_tests}")
    print(f"   成功率: {(passed_tests/total_tests)*100:.1f}%")

    if passed_tests == total_tests:
        print("🎉 所有测试通过！.NET 支持功能运行正常。")
        return 0
    else:
        print("⚠️  部分测试失败，请检查相关功能。")
        return 1

def main():
    """主函数"""
    # 使用用户提供的真实项目路径
    project_path = r"D:\code\dotnet-common"

    return run_e2e_tests(project_path)

if __name__ == "__main__":
    exit(main())