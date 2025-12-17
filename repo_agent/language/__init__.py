"""
语言支持模块 - 为 RepoAgent 提供多语言支持
"""

from enum import Enum
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from pathlib import Path


class Language(Enum):
    """支持的编程语言枚举"""
    PYTHON = "python"
    CSHARP = "csharp"
    VBNET = "vbnet"
    FSHARP = "fsharp"

    @property
    def display_name(self) -> str:
        """获取语言的显示名称"""
        return {
            Language.PYTHON: "Python",
            Language.CSHARP: "C#",
            Language.VBNET: "VB.NET",
            Language.FSHARP: "F#"
        }[self]

    @property
    def file_extensions(self) -> List[str]:
        """获取该语言支持的文件扩展名"""
        return {
            Language.PYTHON: [".py", ".pyi", ".pyx"],
            Language.CSHARP: [".cs", ".csx"],
            Language.VBNET: [".vb", ".vbx"],
            Language.FSHARP: [".fs", ".fsi", ".fsx"]
        }[self]

    @property
    def project_files(self) -> List[str]:
        """获取该语言的项目文件扩展名"""
        return {
            Language.PYTHON: ["setup.py", "pyproject.toml", "requirements.txt"],
            Language.CSHARP: [".csproj", ".sln"],
            Language.VBNET: [".vbproj", ".sln"],
            Language.FSHARP: [".fsproj", ".sln"]
        }[self]


@dataclass
class LanguageMetadata:
    """语言元数据"""
    language: Language
    file_extensions: List[str]
    project_files: List[str]
    comment_patterns: List[str]
    doc_comment_patterns: List[str]

    def __post_init__(self):
        if not self.file_extensions:
            self.file_extensions = self.language.file_extensions
        if not self.project_files:
            self.project_files = self.language.project_files


@dataclass
class Function:
    """函数/方法的通用表示"""
    name: str
    parameters: List[Dict[str, Any]]
    return_type: str
    is_async: bool = False
    access_level: str = "public"
    language_specific: Optional[Dict[str, Any]] = None
    # 添加位置信息
    start_line: int = 1
    end_line: int = 50

    def __post_init__(self):
        if self.language_specific is None:
            self.language_specific = {}


@dataclass
class Class:
    """类/结构的通用表示"""
    name: str
    base_classes: List[str]
    methods: List[Function]
    properties: List[Dict[str, Any]]
    is_interface: bool = False
    is_abstract: bool = False
    access_level: str = "public"
    language_specific: Optional[Dict[str, Any]] = None
    # 添加位置信息
    start_line: int = 1
    end_line: int = 100

    def __post_init__(self):
        if self.language_specific is None:
            self.language_specific = {}


@dataclass
class Import:
    """导入语句的通用表示"""
    module: str
    name: Optional[str] = None
    alias: Optional[str] = None
    is_wildcard: bool = False
    language_specific: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        if self.language_specific is None:
            self.language_specific = {}


@dataclass
class ProjectStructure:
    """项目结构的通用表示"""
    language: Language
    functions: List[Function]
    classes: List[Class]
    imports: List[Import]
    namespaces: List[str]
    language_metadata: LanguageMetadata


class ILanguageParser(ABC):
    """语言解析器接口"""

    @abstractmethod
    def can_parse(self, file_path: Path) -> bool:
        """判断是否能解析指定文件"""
        pass

    @abstractmethod
    def parse_file(self, file_path: Path) -> ProjectStructure:
        """解析文件并返回项目结构"""
        pass

    @abstractmethod
    def extract_functions(self, ast_node: Any) -> List[Function]:
        """从AST节点中提取函数"""
        pass

    @abstractmethod
    def extract_classes(self, ast_node: Any) -> List[Class]:
        """从AST节点中提取类"""
        pass

    @abstractmethod
    def extract_imports(self, ast_node: Any) -> List[Import]:
        """从AST节点中提取导入语句"""
        pass

    @abstractmethod
    def get_namespaces(self, ast_node: Any) -> List[str]:
        """获取文件中的命名空间"""
        pass


class ILanguageAnalyzer(ABC):
    """语言分析器接口"""

    @abstractmethod
    def analyze_project(self, repo_path: Path, language: Language) -> Dict[str, Any]:
        """分析整个项目"""
        pass

    @abstractmethod
    def get_dependencies(self, file_path: Path) -> List[str]:
        """获取文件的依赖关系"""
        pass

    @abstractmethod
    def extract_metadata(self, file_path: Path) -> LanguageMetadata:
        """提取文件的元数据"""
        pass


class ILanguageDocumentGenerator(ABC):
    """语言文档生成器接口"""

    @abstractmethod
    def generate_function_doc(self, function: Function, context: Dict[str, Any]) -> str:
        """生成函数文档"""
        pass

    @abstractmethod
    def generate_class_doc(self, class_item: Class, context: Dict[str, Any]) -> str:
        """生成类文档"""
        pass

    @abstractmethod
    def generate_namespace_doc(self, namespace: str, context: Dict[str, Any]) -> str:
        """生成命名空间文档"""
        pass

    @abstractmethod
    def format_code_example(self, code: str, language: Language) -> str:
        """格式化代码示例"""
        pass


# 语言特定的元数据定义
DOTNET_METADATA = LanguageMetadata(
    language=Language.CSHARP,
    file_extensions=[".cs", ".csx"],
    project_files=[".csproj", ".sln"],
    comment_patterns=["//", "/*", "*/"],
    doc_comment_patterns=["///", "/**", "*/"]
)

PYTHON_METADATA = LanguageMetadata(
    language=Language.PYTHON,
    file_extensions=[".py", ".pyi", ".pyx"],
    project_files=["setup.py", "pyproject.toml", "requirements.txt"],
    comment_patterns=["#"],
    doc_comment_patterns=['"""', "'''"]
)

# 语言元数据映射
LANGUAGE_METADATA_MAP: Dict[Language, LanguageMetadata] = {
    Language.PYTHON: PYTHON_METADATA,
    Language.CSHARP: DOTNET_METADATA,
    Language.VBNET: DOTNET_METADATA,  # VB.NET 使用类似的元数据
    Language.FSHARP: DOTNET_METADATA   # F# 使用类似的元数据
}


def get_language_metadata(language: Language) -> LanguageMetadata:
    """获取语言的元数据"""
    return LANGUAGE_METADATA_MAP.get(language, DOTNET_METADATA)


def detect_language_from_file(file_path: Path) -> Optional[Language]:
    """根据文件路径检测语言"""
    suffix = file_path.suffix.lower()

    for lang in Language:
        if suffix in lang.file_extensions:
            return lang

    return None


def is_project_file(file_path: Path) -> Optional[Language]:
    """判断是否是项目文件并返回对应语言"""
    file_name = file_path.name.lower()
    suffix = file_path.suffix.lower()

    for lang in Language:
        if suffix in lang.project_files or file_name in lang.project_files:
            return lang

    return None


# 导出主要组件
__all__ = [
    'Language',
    'Function',
    'Class',
    'Import',
    'ProjectStructure',
    'LanguageMetadata',
    'ILanguageParser',
    'ILanguageAnalyzer',
    'ILanguageDocumentGenerator',
    'get_language_metadata',
    'detect_language_from_file',
    'is_project_file'
]

# 可选导入（如果需要语言检测器）
try:
    from .detector import LanguageDetector, detect_project_languages, get_project_language_files
    __all__.extend(['LanguageDetector', 'detect_project_languages', 'get_project_language_files'])
except ImportError:
    pass