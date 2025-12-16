"""
文档生成提示模块 - 支持多种编程语言的文档生成提示
"""

from .dotnet_prompts import (
    DotNetCodeType,
    DotNetTerminology,
    DotNetDocumentationTemplates,
    DotNetPromptGenerator,
    create_dotnet_prompt_generator,
    generate_dotnet_doc_prompt
)

__all__ = [
    "DotNetCodeType",
    "DotNetTerminology",
    "DotNetDocumentationTemplates",
    "DotNetPromptGenerator",
    "create_dotnet_prompt_generator",
    "generate_dotnet_doc_prompt"
]