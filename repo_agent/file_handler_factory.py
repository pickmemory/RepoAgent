"""
文件处理器工厂 - 根据文件类型自动选择合适的处理器
"""

from pathlib import Path
from typing import Optional

from repo_agent.file_handler import FileHandler
from repo_agent.file_handler_extended import (
    MultiLanguageFileHandler,
    MultiLanguageConfig,
    is_multilang_supported_file
)
from repo_agent.log import logger


def create_file_handler(
    repo_path: str,
    file_path: str,
    config: Optional[MultiLanguageConfig] = None
) -> FileHandler:
    """
    根据文件类型创建合适的文件处理器

    Args:
        repo_path: 仓库路径
        file_path: 文件路径（可以为 None）
        config: 多语言配置

    Returns:
        合适的文件处理器实例
    """
    # 如果文件路径为 None，使用传统的 FileHandler
    if file_path is None:
        logger.debug("文件路径为 None，使用传统 FileHandler")
        return FileHandler(repo_path, file_path)

    # 检查是否支持多语言解析
    if is_multilang_supported_file(file_path):
        logger.debug(f"文件 {file_path} 支持多语言，使用 MultiLanguageFileHandler")
        return MultiLanguageFileHandler(repo_path, file_path, config)
    else:
        logger.debug(f"文件 {file_path} 使用传统 FileHandler")
        return FileHandler(repo_path, file_path)


def is_dotnet_file(file_path: str) -> bool:
    """
    检查是否为 .NET 文件

    Args:
        file_path: 文件路径

    Returns:
        是否为 .NET 文件
    """
    dotnet_extensions = ['.cs', '.csx', '.fs', '.fsi', '.fsx', '.vb', '.vbx']
    return Path(file_path).suffix.lower() in dotnet_extensions


def is_python_file(file_path: str) -> bool:
    """
    检查是否为 Python 文件

    Args:
        file_path: 文件路径

    Returns:
        是否为 Python 文件
    """
    python_extensions = ['.py', '.pyi']
    return Path(file_path).suffix.lower() in python_extensions


def get_supported_file_extensions() -> list:
    """
    获取所有支持的文件扩展名

    Returns:
        支持的文件扩展名列表
    """
    python_extensions = ['.py', '.pyi']
    dotnet_extensions = ['.cs', '.csx', '.fs', '.fsi', '.fsx', '.vb', '.vbx']

    return python_extensions + dotnet_extensions


def should_process_file(file_path: str) -> bool:
    """
    检查文件是否应该被处理（用于项目扫描）

    Args:
        file_path: 文件路径

    Returns:
        是否应该处理该文件
    """
    return Path(file_path).suffix.lower() in get_supported_file_extensions()