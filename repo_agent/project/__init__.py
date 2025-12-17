"""
.NET 项目模块 - 用于解析和理解 .NET 项目结构
"""

from .dotnet_project import DotNetProjectParser, DotNetProject, ProjectReference

__all__ = [
    'DotNetProjectParser',
    'DotNetProject',
    'ProjectReference'
]