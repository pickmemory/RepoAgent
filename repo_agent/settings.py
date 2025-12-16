from enum import StrEnum
from typing import Optional, List

from iso639 import Language, LanguageNotFoundError
from pydantic import (
    DirectoryPath,
    Field,
    HttpUrl,
    PositiveFloat,
    PositiveInt,
    SecretStr,
    field_validator,
)
from pydantic_settings import BaseSettings
from pathlib import Path

# Import our language module
from repo_agent.language import Language as CodeLanguage


class LogLevel(StrEnum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class LanguageSettings(BaseSettings):
    """多语言支持的配置设置"""
    enabled_languages: List[CodeLanguage] = Field(
        default=[CodeLanguage.PYTHON, CodeLanguage.CSHARP],
        description="启用的编程语言列表"
    )
    auto_detect_languages: bool = Field(
        default=True,
        description="是否自动检测项目中的编程语言"
    )
    prefer_roslyn_for_dotnet: bool = Field(
        default=False,
        description="对于 .NET 语言是否优先使用 Roslyn 分析器"
    )
    tree_sitter_fallback: bool = Field(
        default=True,
        description="当 Roslyn 不可用时是否回退到 Tree-sitter"
    )
    dotnet_framework_version: Optional[str] = Field(
        default=None,
        description="目标 .NET 框架版本（如 'net6.0', 'net8.0'）"
    )

    @field_validator("enabled_languages", mode="before")
    @classmethod
    def parse_enabled_languages(cls, v):
        """解析启用的语言列表，支持字符串输入"""
        if isinstance(v, str):
            # 如果是逗号分隔的字符串，转换为列表
            languages = []
            for lang_str in v.split(","):
                lang_str = lang_str.strip().lower()
                for code_lang in CodeLanguage:
                    if code_lang.value == lang_str:
                        languages.append(code_lang)
                        break
            return languages
        return v

    @field_validator("dotnet_framework_version")
    @classmethod
    def validate_dotnet_version(cls, v):
        """验证 .NET 框架版本格式"""
        if v is not None:
            valid_prefixes = ["net", "netstandard", "netcoreapp"]
            if not any(v.startswith(prefix) for prefix in valid_prefixes):
                raise ValueError(
                    f"Invalid .NET framework version: {v}. "
                    f"Should start with one of: {', '.join(valid_prefixes)}"
                )
        return v


class ProjectSettings(BaseSettings):
    target_repo: DirectoryPath = ""  # type: ignore
    hierarchy_name: str = ".project_doc_record"
    markdown_docs_name: str = "markdown_docs"
    ignore_list: list[str] = []
    language: str = "English"  # 文档输出语言，不是编程语言
    max_thread_count: PositiveInt = 4
    log_level: LogLevel = LogLevel.INFO
    language_settings: LanguageSettings = Field(
        default_factory=LanguageSettings,
        description="编程语言相关设置"
    )

    @field_validator("language")
    @classmethod
    def validate_language_code(cls, v: str) -> str:
        try:
            language_name = Language.match(v).name
            return language_name  # Returning the resolved language name
        except LanguageNotFoundError:
            raise ValueError(
                "Invalid language input. Please enter a valid ISO 639 code or language name."
            )

    @field_validator("log_level", mode="before")
    @classmethod
    def set_log_level(cls, v: str) -> LogLevel:
        if isinstance(v, str):
            v = v.upper()  # Convert input to uppercase
        if (
            v in LogLevel._value2member_map_
        ):  # Check if the converted value is in enum members
            return LogLevel(v)
        raise ValueError(f"Invalid log level: {v}")


class ChatCompletionSettings(BaseSettings):
    model: str = "gpt-4o-mini"  # NOTE: No model restrictions for user flexibility, but it's recommended to use models with a larger context window.
    temperature: PositiveFloat = 0.2
    request_timeout: PositiveInt = 60
    openai_base_url: str = "http://pickmemory.cn:8084/v1"
    openai_api_key: SecretStr = Field(..., exclude=True)

    @field_validator("openai_base_url", mode="before")
    @classmethod
    def convert_base_url_to_str(cls, openai_base_url: HttpUrl) -> str:
        return str(openai_base_url)


class Setting(BaseSettings):
    project: ProjectSettings = {}  # type: ignore
    chat_completion: ChatCompletionSettings = {}  # type: ignore


class SettingsManager:
    _setting_instance: Optional[Setting] = (
        None  # Private class attribute, initially None
    )

    @classmethod
    def get_setting(cls):
        if cls._setting_instance is None:
            cls._setting_instance = Setting()
        return cls._setting_instance

    @classmethod
    def initialize_with_params(
        cls,
        target_repo: Path,
        markdown_docs_name: str,
        hierarchy_name: str,
        ignore_list: list[str],
        language: str,
        max_thread_count: int,
        log_level: str,
        model: str,
        temperature: float,
        request_timeout: int,
        openai_base_url: str,
        language_settings: Optional[LanguageSettings] = None,
    ):
        """初始化设置（保持向后兼容）"""
        project_settings = ProjectSettings(
            target_repo=target_repo,
            hierarchy_name=hierarchy_name,
            markdown_docs_name=markdown_docs_name,
            ignore_list=ignore_list,
            language=language,
            max_thread_count=max_thread_count,
            log_level=LogLevel(log_level),
            language_settings=language_settings or LanguageSettings(),
        )

        chat_completion_settings = ChatCompletionSettings(
            model=model,
            temperature=temperature,
            request_timeout=request_timeout,
            openai_base_url=openai_base_url,
        )

        cls._setting_instance = Setting(
            project=project_settings,
            chat_completion=chat_completion_settings,
        )

    @classmethod
    def initialize_with_language_support(
        cls,
        target_repo: Path,
        markdown_docs_name: str,
        hierarchy_name: str,
        ignore_list: list[str],
        language: str,
        max_thread_count: int,
        log_level: str,
        model: str,
        temperature: float,
        request_timeout: int,
        openai_base_url: str,
        enabled_languages: Optional[List[CodeLanguage]] = None,
        auto_detect_languages: bool = True,
        prefer_roslyn_for_dotnet: bool = False,
        tree_sitter_fallback: bool = True,
        dotnet_framework_version: Optional[str] = None,
    ):
        """初始化设置，支持多语言配置"""
        language_settings = LanguageSettings(
            enabled_languages=enabled_languages or [CodeLanguage.PYTHON, CodeLanguage.CSHARP],
            auto_detect_languages=auto_detect_languages,
            prefer_roslyn_for_dotnet=prefer_roslyn_for_dotnet,
            tree_sitter_fallback=tree_sitter_fallback,
            dotnet_framework_version=dotnet_framework_version,
        )

        return cls.initialize_with_params(
            target_repo=target_repo,
            markdown_docs_name=markdown_docs_name,
            hierarchy_name=hierarchy_name,
            ignore_list=ignore_list,
            language=language,
            max_thread_count=max_thread_count,
            log_level=log_level,
            model=model,
            temperature=temperature,
            request_timeout=request_timeout,
            openai_base_url=openai_base_url,
            language_settings=language_settings,
        )


if __name__ == "__main__":
    setting = SettingsManager.get_setting()
    print(setting.model_dump())
