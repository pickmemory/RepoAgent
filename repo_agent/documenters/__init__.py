"""
文档生成器模块 - 支持多种编程语言的文档生成
"""

from .dotnet_documenter import (
    DotNetDocConfig,
    DotNetDocumentGenerator,
    create_dotnet_documenter
)

__all__ = [
    "DotNetDocConfig",
    "DotNetDocumentGenerator",
    "create_dotnet_documenter"
]