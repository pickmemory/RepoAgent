import os
from pathlib import Path

import jedi
from repo_agent.file_handler_factory import get_supported_file_extensions
from repo_agent.project.dotnet_project import DotNetProjectParser
from repo_agent.log import logger


class ProjectManager:
    def __init__(self, repo_path, project_hierarchy):
        self.repo_path = repo_path
        self.project = jedi.Project(self.repo_path)
        self.project_hierarchy = os.path.join(
            self.repo_path, project_hierarchy, "project_hierarchy.json"
        )

        # 初始化 .NET 项目解析器
        self.dotnet_parser = None
        self._init_dotnet_parser()

    def _init_dotnet_parser(self):
        """初始化 .NET 项目解析器"""
        try:
            self.dotnet_parser = DotNetProjectParser(self.repo_path)
            logger.debug(".NET 项目解析器已初始化")
        except Exception as e:
            logger.warning(f".NET 项目解析器初始化失败: {e}")
            self.dotnet_parser = None

    def get_project_structure(self, include_metadata=True):
        """
        Returns the structure of the project by recursively walking through the directory tree.
        Supports both Python and .NET projects with metadata.

        Args:
            include_metadata: 是否包含项目元数据信息

        Returns:
            str: The project structure as a string, optionally with metadata.
        """
        structure = []

        # 添加仓库根目录
        repo_name = os.path.basename(self.repo_path) or "repository"
        structure.append(repo_name)

        # 如果需要包含元数据
        if include_metadata:
            metadata = self._analyze_project_metadata()
            if metadata:
                structure.extend([f"  {m}" for m in metadata])

        # 遍历目录结构
        def walk_dir(root, prefix="  "):
            items = sorted(os.listdir(root))
            dirs = []
            files = []

            # 分离目录和文件
            for name in items:
                if name.startswith('.'):
                    continue
                path = os.path.join(root, name)
                if os.path.isdir(path):
                    dirs.append(name)
                elif os.path.isfile(path):
                    supported_extensions = get_supported_file_extensions()
                    if any(name.endswith(ext) for ext in supported_extensions):
                        files.append(name)

            # 先添加目录
            for name in dirs:
                structure.append(prefix + name + "/")
                walk_dir(os.path.join(root, name), prefix + "  ")

            # 再添加文件
            for name in files:
                # 添加文件类型标记
                marker = self._get_file_marker(name)
                structure.append(prefix + name + marker)

        walk_dir(self.repo_path)
        return "\n".join(structure)

    def _analyze_project_metadata(self):
        """分析项目元数据"""
        metadata = []

        # 检测 Python 项目
        python_files = list(Path(self.repo_path).rglob("*.py"))
        if python_files:
            metadata.append(f"📦 Python: {len(python_files)} Python files")

        # 检测 .NET 项目
        if self.dotnet_parser:
            solutions = self.dotnet_parser.find_solution_files()
            projects = self.dotnet_parser.find_project_files()

            if projects:
                # 统计 .NET 文件类型
                cs_files = len([p for p in projects if p.endswith('.csproj')])
                vb_files = len([p for p in projects if p.endswith('.vbproj')])
                fs_files = len([p for p in projects if p.endswith('.fsproj')])

                dotnet_info = f"🎯 .NET: {len(projects)} projects"
                if cs_files:
                    dotnet_info += f" ({cs_files} C#)"
                if vb_files:
                    dotnet_info += f" ({vb_files} VB.NET)"
                if fs_files:
                    dotnet_info += f" ({fs_files} F#)"

                metadata.append(dotnet_info)

                if solutions:
                    metadata.append(f"📋 Solutions: {len(solutions)}")

        return metadata

    def _get_file_marker(self, filename):
        """获取文件类型标记"""
        ext = Path(filename).suffix.lower()

        # Python 文件
        if ext == '.py':
            return " 🐍"
        elif ext == '.pyi':
            return " 🐍💡"

        # .NET 文件
        elif ext == '.cs':
            return " 🔷"
        elif ext == '.csproj':
            return " 📦"
        elif ext == '.sln':
            return " 📋"
        elif ext == '.vb':
            return " 🔵"
        elif ext == '.vbproj':
            return " 📦"
        elif ext == '.fs':
            return " 🟪"
        elif ext == '.fsproj':
            return " 📦"

        # 配置文件
        elif ext in ['.json', '.xml', '.config', '.yml', '.yaml']:
            return " ⚙️"

        # 文档文件
        elif ext in ['.md', '.txt', '.rst']:
            return " 📄"

        return ""

    def get_dotnet_projects_info(self):
        """
        获取 .NET 项目详细信息

        Returns:
            list: .NET 项目信息列表
        """
        if not self.dotnet_parser:
            return []

        projects_info = []

        # 解析所有项目
        project_files = self.dotnet_parser.find_project_files()
        for proj_path in project_files[:10]:  # 限制最多10个项目
            project = self.dotnet_parser.parse_project(proj_path)
            if project:
                projects_info.append({
                    'name': project.name,
                    'path': project.path,
                    'type': project.project_type.value,
                    'language': project.language,
                    'frameworks': [fw.value for fw in project.target_frameworks],
                    'is_web': project.is_web_project,
                    'has_tests': project.has_tests,
                    'source_files_count': len(project.source_files),
                    'dependencies_count': len(project.project_references) + len(project.package_references)
                })

        return projects_info

    def get_solution_info(self, solution_path=None):
        """
        获取解决方案信息

        Args:
            solution_path: 解决方案路径，如果为None则查找第一个

        Returns:
            dict: 解决方案信息
        """
        if not self.dotnet_parser:
            return None

        # 查找解决方案
        if not solution_path:
            solutions = self.dotnet_parser.find_solution_files()
            if not solutions:
                return None
            solution_path = solutions[0]

        # 解析解决方案
        solution = self.dotnet_parser.parse_solution(solution_path)
        if not solution:
            return None

        # 构建返回信息
        return {
            'name': solution.name,
            'path': solution.path,
            'projects_count': len(solution.projects),
            'projects': [
                {
                    'name': proj.name,
                    'type': proj.project_type.value,
                    'language': proj.language,
                    'frameworks': [fw.value for fw in proj.target_frameworks]
                }
                for proj in solution.projects.values()
            ],
            'build_configurations': solution.build_configurations,
            'dependencies': self.dotnet_parser.analyze_project_dependencies(solution)
        }

    def build_path_tree(self, who_reference_me, reference_who, doc_item_path):
        from collections import defaultdict

        def tree():
            return defaultdict(tree)

        path_tree = tree()

        # 构建 who_reference_me 和 reference_who 的树
        for path_list in [who_reference_me, reference_who]:
            for path in path_list:
                parts = path.split(os.sep)
                node = path_tree
                for part in parts:
                    node = node[part]

        # 处理 doc_item_path
        parts = doc_item_path.split(os.sep)
        parts[-1] = "✳️" + parts[-1]  # 在最后一个对象前面加上星号
        node = path_tree
        for part in parts:
            node = node[part]

        def tree_to_string(tree, indent=0):
            s = ""
            for key, value in sorted(tree.items()):
                s += "    " * indent + key + "\n"
                if isinstance(value, dict):
                    s += tree_to_string(value, indent + 1)
            return s

        return tree_to_string(path_tree)


if __name__ == "__main__":
    project_manager = ProjectManager(repo_path="", project_hierarchy="")
    print(project_manager.get_project_structure())
