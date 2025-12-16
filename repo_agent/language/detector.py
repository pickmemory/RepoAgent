"""
语言检测器 - 自动检测项目中的编程语言
"""

import os
from pathlib import Path
from typing import Dict, List, Set, Optional
import fnmatch

from . import Language, LanguageMetadata, get_language_metadata
from repo_agent.utils.gitignore_checker import GitignoreChecker
from repo_agent.log import logger


class LanguageDetector:
    """语言检测器，用于自动识别项目中的编程语言"""

    def __init__(self, repo_path: Path, respect_gitignore: bool = True):
        """
        初始化语言检测器

        Args:
            repo_path: 仓库根路径
            respect_gitignore: 是否遵守 .gitignore 规则
        """
        self.repo_path = Path(repo_path)
        self.respect_gitignore = respect_gitignore
        self._gitignore_checker = None

        if self.respect_gitignore:
            gitignore_path = self.repo_path / ".gitignore"
            if gitignore_path.exists():
                self._gitignore_checker = GitignoreChecker(
                    directory=self.repo_path,
                    gitignore_path=gitignore_path
                )

    def detect_languages(self) -> Set[Language]:
        """
        检测仓库中存在的编程语言

        Returns:
            检测到的语言集合
        """
        detected_languages = set()

        # 扫描所有文件
        for file_path in self._get_all_files():
            language = self._detect_language_for_file(file_path)
            if language:
                detected_languages.add(language)
                logger.debug(f"检测到文件 {file_path} 的语言: {language.value}")

        # 扫描项目文件
        project_languages = self._detect_from_project_files()
        detected_languages.update(project_languages)

        logger.info(f"检测到的语言: {[lang.value for lang in detected_languages]}")
        return detected_languages

    def get_language_for_file(self, file_path: Path) -> Optional[Language]:
        """
        获取指定文件的编程语言

        Args:
            file_path: 文件路径

        Returns:
            检测到的语言，如果无法识别则返回 None
        """
        relative_path = file_path.relative_to(self.repo_path) if file_path.is_absolute() else file_path
        return self._detect_language_for_file(relative_path)

    def is_supported_file(self, file_path: Path) -> bool:
        """
        判断文件是否被支持的语言

        Args:
            file_path: 文件路径

        Returns:
            如果文件被支持则返回 True
        """
        return self.get_language_for_file(file_path) is not None

    def get_files_by_language(self, language: Language) -> List[Path]:
        """
        获取指定语言的所有文件

        Args:
            language: 目标语言

        Returns:
            该语言的所有文件路径列表
        """
        files = []
        metadata = get_language_metadata(language)

        for file_path in self._get_all_files():
            if self._is_file_of_language(file_path, language, metadata):
                files.append(file_path)

        return files

    def _get_all_files(self) -> List[Path]:
        """获取仓库中的所有文件（可能受 .gitignore 影响）"""
        files = []

        if self._gitignore_checker:
            # 使用 GitignoreChecker
            for file_path in self._gitignore_checker.check_files_and_folders():
                files.append(Path(file_path))
        else:
            # 遍历所有文件
            for root, dirs, filenames in os.walk(self.repo_path):
                # 跳过隐藏目录
                dirs[:] = [d for d in dirs if not d.startswith('.')]

                for filename in filenames:
                    # 跳过隐藏文件
                    if filename.startswith('.'):
                        continue

                    file_path = Path(root) / filename
                    relative_path = file_path.relative_to(self.repo_path)
                    files.append(relative_path)

        return files

    def _detect_language_for_file(self, file_path: Path) -> Optional[Language]:
        """
        检测单个文件的编程语言

        Args:
            file_path: 文件路径（相对于仓库根目录）

        Returns:
            检测到的语言
        """
        # 首先检查是否是项目文件
        project_language = self._is_project_file(file_path)
        if project_language:
            return project_language

        # 然后通过文件扩展名检查
        return self._detect_by_extension(file_path)

    def _is_project_file(self, file_path: Path) -> Optional[Language]:
        """
        检查文件是否是特定语言的项目文件

        Args:
            file_path: 文件路径

        Returns:
            对应的语言，如果不是项目文件则返回 None
        """
        filename = file_path.name.lower()
        suffix = file_path.suffix.lower()

        for language in Language:
            metadata = get_language_metadata(language)

            # 检查文件名
            if filename in metadata.project_files:
                return language

            # 检查文件扩展名
            if suffix in metadata.project_files:
                return language

        return None

    def _detect_by_extension(self, file_path: Path) -> Optional[Language]:
        """
        通过文件扩展名检测语言

        Args:
            file_path: 文件路径

        Returns:
            检测到的语言
        """
        suffix = file_path.suffix.lower()

        for language in Language:
            metadata = get_language_metadata(language)
            if suffix in metadata.file_extensions:
                return language

        return None

    def _is_file_of_language(self, file_path: Path, language: Language, metadata: LanguageMetadata) -> bool:
        """
        判断文件是否属于指定语言

        Args:
            file_path: 文件路径
            language: 目标语言
            metadata: 语言元数据

        Returns:
            如果文件属于该语言则返回 True
        """
        # 检查文件扩展名
        if file_path.suffix.lower() in metadata.file_extensions:
            return True

        # 检查项目文件
        filename = file_path.name.lower()
        suffix = file_path.suffix.lower()
        if filename in metadata.project_files or suffix in metadata.project_files:
            return True

        return False

    def _detect_from_project_files(self) -> Set[Language]:
        """
        通过项目文件检测语言

        Returns:
            检测到的语言集合
        """
        languages = set()

        # 查找特定于语言的项目文件
        for file_path in self._get_all_files():
            language = self._is_project_file(file_path)
            if language:
                languages.add(language)
                logger.debug(f"通过项目文件检测到语言: {language.value} (文件: {file_path})")

        return languages

    def get_language_statistics(self) -> Dict[Language, int]:
        """
        获取各种语言的文件数量统计

        Returns:
            语言到文件数量的映射
        """
        stats = {}

        for file_path in self._get_all_files():
            language = self._detect_language_for_file(file_path)
            if language:
                stats[language] = stats.get(language, 0) + 1

        return stats

    def suggest_enabled_languages(self, min_files: int = 5) -> List[Language]:
        """
        建议应该启用的语言（基于文件数量）

        Args:
            min_files: 建议启用该语言的最少文件数量

        Returns:
            建议的语言列表，按文件数量降序排列
        """
        stats = self.get_language_statistics()

        # 过滤出文件数量达到阈值的语言
        suggested = [
            (lang, count) for lang, count in stats.items()
            if count >= min_files
        ]

        # 按文件数量降序排列
        suggested.sort(key=lambda x: x[1], reverse=True)

        return [lang for lang, _ in suggested]


def detect_project_languages(repo_path: Path, respect_gitignore: bool = True) -> Set[Language]:
    """
    便捷函数：检测项目的编程语言

    Args:
        repo_path: 仓库路径
        respect_gitignore: 是否遵守 .gitignore

    Returns:
        检测到的语言集合
    """
    detector = LanguageDetector(repo_path, respect_gitignore)
    return detector.detect_languages()


def get_project_language_files(repo_path: Path, language: Language, respect_gitignore: bool = True) -> List[Path]:
    """
    便捷函数：获取项目中指定语言的所有文件

    Args:
        repo_path: 仓库路径
        language: 目标语言
        respect_gitignore: 是否遵守 .gitignore

    Returns:
        该语言的文件列表
    """
    detector = LanguageDetector(repo_path, respect_gitignore)
    return detector.get_files_by_language(language)