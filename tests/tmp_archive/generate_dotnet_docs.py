#!/usr/bin/env python3
"""
为 .NET 项目生成基本的项目文档
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到 Python 路径
repo_root = Path(__file__).parent
sys.path.insert(0, str(repo_root))

def generate_basic_docs():
    """生成基本的项目文档"""
    print("=" * 80)
    print("为 dotnet-common 生成项目文档")
    print("=" * 80)

    project_path = r"D:\code\dotnet-common"
    output_dir = "dotnet_common_docs"

    try:
        from repo_agent.project.dotnet_project import DotNetProjectParser

        parser = DotNetProjectParser(project_path)
        projects = parser.find_project_files()

        print(f"找到 {len(projects)} 个项目，开始生成文档...\n")

        # 为每个项目生成基本文档
        for i, proj_path in enumerate(projects):
            try:
                print(f"{i+1}. 处理项目: {proj_path}")

                # 解析项目
                project = parser.parse_project(proj_path)
                if not project:
                    print(f"   跳过: 无法解析")
                    continue

                # 创建项目文档目录
                proj_name = project.name.replace('.', '_').replace(' ', '_')
                proj_dir = Path(output_dir) / proj_name
                proj_dir.mkdir(parents=True, exist_ok=True)

                # 生成项目README
                readme_file = proj_dir / "README.md"
                with open(readme_file, 'w', encoding='utf-8') as f:
                    f.write(f"# {project.name}\n\n")
                    f.write(f"## 项目信息\n\n")
                    f.write(f"- **项目类型**: {project.project_type.value}\n")
                    f.write(f"- **编程语言**: {project.language}\n")
                    f.write(f"- **目标框架**: {', '.join([fw.value for fw in project.target_frameworks])}\n")
                    f.write(f"- **项目文件**: {project.path}\n\n")

                    # 项目描述
                    f.write("## 项目描述\n\n")
                    if project.is_web_project:
                        f.write("这是一个Web应用程序项目。\n\n")
                    elif project.project_type.value == "classlib":
                        f.write("这是一个类库项目。\n\n")
                    elif project.project_type.value == "test":
                        f.write("这是一个测试项目。\n\n")
                    else:
                        f.write(f"这是一个{project.project_type.value}类型的项目。\n\n")

                    # 源代码文件
                    if project.source_files:
                        f.write(f"## 源代码文件 ({len(project.source_files)} 个)\n\n")
                        # 按目录组织显示
                        dirs = {}
                        for src in project.source_files:
                            src_dir = Path(src).parent
                            if src_dir.name:
                                if src_dir not in dirs:
                                    dirs[src_dir] = []
                                dirs[src_dir].append(Path(src).name)

                        for directory, files in sorted(dirs.items()):
                            f.write(f"### {directory}/\n\n")
                            for file in sorted(files):
                                f.write(f"- `{file}`\n")
                            f.write("\n")

                    # 包依赖
                    if project.package_references:
                        f.write(f"## 包依赖 ({len(project.package_references)} 个)\n\n")
                        for pkg in project.package_references:
                            version = f" ({pkg.version})" if pkg.version else ""
                            f.write(f"- `{pkg.name}`{version}\n")
                        f.write("\n")

                    # 项目引用
                    if project.project_references:
                        f.write(f"## 项目引用 ({len(project.project_references)} 个)\n\n")
                        for ref in project.project_references:
                            f.write(f"- `{ref.name}` -> `{ref.path}`\n")
                        f.write("\n")

                    # 配置信息
                    if project.configurations:
                        f.write("## 构建配置\n\n")
                        for config in project.configurations:
                            f.write(f"- {config}\n")
                        f.write("\n")

                print(f"   ✓ 已生成: {readme_file}")

                # 生成文件列表
                files_list = proj_dir / "files.md"
                with open(files_list, 'w', encoding='utf-8') as f:
                    f.write(f"# {project.name} - 文件列表\n\n")
                    f.write(f"总计 {len(project.source_files)} 个源代码文件:\n\n")

                    if project.source_files:
                        for i, src in enumerate(project.source_files, 1):
                            f.write(f"{i:2d}. `{src}`\n")

                print(f"   ✓ 已生成: {files_list}")

                # 生成依赖分析
                if project.package_references or project.project_references:
                    deps_file = proj_dir / "dependencies.md"
                    with open(deps_file, 'w', encoding='utf-8') as f:
                        f.write(f"# {project.name} - 依赖分析\n\n")

                        if project.package_references:
                            f.write("## NuGet 包依赖\n\n")
                            for pkg in sorted(project.package_references, key=lambda x: x.name):
                                version = f" ({pkg.version})" if pkg.version else ""
                                f.write(f"- **{pkg.name}**{version}\n")
                            f.write("\n")

                        if project.project_references:
                            f.write("## 项目引用\n\n")
                            for ref in project.project_references:
                                f.write(f"- **{ref.name}**\n")
                            f.write(f"  - 路径: `{ref.path}`\n")
                            f.write(f"  - 类型: 项目引用\n")
                            f.write("\n")

                    print(f"   ✓ 已生成: {deps_file}")

            except Exception as e:
                print(f"   ❌ 处理失败: {e}")

        # 生成总体概览
        overview_file = Path(output_dir) / "README.md"
        with open(overview_file, 'w', encoding='utf-8') as f:
            f.write("# dotnet-common 项目文档概览\n\n")
            f.write("本目录包含了使用 RepoAgent 为 dotnet-common 项目生成的文档。\n\n")

            f.write("## 项目列表\n\n")
            processed_projects = 0
            for proj_path in projects:
                try:
                    project = parser.parse_project(proj_path)
                    if project:
                        proj_name = project.name.replace('.', '_').replace(' ', '_')
                        f.write(f"- [{project.name}]({proj_name}/) - {project.project_type.value}\n")
                        processed_projects += 1
                except:
                    continue

            f.write(f"\n## 统计信息\n\n")
            f.write(f"- 总项目数: {len(projects)}\n")
            f.write(f"- 成功处理: {processed_projects}\n")
            f.write(f"- 生成时间: {os.popen('date').read().strip()}\n")

        print(f"\n🎉 文档生成完成！")
        print(f"📁 输出目录: {output_dir}")
        print(f"📊 处理项目: {processed_projects}/{len(projects)}")

        return True

    except Exception as e:
        print(f"❌ 文档生成失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = generate_basic_docs()
    exit(0 if success else 1)