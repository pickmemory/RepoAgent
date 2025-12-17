#!/usr/bin/env python3
"""
测试真实的 .NET 项目文档生成功能
为 dotnet-common 项目生成实际的文档
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到 Python 路径
repo_root = Path(__file__).parent
sys.path.insert(0, str(repo_root))

def test_real_documentation_generation():
    """测试真实的文档生成"""
    print("=" * 80)
    print("测试真实的 .NET 项目文档生成")
    print("=" * 80)

    # 设置环境变量以避免API配置问题
    os.environ.setdefault('OPENAI_API_KEY', 'test-key')

    project_path = r"D:\code\dotnet-common"
    output_dir = "dotnet_common_docs"

    try:
        # 1. 测试项目结构生成
        print("1. 生成项目结构...")
        from repo_agent.project_manager import ProjectManager

        project_manager = ProjectManager(project_path, output_dir)

        # 生成带元数据的项目结构
        structure = project_manager.get_project_structure(include_metadata=True)

        # 保存项目结构
        structure_file = Path(output_dir) / "project_structure.txt"
        structure_file.parent.mkdir(exist_ok=True)

        with open(structure_file, 'w', encoding='utf-8') as f:
            f.write("# dotnet-common 项目结构\n\n")
            f.write(structure)

        print(f"   项目结构已保存到: {structure_file}")

        # 2. 获取 .NET 项目详细信息
        print("\n2. 收集 .NET 项目信息...")
        dotnet_projects = project_manager.get_dotnet_projects_info()

        print(f"   找到 {len(dotnet_projects)} 个 .NET 项目:")
        for i, proj in enumerate(dotnet_projects[:5], 1):  # 显示前5个
            print(f"   {i}. {proj['name']} ({proj['type']})")
            print(f"      路径: {proj['path']}")
            print(f"      语言: {proj['language']}")
            frameworks = ', '.join(proj['frameworks'])
            print(f"      框架: {frameworks}")
            print(f"      源文件: {proj['source_files_count']} 个")
            print()

        # 3. 获取解决方案信息
        print("3. 解析解决方案信息...")
        solution_info = project_manager.get_solution_info()

        if solution_info:
            print(f"   解决方案: {solution_info['name']}")
            print(f"   包含项目: {solution_info['projects_count']} 个")
            build_configs = len(solution_info['build_configurations'])
            print(f"   构建配置: {build_configs} 个")
            print()

        # 4. 生成每个项目的文档
        print("4. 为 .NET 项目生成文档...")

        from repo_agent.project.dotnet_project import DotNetProjectParser
        from repo_agent.documenters.dotnet_documenter import DotNetDocumentGenerator
        from repo_agent.prompts.dotnet_prompts import DotNetPromptGenerator

        parser = DotNetProjectParser(project_path)
        doc_generator = DotNetDocumentGenerator()
        prompt_generator = DotNetPromptGenerator()

        # 处理前3个项目作为示例
        projects = parser.find_project_files()
        processed_count = 0

        for i, proj_path in enumerate(projects[:3]):
            try:
                print(f"   处理项目 {i+1}: {proj_path}")

                # 解析项目
                project = parser.parse_project(proj_path)
                if not project:
                    print(f"   ✗ 无法解析项目: {proj_path}")
                    continue

                # 生成项目文档
                project_docs = doc_generator.generate_documentation(
                    project_structure=None,  # 暂时不使用
                    output_path=Path(output_dir) / project.name
                )

                print(f"   ✓ 生成文档: {len(project_docs)} 个文件")

                # 生成项目总结
                summary_file = Path(output_dir) / project.name / "README.md"
                summary_file.parent.mkdir(parents=True, exist_ok=True)

                with open(summary_file, 'w', encoding='utf-8') as f:
                    f.write(f"# {project.name}\n\n")
                    f.write(f"## 项目信息\n")
                    f.write(f"- **类型**: {project.project_type.value}\n")
                    f.write(f"- **语言**: {project.language}\n")

                    frameworks_list = [fw.value for fw in project.target_frameworks]
                    frameworks_str = ', '.join(frameworks_list)
                    f.write(f"- **目标框架**: {frameworks_str}\n")
                    f.write(f"- **路径**: {project.path}\n\n")

                    if project.source_files:
                        f.write(f"## 源代码文件 ({len(project.source_files)} 个)\n\n")
                        for src in project.source_files[:10]:  # 显示前10个
                            f.write(f"- `{src}`\n")
                        if len(project.source_files) > 10:
                            remaining = len(project.source_files) - 10
                            f.write(f"- ... 还有 {remaining} 个文件\n")
                        f.write("\n")

                    if project.package_references:
                        f.write(f"## 包依赖 ({len(project.package_references)} 个)\n\n")
                        for pkg in project.package_references[:10]:  # 显示前10个
                            version = f" ({pkg.version})" if pkg.version else ""
                            f.write(f"- `{pkg.name}`{version}\n")
                        if len(project.package_references) > 10:
                            remaining = len(project.package_references) - 10
                            f.write(f"- ... 还有 {remaining} 个包\n")
                        f.write("\n")

                processed_count += 1

            except Exception as e:
                print(f"   ✗ 处理项目失败: {proj_path} - {e}")

        # 5. 生成总体报告
        print("\n5. 生成总体文档报告...")

        overall_file = Path(output_dir) / "README.md"
        with open(overall_file, 'w', encoding='utf-8') as f:
            f.write("# dotnet-common 项目文档\n\n")
            f.write(f"本目录包含了使用 RepoAgent 生成的 dotnet-common 项目文档。\n\n")
            f.write(f"## 项目概览\n\n")
            f.write(f"- **总项目数**: {len(dotnet_projects)}\n")
            f.write(f"- **生成时间**: {os.popen('date').read().strip()}\n\n")

            f.write("## 生成的文档\n\n")
            for proj in dotnet_projects:
                proj_dir = Path(output_dir) / proj['name']
                if proj_dir.exists():
                    f.write(f"- [{proj['name']}]({proj['name']}/) - {proj['type']}\n")

            f.write(f"\n## 项目结构\n\n")
            f.write("详细的项目结构请查看: [project_structure.txt](project_structure.txt)\n")

        print(f"\n📁 文档已生成到目录: {output_dir}")
        print(f"📊 处理了 {processed_count} 个项目")
        print(f"📄 生成 {len(dotnet_projects)} 个项目的文档")

        return True

    except Exception as e:
        print(f"❌ 文档生成失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    success = test_real_documentation_generation()

    if success:
        print("\n🎉 文档生成完成！")
        print("请查看 'dotnet_common_docs' 目录中的生成文档。")
        return 0
    else:
        print("\n❌ 文档生成失败！")
        return 1

if __name__ == "__main__":
    exit(main())