"""
扩展文件处理器 - 支持多语言（包括 .NET）的文件处理
"""

import os
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass

from repo_agent.language import (
    Language, detect_language_from_file,
    ProjectStructure, Function, Class, Import
)
from repo_agent.file_handler import FileHandler
from repo_agent.log import logger
from repo_agent.parsers.dotnet_parser import DotNetParser, AnalysisStrategy
from repo_agent.parsers.tree_sitter_parser import is_tree_sitter_available, get_tree_sitter_wrapper


@dataclass
class MultiLanguageConfig:
    """多语言配置"""
    enable_dotnet: bool = True
    enable_treesitter: bool = True
    prefer_roslyn: bool = False
    dotnet_strategy: str = "auto"  # auto, tree-sitter, roslyn, hybrid
    treesitter_fallback: bool = True


class MultiLanguageFileHandler(FileHandler):
    """扩展的文件处理器，支持多语言解析"""

    def __init__(self, repo_path: str, file_path: str, config: Optional[MultiLanguageConfig] = None):
        """
        初始化多语言文件处理器

        Args:
            repo_path: 仓库路径
            file_path: 文件路径
            config: 多语言配置
        """
        super().__init__(repo_path, file_path)
        self.config = config or MultiLanguageConfig()

        # 初始化多语言解析器
        self._init_parsers()

        # 语言检测缓存
        self._detected_language = None

    def _init_parsers(self):
        """初始化解析器"""
        self.dotnet_parser = None
        self.treesitter_wrapper = None

        # 初始化 .NET 解析器
        if self.config.enable_dotnet:
            try:
                strategy = AnalysisStrategy(self.config.dotnet_strategy)
                self.dotnet_parser = DotNetParser(
                    strategy=strategy,
                    prefer_roslyn_for_large_files=self.config.prefer_roslyn,
                    treesitter_fallback=self.config.treesitter_fallback
                )
                logger.debug(".NET 解析器已初始化")
            except Exception as e:
                logger.warning(f".NET 解析器初始化失败: {e}")

        # 初始化 Tree-sitter 包装器
        if self.config.enable_treesitter and is_tree_sitter_available():
            try:
                self.treesitter_wrapper = get_tree_sitter_wrapper()
                logger.debug("Tree-sitter 包装器已初始化")
            except Exception as e:
                logger.warning(f"Tree-sitter 包装器初始化失败: {e}")

    def detect_language(self) -> Optional[Language]:
        """
        检测文件语言

        Returns:
            检测到的语言，如果无法确定则返回 None
        """
        if self._detected_language is not None:
            return self._detected_language

        file_path = Path(self.repo_path) / self.file_path
        detected = detect_language_from_file(file_path)

        if detected:
            self._detected_language = detected
            logger.debug(f"检测到语言: {detected.value}")

        return self._detected_language

    def read_file(self) -> str:
        """
        读取文件内容（支持多种编码）

        Returns:
            文件内容字符串
        """
        import chardet

        file_path = os.path.join(self.repo_path, self.file_path)

        # 尝试多种编码
        encodings = ['utf-8', 'utf-8-sig', 'gbk', 'gb2312', 'latin1']

        # 先检测编码
        try:
            with open(file_path, 'rb') as f:
                raw_data = f.read()
                detected = chardet.detect(raw_data)
                if detected and detected['confidence'] > 0.7:
                    # 将检测到的编码添加到尝试列表的前面
                    encodings.insert(0, detected['encoding'])
        except Exception:
            pass

        # 尝试用不同的编码读取
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    content = f.read()
                    # 移除 BOM（如果有）
                    if content.startswith('\ufeff'):
                        content = content[1:]
                    return content
            except UnicodeDecodeError:
                continue
            except Exception as e:
                logger.debug(f"读取文件失败（编码 {encoding}）: {e}")
                continue

        # 如果都失败了，使用替换策略
        try:
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
                logger.warning(f"文件 {self.file_path} 使用 UTF-8 替换模式读取，可能包含无效字符")
                return content
        except Exception as e:
            logger.error(f"无法读取文件 {self.file_path}: {e}")
            raise

    def parse_file_structure(self, content: Optional[str] = None) -> Optional[ProjectStructure]:
        """
        解析文件结构（支持多语言）

        Args:
            content: 文件内容，如果为 None 则自动读取

        Returns:
            解析后的项目结构，如果不支持该语言则返回 None
        """
        if content is None:
            content = self.read_file()

        # 检测文件语言
        language = self.detect_language()
        if not language:
            logger.debug(f"无法检测文件语言: {self.file_path}")
            return None

        # 根据语言选择解析器
        if language == Language.CSHARP:
            return self._parse_csharp_file(content)
        elif language == Language.PYTHON:
            return self._parse_python_file(content)
        else:
            logger.debug(f"不支持的语言: {language.value}")
            return None

    def _parse_csharp_file(self, content: str) -> Optional[ProjectStructure]:
        """解析 C# 文件"""
        if not self.dotnet_parser:
            logger.warning(".NET 解析器不可用，跳过 C# 文件解析")
            return None

        try:
            file_path = Path(self.repo_path) / self.file_path
            structure = self.dotnet_parser.parse_file(file_path)
            logger.debug(f"C# 文件解析成功: {len(structure.classes)} 个类, {len(structure.functions)} 个方法")
            return structure
        except Exception as e:
            logger.error(f"C# 文件解析失败: {e}")
            return None

    def _parse_python_file(self, content: str) -> Optional[ProjectStructure]:
        """解析 Python 文件（使用原有逻辑）"""
        # 这里可以集成原有的 Python 解析逻辑
        # 或者使用 Tree-sitter Python 包装器
        if self.treesitter_wrapper:
            try:
                from repo_agent.language import get_language_metadata
                file_path = Path(self.repo_path) / self.file_path
                structure = self.treesitter_wrapper.parse_file(file_path, Language.PYTHON)
                logger.debug(f"Python Tree-sitter 解析成功: {len(structure.classes)} 个类, {len(structure.functions)} 个方法")
                return structure
            except Exception as e:
                logger.warning(f"Tree-sitter Python 解析失败，使用备用方案: {e}")

        # 如果没有 Tree-sitter，可以使用简化的正则表达式解析
        # 这里暂时返回 None，实际项目中应该有更完善的实现
        logger.debug("Python 文件解析未实现")
        return None

    def get_functions_and_classes(self, content: Optional[str] = None) -> List[tuple]:
        """
        获取函数和类列表（支持多语言）

        Args:
            content: 文件内容，如果为 None 则自动读取

        Returns:
            结构元组列表，格式与原有方法兼容
        """
        # 首先尝试使用多语言解析器
        structure = self.parse_file_structure(content)
        if structure:
            return self._convert_structure_to_legacy_format(structure)

        # 如果多语言解析失败，回退到原有方法
        try:
            return super().get_functions_and_classes(content or self.read_file())
        except Exception as e:
            logger.warning(f"传统解析方法失败: {e}")
            return []

    def _convert_structure_to_legacy_format(self, structure: ProjectStructure) -> List[tuple]:
        """
        将 ProjectStructure 转换为原有格式的元组列表

        Args:
            structure: 项目结构对象

        Returns:
            兼容原有格式的元组列表
        """
        legacy_format = []

        # 转换类
        for cls in structure.classes:
            # 构造类元组
            class_tuple = (
                "ClassDef",  # 节点类型
                cls.name,  # 名称
                1,  # 开始行号（简化处理）
                100,  # 结束行号（简化处理）
                None,  # 父类名称（简化处理）
                []  # 参数列表（简化处理）
            )
            legacy_format.append(class_tuple)

        # 转换函数/方法
        for func in structure.functions:
            # 提取参数名列表
            param_names = [p.get('name', '') for p in func.parameters]

            # 构造函数元组
            func_tuple = (
                "FunctionDef",  # 节点类型
                func.name,  # 名称
                1,  # 开始行号（简化处理）
                50,  # 结束行号（简化处理）
                None,  # 父类名称（简化处理）
                param_names
            )
            legacy_format.append(func_tuple)

        return legacy_format

    def _generate_doc_objects_from_structure(self, structure: ProjectStructure) -> List[Dict]:
        """
        从 ProjectStructure 生成文档对象列表

        Args:
            structure: 项目结构对象

        Returns:
            文档对象列表
        """
        doc_objects = []
        file_content = self.read_file()
        lines = file_content.split('\n')
        # 清理所有行的 BOM
        lines = [line.replace('\ufeff', '') if '\ufeff' in line else line for line in lines]

        # 为每个类生成文档对象
        for cls in structure.classes:
            # 提取类的代码内容
            start_line = max(1, cls.start_line - 5)  # 提前几行以获取可能的修饰符
            end_line = min(len(lines), cls.end_line + 5)  # 多取几行以确保完整
            code_content = '\n'.join(lines[start_line - 1:end_line])

            # 获取对象名称在第一行代码中的位置
            name_column = 0
            if start_line <= len(lines):
                first_line = lines[start_line - 1]
                # 移除 BOM 字符（如果有）
                if '\ufeff' in first_line:
                    first_line = first_line.replace('\ufeff', '')
                name_pos = first_line.find(cls.name)
                if name_pos >= 0:
                    name_column = name_pos
                else:
                    name_column = 0

            doc_obj = {
                "type": "class",
                "name": cls.name,
                "content": cls.language_specific.get("documentation", ""),
                "md_content": [],  # 初始为空列表，将由LLM生成
                "functions": [method.name for method in cls.methods],
                "classes": [],  # 类内部嵌套类暂时不处理
                "start_line": cls.start_line,
                "end_line": cls.end_line,
                "parent_class": None,
                "parameters": [],
                "code_start_line": cls.start_line,
                "code_end_line": cls.end_line,
                "code_content": code_content,  # 添加代码内容
                "have_return": False,  # 类不返回值
                "name_column": name_column  # 添加名称位置
            }
            doc_objects.append(doc_obj)

        # 为每个独立函数生成文档对象
        for func in structure.functions:
            # 检查是否是类的成员方法
            is_method = any(func.name in [m.name for m in cls.methods] for cls in structure.classes)

            if not is_method:
                # 提取函数的代码内容
                start_line = max(1, func.start_line - 5)
                end_line = min(len(lines), func.end_line + 5)
                code_content = '\n'.join(lines[start_line - 1:end_line])

                # 获取对象名称在第一行代码中的位置
                name_column = 0
                if start_line <= len(lines):
                    first_line = lines[start_line - 1]
                    # 移除 BOM 字符（如果有）
                    if '\ufeff' in first_line:
                        first_line = first_line.replace('\ufeff', '')
                    name_pos = first_line.find(func.name)
                    if name_pos >= 0:
                        name_column = name_pos
                    else:
                        name_column = 0

                doc_obj = {
                    "type": "function",
                    "name": func.name,
                    "content": func.language_specific.get("description", ""),
                    "md_content": [],  # 初始为空列表，将由LLM生成
                    "functions": [],
                    "classes": [],
                    "start_line": func.start_line,
                    "end_line": func.end_line,
                    "parent_class": None,
                    "parameters": [p.get("name", "") for p in func.parameters],
                    "code_start_line": func.start_line,
                    "code_end_line": func.end_line,
                    "code_content": code_content,  # 添加代码内容
                    "have_return": func.language_specific.get("has_return_value", False),
                    "name_column": name_column  # 添加名称位置
                }
                doc_objects.append(doc_obj)

        return doc_objects

    def generate_file_structure(self, file_path=None) -> List[Dict]:
        """
        生成文件结构（支持多语言）

        Args:
            file_path: 文件路径（为了兼容父类接口）

        Returns:
            文档对象列表
        """
        content = self.read_file()
        structure = self.parse_file_content(content)

        if structure:
            # 使用多语言解析结果生成文档对象
            return self._generate_doc_objects_from_structure(structure)
        else:
            # 回退到原有方法
            try:
                # 调用父类方法，不需要参数
                return super().generate_file_structure()
            except Exception as e:
                logger.warning(f"传统文件结构生成失败: {e}")
                return []

    def parse_file_content(self, content: str) -> Optional[ProjectStructure]:
        """
        解析文件内容（公开方法）

        Args:
            content: 文件内容

        Returns:
            解析后的项目结构
        """
        return self.parse_file_structure(content)

    def get_capabilities(self) -> Dict[str, Any]:
        """
        获取解析器能力信息

        Returns:
            能力信息字典
        """
        capabilities = {
            "supported_languages": [lang.value for lang in Language],
            "dotnet_enabled": self.dotnet_parser is not None,
            "treesitter_enabled": self.treesitter_wrapper is not None,
            "current_file_language": self._detected_language.value if self._detected_language else None
        }

        if self.dotnet_parser:
            dotnet_caps = self.dotnet_parser.get_capabilities()
            capabilities["dotnet_strategies"] = list(dotnet_caps.keys())
            capabilities["dotnet_parser_availability"] = {
                name: cap.availability for name, cap in dotnet_caps.items()
            }

        return capabilities

    def get_language_statistics(self) -> Dict[str, Any]:
        """
        获取语言统计信息

        Returns:
            统计信息字典
        """
        return {
            "detected_language": self._detected_language.value if self._detected_language else "unknown",
            "supports_multilang": True,
            "available_parsers": {
                "dotnet": self.dotnet_parser is not None,
                "treesitter": self.treesitter_wrapper is not None
            }
        }


# 便捷函数
def create_multilang_file_handler(
    repo_path: str,
    file_path: str,
    config: Optional[MultiLanguageConfig] = None
) -> MultiLanguageFileHandler:
    """创建多语言文件处理器实例"""
    return MultiLanguageFileHandler(repo_path, file_path, config)


def is_multilang_supported_file(file_path: str) -> bool:
    """
    检查文件是否支持多语言解析

    Args:
        file_path: 文件路径

    Returns:
        是否支持多语言
    """
    supported_extensions = [
        '.cs', '.csx',  # C#
        '.py', '.pyi',  # Python
        '.fs', '.fsi', '.fsx',  # F#
        '.vb', '.vbx'  # VB.NET
    ]

    return Path(file_path).suffix.lower() in supported_extensions