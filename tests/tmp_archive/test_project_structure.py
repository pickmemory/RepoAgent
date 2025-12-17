"""
测试增强的项目结构生成功能
"""

from repo_agent.project_manager import ProjectManager

def test_enhanced_project_structure():
    """测试增强的项目结构生成"""

    print("=" * 70)
    print("测试增强的项目结构生成 (支持 Python + .NET)")
    print("=" * 70)

    # 创建项目管理者
    project_manager = ProjectManager(".", "hierarchy")

    # 1. 测试基本项目结构（带元数据）
    print("\n1. 项目结构（带元数据标记）:")
    print("-" * 50)
    structure = project_manager.get_project_structure(include_metadata=True)
    try:
        print(structure)
    except UnicodeEncodeError:
        # 如果遇到编码问题，替换Unicode字符
        structure_safe = structure.replace('📦', '[Python]').replace('🎯', '[.NET]').replace('📋', '[Solution]')
        structure_safe = structure_safe.replace('🐍', '[PY]').replace('🔷', '[CS]').replace('🔵', '[VB]')
        structure_safe = structure_safe.replace('🟪', '[FS]').replace('📦', '[PROJ]').replace('⚙️', '[CONFIG]')
        structure_safe = structure_safe.replace('📄', '[DOC]')
        print(structure_safe)

    # 2. 测试基本项目结构（不带元数据）
    print("\n\n2. 项目结构（仅文件树）:")
    print("-" * 50)
    structure_simple = project_manager.get_project_structure(include_metadata=False)
    try:
        print(structure_simple)
    except UnicodeEncodeError:
        structure_simple_safe = structure_simple.replace('🐍', '[PY]').replace('🔷', '[CS]')
        structure_simple_safe = structure_simple_safe.replace('📦', '[PROJ]').replace('📋', '[Solution]')
        print(structure_simple_safe)

    # 3. 测试 .NET 项目信息
    print("\n\n3. .NET 项目详细信息:")
    print("-" * 50)
    dotnet_info = project_manager.get_dotnet_projects_info()
    if dotnet_info:
        for idx, info in enumerate(dotnet_info, 1):
            print(f"\n项目 {idx}: {info['name']}")
            print(f"  路径: {info['path']}")
            print(f"  类型: {info['type']}")
            print(f"  语言: {info['language']}")
            print(f"  框架: {', '.join(info['frameworks'])}")
            print(f"  Web项目: {'是' if info['is_web'] else '否'}")
            print(f"  包含测试: {'是' if info['has_tests'] else '否'}")
            print(f"  源文件数: {info['source_files_count']}")
            print(f"  依赖数: {info['dependencies_count']}")
    else:
        print("未找到 .NET 项目")

    # 4. 测试解决方案信息
    print("\n\n4. 解决方案信息:")
    print("-" * 50)
    solution_info = project_manager.get_solution_info()
    if solution_info:
        print(f"\n解决方案: {solution_info['name']}")
        print(f"  路径: {solution_info['path']}")
        print(f"  项目数: {solution_info['projects_count']}")

        print("\n包含的项目:")
        for proj in solution_info['projects']:
            frameworks = ', '.join(proj['frameworks'])
            print(f"  - {proj['name']} ({proj['type']}, {proj['language']}, {frameworks})")

        print("\n构建配置:")
        for config, platform in solution_info['build_configurations']:
            print(f"  - {config}|{platform}")

        print("\n项目依赖关系:")
        for proj_guid, deps in solution_info['dependencies'].items():
            if deps:
                # 查找项目名称
                proj_name = None
                for proj in solution_info['projects']:
                    # 简化：这里假设项目名称不重复
                    pass
                print(f"  项目依赖: {len(deps)} 个依赖")
    else:
        print("未找到解决方案文件")

    # 5. 文件类型标记说明
    print("\n\n5. 文件类型标记说明:")
    print("-" * 50)
    markers = [
        ("[PY]", "Python 源文件"),
        ("[PY💡]", "Python 类型存根文件"),
        ("[CS]", "C# 源文件"),
        ("[VB]", "VB.NET 源文件"),
        ("[FS]", "F# 源文件"),
        ("[PROJ]", ".NET 项目文件"),
        ("[Solution]", "Visual Studio 解决方案文件"),
        ("[CONFIG]", "配置文件"),
        ("[DOC]", "文档文件")
    ]
    for marker, desc in markers:
        print(f"  {marker} {desc}")

    print("\n" + "=" * 70)
    print("测试完成")
    print("=" * 70)

if __name__ == "__main__":
    test_enhanced_project_structure()