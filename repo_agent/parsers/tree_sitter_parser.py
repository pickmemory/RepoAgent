"""
Tree-sitter 解析器包装器 - 提供轻量级的代码解析能力
"""

import os
from pathlib import Path
from typing import Dict, List, Optional, Any, Union, Tuple
import logging

try:
    import tree_sitter
    TREE_SITTER_AVAILABLE = True
except ImportError:
    TREE_SITTER_AVAILABLE = False
    tree_sitter = None

from repo_agent.language import (
    Language, Function, Class, Import, ProjectStructure,
    LanguageMetadata, get_language_metadata
)
from repo_agent.log import logger

logger = logging.getLogger(__name__)


class TreeSitterWrapper:
    """Tree-sitter 解析器包装器"""

    def __init__(self):
        """初始化 Tree-sitter 包装器"""
        self._parsers = {}  # 缓存解析器实例
        self._languages = {}  # 缓存语言实例

        if not TREE_SITTER_AVAILABLE:
            logger.warning("Tree-sitter not available. Some features will be disabled.")
            return

        # 尝试加载语言
        self._try_load_languages()

    def _try_load_languages(self):
        """尝试加载支持的语言"""
        # 首先尝试使用内置的语言
        self._load_builtin_languages()

        # 如果内置语言不够，可以尝试从 tree_sitter_languages 加载
        # 但目前这个包的 API 有兼容性问题，暂时跳过

    def _load_builtin_languages(self):
        """加载内置的语言支持"""
        # Tree-sitter 可能有一些内置的语言
        # 这里我们创建一个基础的 Python 解析器作为示例

        # 目前先跳过，因为需要编译的语言库
        logger.info("Tree-sitter loaded, but language parsers need to be compiled")

    def is_available(self) -> bool:
        """检查 Tree-sitter 是否可用"""
        return TREE_SITTER_AVAILABLE

    def is_language_supported(self, language: Language) -> bool:
        """检查是否支持指定语言"""
        return language in self._parsers

    def parse_file(self, file_path: Path, language: Language) -> Optional[ProjectStructure]:
        """
        解析文件并返回项目结构

        Args:
            file_path: 文件路径
            language: 编程语言

        Returns:
            解析后的项目结构，如果解析失败则返回 None
        """
        # 目前返回一个基本的结构
        # 后续可以实现真正的解析

        try:
            # 读取文件内容
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                source_code = f.read()

            # 获取语言元数据
            metadata = get_language_metadata(language)

            # 创建一个基本的项目结构（占位符实现）
            structure = ProjectStructure(
                language=language,
                functions=[],
                classes=[],
                imports=[],
                namespaces=[],
                language_metadata=metadata
            )

            logger.info(f"Parsed {file_path} with basic structure (Tree-sitter not fully implemented yet)")

            return structure

        except Exception as e:
            logger.error(f"Failed to parse {file_path}: {e}")
            return None

    def get_supported_languages(self) -> List[Language]:
        """获取支持的语言列表"""
        return list(self._parsers.keys())

    def clear_cache(self):
        """清除缓存"""
        self._parsers.clear()
        self._languages.clear()
        self._try_load_languages()


# 全局实例
_tree_sitter_wrapper = None


def get_tree_sitter_wrapper() -> TreeSitterWrapper:
    """获取 Tree-sitter 包装器单例"""
    global _tree_sitter_wrapper
    if _tree_sitter_wrapper is None:
        _tree_sitter_wrapper = TreeSitterWrapper()
    return _tree_sitter_wrapper


def is_tree_sitter_available() -> bool:
    """检查 Tree-sitter 是否可用"""
    return TREE_SITTER_AVAILABLE