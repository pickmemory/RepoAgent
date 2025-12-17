"""
.NET 项目解析器 - 解析 .sln 和 .csproj 文件，理解项目结构和依赖关系
"""

import os
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
import logging

from repo_agent.log import logger
from repo_agent.utils.performance import (
    get_global_optimizer,
    performance_monitor,
    cached_operation,
    memory_efficient
)


class ProjectType(Enum):
    """.NET 项目类型"""
    CONSOLE_APP = "console"
    WEB_APP = "web"
    WEB_API = "webapi"
    CLASS_LIBRARY = "classlib"
    MVC = "mvc"
    RAZOR = "razor"
    BLAZOR = "blazor"
    MAUI = "maui"
    XAMARIN = "xamarin"
    TEST = "test"
    WORKER = "worker"
    GMAIL = "grpc"
    UNSPECIFIED = "unspecified"


class TargetFramework(Enum):
    """.NET 目标框架"""
    NET5 = "net5.0"
    NET6 = "net6.0"
    NET7 = "net7.0"
    NET8 = "net8.0"
    NET9 = "net9.0"
    NETCOREAPP3_1 = "netcoreapp3.1"
    NETFRAMEWORK = "net"
    NETSTANDARD = "netstandard"


@dataclass
class ProjectReference:
    """项目引用信息"""
    name: str
    path: str
    project_guid: Optional[str] = None
    is_project_reference: bool = True  # True for project reference, False for package reference
    version: Optional[str] = None
    include_assets: Optional[List[str]] = None
    private_assets: Optional[List[str]] = None


@dataclass
class DotNetProject:
    """.NET 项目信息"""
    name: str
    path: str
    project_type: ProjectType
    target_frameworks: List[TargetFramework]
    language: str = "C#"  # C#, VB.NET, F#
    sdk: Optional[str] = None
    output_type: Optional[str] = None
    assembly_name: Optional[str] = None
    root_namespace: Optional[str] = None
    project_guid: Optional[str] = None

    # 依赖关系
    project_references: List[ProjectReference] = field(default_factory=list)
    package_references: List[ProjectReference] = field(default_factory=list)

    # 文件信息
    source_files: List[str] = field(default_factory=list)
    config_files: List[str] = field(default_factory=list)

    # 构建配置
    configurations: List[str] = field(default_factory=lambda: ["Debug", "Release"])
    platforms: List[str] = field(default_factory=lambda: ["AnyCPU"])

    # 其他属性
    properties: Dict[str, str] = field(default_factory=dict)
    is_web_project: bool = False
    has_tests: bool = False


@dataclass
class DotNetSolution:
    """.NET 解决方案信息"""
    name: str
    path: str
    solution_guid: str
    projects: Dict[str, DotNetProject] = field(default_factory=dict)
    project_dependencies: Dict[str, Set[str]] = field(default_factory=dict)

    # 解决方案级别的配置
    build_configurations: List[Tuple[str, str]] = field(default_factory=list)
    solution_folders: Dict[str, str] = field(default_factory=dict)

    # 全局属性
    global_properties: Dict[str, str] = field(default_factory=dict)


class DotNetProjectParser:
    """.NET 项目解析器"""

    def __init__(self, repo_path: str):
        """
        初始化解析器

        Args:
            repo_path: 仓库根路径
        """
        self.repo_path = Path(repo_path)
        self._projects_cache: Dict[str, DotNetProject] = {}
        self.optimizer = get_global_optimizer()

        # 项目类型检测模式（按优先级排序）
        self._project_type_patterns = {
            ProjectType.WEB_API: [
                r'<Project Sdk="Microsoft\.NET\.Sdk\.Web">',
                r'Microsoft\.AspNetCore\.OpenApi',
                r'Swagger|OpenAPI'
            ],
            ProjectType.WEB_APP: [
                r'<Project Sdk="Microsoft\.NET\.Sdk\.Web">',
                r'<AspNetCoreHostingModel>',
                r'services\.AddMvc|services\.AddRazorPages'
            ],
            ProjectType.TEST: [
                r'Microsoft\.NET\.Test\.Sdk',
                r'xunit|nunit|mstest'
            ],
            ProjectType.MVC: [
                r'Microsoft\.NET\.Sdk\.Razor',
                r'Microsoft\.AspNetCore\.Mvc',
                r'Views|Controllers'
            ],
            ProjectType.CONSOLE_APP: [
                r'<OutputType>Exe</OutputType>',
                r'<OutputExe>.*</OutputExe>'
            ],
            ProjectType.CLASS_LIBRARY: [
                r'Microsoft\.NET\.Sdk(?!\.Web|\.Razor)'
            ]
        }

        # 目标框架正则表达式
        self._target_framework_pattern = re.compile(
            r'<TargetFramework[^>]*>([^<]+)</TargetFramework[^>]*>|'
            r'<TargetFrameworks[^>]*>([^<]+)</TargetFrameworks[^>]*>'
        )

        logger.debug(f".NET 项目解析器已初始化: {repo_path}")

    def parse_solution(self, solution_path: str) -> Optional[DotNetSolution]:
        """
        解析解决方案文件 (.sln)

        Args:
            solution_path: 解决方案文件路径（相对于仓库根目录）

        Returns:
            解析后的解决方案信息，如果解析失败返回 None
        """
        solution_file = self.repo_path / solution_path

        if not solution_file.exists():
            logger.warning(f"解决方案文件不存在: {solution_file}")
            return None

        logger.debug(f"解析解决方案: {solution_path}")

        try:
            with open(solution_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # 解析解决方案 GUID
            solution_guid_match = re.search(
                r'解决方案Guid\s*=\s*"{([^"]+)}"', content
            ) or re.search(
                r'SolutionGuid\s*=\s*"{([^"]+)}"', content
            )

            solution_guid = solution_guid_match.group(1) if solution_guid_match else ""

            # 创建解决方案对象
            solution = DotNetSolution(
                name=solution_file.stem,
                path=solution_path,
                solution_guid=solution_guid
            )

            # 解析项目定义
            self._parse_solution_projects(content, solution)

            # 解析项目依赖关系
            self._parse_solution_dependencies(content, solution)

            # 解析构建配置
            self._parse_solution_configurations(content, solution)

            # 解析解决方案文件夹
            self._parse_solution_folders(content, solution)

            logger.debug(f"解决方案解析完成: {len(solution.projects)} 个项目")
            return solution

        except Exception as e:
            logger.error(f"解析解决方案失败: {solution_path}, 错误: {e}")
            return None

    def _parse_solution_projects(self, content: str, solution: DotNetSolution):
        """解析解决方案中的项目定义"""
        # 匹配项目定义的正则表达式
        project_pattern = re.compile(
            r'Project\("\{([^}]+)}"\)\s*=\s*"([^"]+)",\s*"([^"]+)",\s*"(\{[^}]+\})"'
        )

        for match in project_pattern.finditer(content):
            project_type_guid = match.group(1)
            project_name = match.group(2)
            project_path = match.group(3)
            project_guid = match.group(4)

            # 转换为相对于仓库根目录的路径
            solution_dir = Path(solution.path).parent
            relative_path = solution_dir / project_path
            relative_path = str(relative_path).replace('\\', '/')

            # 解析项目文件
            project = self.parse_project(relative_path, project_guid)
            if project:
                solution.projects[project_guid] = project

    def _parse_solution_dependencies(self, content: str, solution: DotNetSolution):
        """解析解决方案中的项目依赖关系"""
        # 匹配项目依赖关系的正则表达式
        dependency_pattern = re.compile(
            r'\{([^}]+)}\.{([^}]+)}\s*=\s*\{([^}]+)}'
        )

        for match in dependency_pattern.finditer(content):
            project_guid = match.group(1)
            dependency_type = match.group(2)
            dependency_guid = match.group(3)

            if project_guid not in solution.project_dependencies:
                solution.project_dependencies[project_guid] = set()

            if dependency_type == "ProjectDependencies":
                solution.project_dependencies[project_guid].add(dependency_guid)

    def _parse_solution_configurations(self, content: str, solution: DotNetSolution):
        """解析解决方案的构建配置"""
        config_pattern = re.compile(
            r'(?P<config>[^|]+)\|(?P<platform>[^\s=]+)\.Build\.0\s*=\s*(?P<build_config>[^|]+)\|(?P<build_platform>[^\s\r\n]+)'
        )

        for match in config_pattern.finditer(content):
            config = match.group('config').strip()
            platform = match.group('platform').strip()
            build_config = match.group('build_config').strip()
            build_platform = match.group('build_platform').strip()

            solution.build_configurations.append((build_config, build_platform))

        # 如果没有找到配置，使用默认值
        if not solution.build_configurations:
            solution.build_configurations = [("Debug", "AnyCPU"), ("Release", "AnyCPU")]

    def _parse_solution_folders(self, content: str, solution: DotNetSolution):
        """解析解决方案文件夹"""
        folder_pattern = re.compile(
            r'Project\("{2150E333-8FDC-42A3-9474-1A3956D46DE8}"\)\s*=\s*"([^"]+)",\s*"([^"]*)",\s*"(\{[^}]+\})"'
        )

        for match in folder_pattern.finditer(content):
            folder_name = match.group(1)
            folder_path = match.group(2)
            folder_guid = match.group(3)

            solution.solution_folders[folder_guid] = folder_name

    @performance_monitor("parse_project")
    @cached_operation()
    @memory_efficient()
    def parse_project(self, project_path: str, project_guid: Optional[str] = None) -> Optional[DotNetProject]:
        """
        解析项目文件 (.csproj, .fsproj, .vbproj)

        Args:
            project_path: 项目文件路径（相对于仓库根目录）
            project_guid: 项目 GUID（可选）

        Returns:
            解析后的项目信息，如果解析失败返回 None
        """
        # 检查缓存
        if project_path in self._projects_cache:
            return self._projects_cache[project_path]

        project_file = self.repo_path / project_path

        if not project_file.exists():
            logger.warning(f"项目文件不存在: {project_file}")
            return None

        logger.debug(f"解析项目: {project_path}")

        try:
            # 解析 XML
            tree = ET.parse(project_file)
            root = tree.getroot()

            # 确定语言
            language = self._detect_project_language(project_path)

            # 确定项目类型
            project_type = self._detect_project_type(root, project_file)

            # 解析目标框架
            target_frameworks = self._parse_target_frameworks(root)

            # 创建项目对象
            project = DotNetProject(
                name=project_file.stem,
                path=project_path,
                project_type=project_type,
                target_frameworks=target_frameworks,
                language=language,
                project_guid=project_guid
            )

            # 解析项目属性
            self._parse_project_properties(root, project)

            # 解析项目引用
            self._parse_project_references(root, project)

            # 解析包引用
            self._parse_package_references(root, project)

            # 扫描源代码文件
            self._scan_source_files(project)

            # 检测是否为 Web 项目或测试项目
            project.is_web_project = self._is_web_project(root, project)
            project.has_tests = self._has_tests(root, project)

            # 缓存结果
            self._projects_cache[project_path] = project

            logger.debug(f"项目解析完成: {project.name} ({project_type.value})")
            return project

        except Exception as e:
            logger.error(f"解析项目失败: {project_path}, 错误: {e}")
            return None

    def _detect_project_language(self, project_path: str) -> str:
        """检测项目语言"""
        ext = Path(project_path).suffix.lower()
        language_map = {
            '.csproj': 'C#',
            '.vbproj': 'VB.NET',
            '.fsproj': 'F#'
        }
        return language_map.get(ext, 'C#')

    def _detect_project_type(self, root: ET.Element, project_file: Path) -> ProjectType:
        """检测项目类型"""
        # 获取 SDK 属性
        sdk = root.get('Sdk', '')

        # 读取项目内容用于模式匹配
        content = ET.tostring(root, encoding='unicode')

        # 根据模式和 SDK 判断项目类型
        for project_type, patterns in self._project_type_patterns.items():
            for pattern in patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    return project_type

        # 根据 SDK 名称判断
        if 'Web' in sdk:
            return ProjectType.WEB_APP
        elif 'Razor' in sdk:
            return ProjectType.MVC
        elif 'Test' in sdk:
            return ProjectType.TEST
        elif 'Microsoft.NET.Sdk' in sdk:
            return ProjectType.CLASS_LIBRARY

        return ProjectType.UNSPECIFIED

    def _parse_target_frameworks(self, root: ET.Element) -> List[TargetFramework]:
        """解析目标框架"""
        frameworks = []

        # 查找 TargetFramework 或 TargetFrameworks
        for elem in root.iter():
            if elem.tag.endswith('TargetFramework'):
                frameworks.append(TargetFramework(elem.text))
            elif elem.tag.endswith('TargetFrameworks'):
                # 多个框架，用分号分隔
                for fw in elem.text.split(';'):
                    fw = fw.strip()
                    if fw:
                        frameworks.append(TargetFramework(fw))

        return frameworks

    def _parse_project_properties(self, root: ET.Element, project: DotNetProject):
        """解析项目属性"""
        # 常见属性映射
        property_mapping = {
            'Sdk': 'sdk',
            'OutputType': 'output_type',
            'AssemblyName': 'assembly_name',
            'RootNamespace': 'root_namespace',
            'GeneratePackageOnBuild': 'generate_package',
            'Version': 'version',
            'Authors': 'authors',
            'Description': 'description'
        }

        for elem in root.iter():
            if elem.tag.endswith('PropertyGroup'):
                for child in elem:
                    tag_name = child.tag.split('}')[-1]  # 移除命名空间
                    if tag_name in property_mapping:
                        value = child.text or ''
                        setattr(project, property_mapping[tag_name], value)
                    else:
                        project.properties[tag_name] = child.text or ''

        # 解析配置和平台
        for elem in root.iter():
            if elem.tag.endswith('PropertyGroup'):
                condition = elem.get('Condition', '')
                if "'$(Configuration)|$(Platform)'" in condition:
                    # 提取配置名称
                    config_match = re.search(r"'([^|]+)\|", condition)
                    if config_match:
                        config = config_match.group(1)
                        if config not in project.configurations:
                            project.configurations.append(config)

    def _parse_project_references(self, root: ET.Element, project: DotNetProject):
        """解析项目引用"""
        for elem in root.iter():
            if elem.tag.endswith('ProjectReference'):
                include = elem.get('Include', '')
                if include:
                    # 转换为相对于仓库根目录的路径
                    project_dir = Path(project.path).parent
                    ref_path = project_dir / include
                    ref_path = str(ref_path).replace('\\', '/')

                    project_ref = ProjectReference(
                        name=Path(include).stem,
                        path=ref_path,
                        is_project_reference=True
                    )
                    project.project_references.append(project_ref)

    def _parse_package_references(self, root: ET.Element, project: DotNetProject):
        """解析包引用"""
        for elem in root.iter():
            if elem.tag.endswith('PackageReference'):
                include = elem.get('Include', '')
                version = elem.get('Version', '')

                if include:
                    package_ref = ProjectReference(
                        name=include,
                        path="",  # 包引用没有路径
                        is_project_reference=False,
                        version=version
                    )
                    project.package_references.append(package_ref)

    def _scan_source_files(self, project: DotNetProject):
        """扫描项目的源代码文件"""
        project_dir = self.repo_path / Path(project.path).parent

        # 支持的文件扩展名
        extensions = {
            'C#': ['.cs'],
            'VB.NET': ['.vb'],
            'F#': ['.fs', '.fsi', '.fsx']
        }

        for ext in extensions.get(project.language, []):
            pattern = f"**/*{ext}"
            for file_path in project_dir.glob(pattern):
                relative_path = file_path.relative_to(self.repo_path)
                project.source_files.append(str(relative_path))

        # 扫描配置文件
        config_patterns = ['*.json', '*.xml', '*.config', '*.yml', '*.yaml']
        for pattern in config_patterns:
            for file_path in project_dir.glob(pattern):
                relative_path = file_path.relative_to(self.repo_path)
                project.config_files.append(str(relative_path))

    def _is_web_project(self, root: ET.Element, project: DotNetProject) -> bool:
        """检查是否为 Web 项目"""
        # 检查 SDK
        if 'Web' in root.get('Sdk', ''):
            return True

        # 检查包引用
        web_packages = [
            'Microsoft.AspNetCore.App',
            'Microsoft.AspNetCore.Mvc',
            'Microsoft.AspNetCore.All'
        ]

        for package_ref in project.package_references:
            if any(web_pkg in package_ref.name for web_pkg in web_packages):
                return True

        return False

    def _has_tests(self, root: ET.Element, project: DotNetProject) -> bool:
        """检查是否为测试项目"""
        # 检查 SDK
        if 'Test' in root.get('Sdk', ''):
            return True

        # 检查包引用
        test_packages = [
            'Microsoft.NET.Test.Sdk',
            'xunit',
            'nunit',
            'mstest',
            'Moq',
            'Shouldly'
        ]

        for package_ref in project.package_references:
            if any(test_pkg.lower() in package_ref.name.lower() for test_pkg in test_packages):
                return True

        # 检查项目名称
        test_patterns = ['Test', 'Tests', 'Specification', 'Spec']
        if any(pattern in project.name for pattern in test_patterns):
            return True

        return False

    def find_solution_files(self) -> List[str]:
        """
        在仓库中查找所有解决方案文件

        Returns:
            找到的解决方案文件路径列表
        """
        solutions = []

        for sln_file in self.repo_path.rglob("*.sln"):
            relative_path = sln_file.relative_to(self.repo_path)
            solutions.append(str(relative_path))

        return solutions

    def find_project_files(self) -> List[str]:
        """
        在仓库中查找所有项目文件

        Returns:
            找到的项目文件路径列表
        """
        projects = []
        patterns = ["*.csproj", "*.fsproj", "*.vbproj"]

        for pattern in patterns:
            for proj_file in self.repo_path.rglob(pattern):
                relative_path = proj_file.relative_to(self.repo_path)
                projects.append(str(relative_path))

        return projects

    def analyze_project_dependencies(self, solution: DotNetSolution) -> Dict[str, List[str]]:
        """
        分析项目依赖关系

        Args:
            solution: 解决方案信息

        Returns:
            项目依赖关系字典 {项目GUID: [依赖项目GUID列表]}
        """
        dependencies = {}

        # 初始化所有项目的依赖列表
        for proj_guid in solution.projects:
            dependencies[proj_guid] = []

        # 添加解决方案级别的依赖
        for proj_guid, deps in solution.project_dependencies.items():
            if proj_guid in dependencies:
                dependencies[proj_guid].extend(list(deps))

        # 添加项目引用依赖
        for proj_guid, project in solution.projects.items():
            for proj_ref in project.project_references:
                # 查找引用项目的 GUID
                for other_guid, other_proj in solution.projects.items():
                    if proj_ref.path == other_proj.path:
                        dependencies[proj_guid].append(other_guid)
                        break

        return dependencies