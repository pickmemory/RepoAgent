"""
测试 .NET 项目解析器
"""

import os
from pathlib import Path
from repo_agent.project.dotnet_project import DotNetProjectParser
from repo_agent.log import logger

def test_project_parser():
    """测试项目解析器功能"""

    # 设置日志级别
    import logging
    logging.basicConfig(level=logging.DEBUG)

    # 创建解析器
    parser = DotNetProjectParser(".")

    print("=" * 60)
    print("测试 .NET 项目解析器")
    print("=" * 60)

    # 查找所有解决方案和项目文件
    solutions = parser.find_solution_files()
    projects = parser.find_project_files()

    print(f"\n找到 {len(solutions)} 个解决方案文件:")
    for sln in solutions[:5]:  # 只显示前5个
        print(f"  - {sln}")
    if len(solutions) > 5:
        print(f"  ... 还有 {len(solutions) - 5} 个")

    print(f"\n找到 {len(projects)} 个项目文件:")
    for proj in projects[:10]:  # 只显示前10个
        print(f"  - {proj}")
    if len(projects) > 10:
        print(f"  ... 还有 {len(projects) - 10} 个")

    # 测试解析单个项目
    if projects:
        print("\n" + "=" * 40)
        print("测试解析单个项目")
        print("=" * 40)

        # 选择一个C#项目进行测试
        csproj_files = [p for p in projects if p.endswith('.csproj')]
        if csproj_files:
            test_project = csproj_files[0]
            print(f"\n解析项目: {test_project}")

            project = parser.parse_project(test_project)

            if project:
                print(f"\n项目信息:")
                print(f"  名称: {project.name}")
                print(f"  类型: {project.project_type.value}")
                print(f"  语言: {project.language}")
                print(f"  目标框架: {[fw.value for fw in project.target_frameworks]}")
                print(f"  输出类型: {project.output_type}")
                print(f"  程序集名: {project.assembly_name}")
                print(f"  根命名空间: {project.root_namespace}")
                print(f"  是否为Web项目: {project.is_web_project}")
                print(f"  是否包含测试: {project.has_tests}")

                print(f"\n项目引用 ({len(project.project_references)}):")
                for ref in project.project_references[:5]:
                    print(f"  - {ref.name} -> {ref.path}")
                if len(project.project_references) > 5:
                    print(f"  ... 还有 {len(project.project_references) - 5} 个")

                print(f"\n包引用 ({len(project.package_references)}):")
                for pkg in project.package_references[:5]:
                    version = f" ({pkg.version})" if pkg.version else ""
                    print(f"  - {pkg.name}{version}")
                if len(project.package_references) > 5:
                    print(f"  ... 还有 {len(project.package_references) - 5} 个")

                print(f"\n源代码文件 ({len(project.source_files)}):")
                for src in project.source_files[:5]:
                    print(f"  - {src}")
                if len(project.source_files) > 5:
                    print(f"  ... 还有 {len(project.source_files) - 5} 个")

                print(f"\n配置文件 ({len(project.config_files)}):")
                for cfg in project.config_files[:5]:
                    print(f"  - {cfg}")
                if len(project.config_files) > 5:
                    print(f"  ... 还有 {len(project.config_files) - 5} 个")
            else:
                print("项目解析失败")
        else:
            print("未找到C#项目文件")

    # 测试解析解决方案
    if solutions:
        print("\n" + "=" * 40)
        print("测试解析解决方案")
        print("=" * 40)

        test_solution = solutions[0]
        print(f"\n解析解决方案: {test_solution}")

        solution = parser.parse_solution(test_solution)

        if solution:
            print(f"\n解决方案信息:")
            print(f"  名称: {solution.name}")
            print(f"  路径: {solution.path}")
            print(f"  GUID: {solution.solution_guid}")
            print(f"  项目数量: {len(solution.projects)}")

            print(f"\n包含的项目:")
            for guid, proj in solution.projects.items():
                print(f"  - {proj.name} ({proj.project_type.value})")

            print(f"\n构建配置:")
            for config, platform in solution.build_configurations:
                print(f"  - {config}|{platform}")

            # 分析依赖关系
            dependencies = parser.analyze_project_dependencies(solution)
            print(f"\n项目依赖关系:")
            for proj_guid, deps in dependencies.items():
                if deps and proj_guid in solution.projects:
                    proj_name = solution.projects[proj_guid].name
                    dep_names = []
                    for dep_guid in deps:
                        if dep_guid in solution.projects:
                            dep_names.append(solution.projects[dep_guid].name)
                    if dep_names:
                        print(f"  {proj_name} -> {', '.join(dep_names)}")
        else:
            print("解决方案解析失败")

    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)

if __name__ == "__main__":
    test_project_parser()