"""
.NET 混合解析器 - 结合 Tree-sitter 和 Roslyn 的优势
"""

import os
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from enum import Enum

from repo_agent.language import (
    Language, Function, Class, Import, ProjectStructure,
    LanguageMetadata, get_language_metadata
)
from repo_agent.log import logger
from repo_agent.parsers.dotnet_extractor import DotNetStructureExtractor
from repo_agent.parsers.tree_sitter_parser import get_tree_sitter_wrapper, is_tree_sitter_available


class AnalysisStrategy(Enum):
    """分析策略枚举"""
    AUTO = "auto"          # 自动选择
    TREESITTER = "tree-sitter"  # 强制使用 Tree-sitter
    ROSLYN = "roslyn"      # 强制使用 Roslyn
    HYBRID = "hybrid"      # 混合模式（Tree-sitter 初步分析，Roslyn 深度分析）


@dataclass
class ParserCapabilities:
    """解析器能力描述"""
    name: str
    speed: str  # 快速、中等、慢速
    accuracy: str  # 基础、良好、优秀
    features: List[str]  # 支持的特性列表
    availability: bool  # 是否可用
    dependencies: List[str]  # 依赖项


class DotNetParser:
    """.NET 混合解析器 - 根据文件特征智能选择最优解析策略"""

    def __init__(
        self,
        strategy: AnalysisStrategy = AnalysisStrategy.AUTO,
        prefer_roslyn_for_large_files: bool = False,
        treesitter_fallback: bool = True,
        enable_caching: bool = True
    ):
        """
        初始化 .NET 解析器

        Args:
            strategy: 默认分析策略
            prefer_roslyn_for_large_files: 大文件是否优先使用 Roslyn
            treesitter_fallback: Roslyn 不可用时是否回退到 Tree-sitter
            enable_caching: 是否启用结果缓存
        """
        self.strategy = strategy
        self.prefer_roslyn_for_large_files = prefer_roslyn_for_large_files
        self.treesitter_fallback = treesitter_fallback
        self.enable_caching = enable_caching

        # 初始化解析器
        self._extractor = DotNetStructureExtractor()
        self._treesitter_wrapper = None
        self._roslyn_wrapper = None

        # 缓存
        self._parse_cache = {} if enable_caching else None

        # 检查解析器可用性
        self._initialize_parsers()

        # 文件大小阈值（字节）
        self.roslyn_threshold = 50 * 1024  # 50KB
        self.treesitter_threshold = 500 * 1024  # 500KB

    def _initialize_parsers(self):
        """初始化并检查解析器可用性"""
        # Tree-sitter 解析器
        if is_tree_sitter_available():
            try:
                self._treesitter_wrapper = get_tree_sitter_wrapper()
                logger.debug("Tree-sitter 解析器已初始化")
            except Exception as e:
                logger.warning(f"Tree-sitter 解析器初始化失败: {e}")
        else:
            logger.debug("Tree-sitter 不可用")

        # Roslyn 解析器
        try:
            from repo_agent.parsers.roslyn_wrapper import RoslynWrapper
            self._roslyn_wrapper = RoslynWrapper()
            logger.debug("Roslyn 解析器已初始化")
        except Exception as e:
            logger.debug(f"Roslyn 解析器不可用: {e}")

    def get_capabilities(self) -> Dict[str, ParserCapabilities]:
        """获取解析器能力信息"""
        return {
            "tree-sitter": ParserCapabilities(
                name="Tree-sitter",
                speed="快速",
                accuracy="基础",
                features=[
                    "语法结构提取",
                    "函数和类识别",
                    "命名空间解析",
                    "轻量级",
                    "跨平台"
                ],
                availability=self._treesitter_wrapper is not None,
                dependencies=["tree-sitter", "tree-sitter-c-sharp"]
            ),
            "roslyn": ParserCapabilities(
                name="Roslyn",
                speed="慢速",
                accuracy="优秀",
                features=[
                    "完整语义分析",
                    "XML 文档注释",
                    "编译器级准确性",
                    ".NET 特性检测",
                    "依赖关系分析",
                    "LINQ 查询识别"
                ],
                availability=self._roslyn_wrapper is not None,
                dependencies=[".NET SDK", "RoslynAnalyzer.exe"]
            )
        }

    def parse_file(
        self,
        file_path: Union[str, Path],
        strategy: Optional[AnalysisStrategy] = None
    ) -> ProjectStructure:
        """
        解析 .NET 文件

        Args:
            file_path: 文件路径
            strategy: 分析策略，None 表示使用默认策略

        Returns:
            项目结构对象
        """
        file_path = Path(file_path).resolve()

        # 检查缓存
        if self._parse_cache and str(file_path) in self._parse_cache:
            logger.debug(f"从缓存返回结果: {file_path}")
            return self._parse_cache[str(file_path)]

        strategy = strategy or self.strategy

        # 选择解析策略
        selected_strategy = self._select_strategy(file_path, strategy)
        logger.debug(f"文件 {file_path.name} 使用策略: {selected_strategy.value}")

        # 执行解析
        if selected_strategy == AnalysisStrategy.TREESITTER:
            result = self._parse_with_treesitter(file_path)
        elif selected_strategy == AnalysisStrategy.ROSLYN:
            result = self._parse_with_roslyn(file_path)
        elif selected_strategy == AnalysisStrategy.HYBRID:
            result = self._parse_with_hybrid(file_path)
        else:
            # AUTO 策略
            result = self._parse_auto(file_path)

        # 缓存结果
        if self._parse_cache:
            self._parse_cache[str(file_path)] = result

        return result

    def _select_strategy(
        self,
        file_path: Path,
        strategy: AnalysisStrategy
    ) -> AnalysisStrategy:
        """选择实际的解析策略"""
        if strategy != AnalysisStrategy.AUTO:
            # 检查请求的策略是否可用
            if strategy == AnalysisStrategy.TREESITTER and not self._treesitter_wrapper:
                if self.treesitter_fallback and self._roslyn_wrapper:
                    logger.debug("Tree-sitter 不可用，回退到 Roslyn")
                    return AnalysisStrategy.ROSLYN
                raise RuntimeError("Tree-sitter 不可用且未启用回退")
            elif strategy == AnalysisStrategy.ROSLYN and not self._roslyn_wrapper:
                if self.treesitter_fallback and self._treesitter_wrapper:
                    logger.debug("Roslyn 不可用，回退到 Tree-sitter")
                    return AnalysisStrategy.TREESITTER
                raise RuntimeError("Roslyn 不可用且未启用回退")
            elif strategy == AnalysisStrategy.HYBRID:
                if not (self._treesitter_wrapper and self._roslyn_wrapper):
                    logger.debug("混合模式不可用，使用可用解析器")
                    return AnalysisStrategy.ROSLYN if self._roslyn_wrapper else AnalysisStrategy.TREESITTER
            return strategy

        # AUTO 策略的智能选择逻辑将在 _parse_auto 中处理
        return strategy

    def _parse_auto(self, file_path: Path) -> ProjectStructure:
        """自动选择最优解析策略"""
        file_size = file_path.stat().st_size
        file_ext = file_path.suffix.lower()

        # 基于文件大小的策略选择
        if file_size < self.roslyn_threshold and self._roslyn_wrapper:
            # 小文件优先使用 Roslyn 获得更准确的结果
            logger.debug(f"小文件 ({file_size} 字节)，使用 Roslyn")
            return self._parse_with_roslyn(file_path)
        elif file_size > self.treesitter_threshold and self._treesitter_wrapper:
            # 大文件优先使用 Tree-sitter 避免性能问题
            logger.debug(f"大文件 ({file_size} 字节)，使用 Tree-sitter")
            return self._parse_with_treesitter(file_path)
        elif self.prefer_roslyn_for_large_files and self._roslyn_wrapper:
            # 配置偏好 Roslyn
            logger.debug("配置偏好 Roslyn，使用 Roslyn")
            return self._parse_with_roslyn(file_path)
        elif self._treesitter_wrapper:
            # 默认使用 Tree-sitter
            logger.debug("默认使用 Tree-sitter")
            return self._parse_with_treesitter(file_path)
        elif self._roslyn_wrapper:
            # Tree-sitter 不可用时使用 Roslyn
            logger.debug("Tree-sitter 不可用，使用 Roslyn")
            return self._parse_with_roslyn(file_path)
        else:
            # 都不可用时使用内置提取器
            logger.debug("使用内置提取器")
            return self._parse_with_extractor(file_path)

    def _parse_with_treesitter(self, file_path: Path) -> ProjectStructure:
        """使用 Tree-sitter 解析"""
        if not self._treesitter_wrapper:
            raise RuntimeError("Tree-sitter 解析器不可用")

        try:
            structure = self._treesitter_wrapper.parse_file(file_path, Language.CSHARP)
            logger.debug(f"Tree-sitter 解析完成: {structure}")
            return structure
        except Exception as e:
            logger.warning(f"Tree-sitter 解析失败: {e}")
            if self.treesitter_fallback:
                if self._roslyn_wrapper:
                    logger.debug("回退到 Roslyn 解析")
                    return self._parse_with_roslyn(file_path)
                else:
                    logger.debug("回退到内置提取器")
                    return self._parse_with_extractor(file_path)
            raise

    def _parse_with_roslyn(self, file_path: Path) -> ProjectStructure:
        """使用 Roslyn 解析"""
        if not self._roslyn_wrapper:
            raise RuntimeError("Roslyn 解析器不可用")

        try:
            # 使用文件输出模式以避免编码问题
            import tempfile
            import json

            with tempfile.NamedTemporaryFile(mode='w+', suffix='.json', delete=False) as tmp_file:
                tmp_path = Path(tmp_file.name)

            try:
                # 调用 Roslyn 分析器
                output_path = self._roslyn_wrapper.analyze_file_to_json(file_path, tmp_path)

                # 读取结果
                with open(output_path, 'r', encoding='utf-8') as f:
                    roslyn_result = json.load(f)

                # 转换为 ProjectStructure
                structure = self._convert_roslyn_result(roslyn_result, file_path)

                logger.debug(f"Roslyn 解析完成: {len(structure.classes)} 个类")
                return structure

            finally:
                # 清理临时文件
                if tmp_path.exists():
                    tmp_path.unlink()

        except Exception as e:
            logger.warning(f"Roslyn 解析失败: {e}")
            if self.treesitter_fallback:
                if self._treesitter_wrapper:
                    logger.debug("回退到 Tree-sitter 解析")
                    return self._parse_with_treesitter(file_path)
                else:
                    logger.debug("回退到内置提取器")
                    return self._parse_with_extractor(file_path)
            raise

    def _parse_with_hybrid(self, file_path: Path) -> ProjectStructure:
        """混合解析模式 - Tree-sitter 快速分析 + Roslyn 深度分析"""
        if not (self._treesitter_wrapper and self._roslyn_wrapper):
            logger.debug("混合模式不可用，使用 Roslyn")
            return self._parse_with_roslyn(file_path)

        try:
            # 第一阶段：Tree-sitter 快速分析
            logger.debug("混合模式 - 第一阶段：Tree-sitter 分析")
            ts_structure = self._parse_with_treesitter(file_path)

            # 第二阶段：Roslyn 深度分析（可选，用于复杂文件）
            file_size = file_path.stat().st_size
            if file_size < self.treesitter_threshold:  # 只对小文件进行深度分析
                logger.debug("混合模式 - 第二阶段：Roslyn 深度分析")
                roslyn_structure = self._parse_with_roslyn(file_path)

                # 合并结果，优先使用 Roslyn 的准确数据
                structure = self._merge_structures(roslyn_structure, ts_structure)
            else:
                # 大文件只使用 Tree-sitter 结果
                structure = ts_structure

            logger.debug(f"混合解析完成")
            return structure

        except Exception as e:
            logger.warning(f"混合解析失败: {e}")
            # 回退到单一解析器
            return self._parse_with_roslyn(file_path)

    def _parse_with_extractor(self, file_path: Path) -> ProjectStructure:
        """使用内置正则表达式提取器"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                source_code = f.read()

            structure = self._extractor.extract_from_source(source_code, file_path)
            logger.debug(f"内置提取器解析完成: {len(structure.classes)} 个类")
            return structure

        except Exception as e:
            logger.error(f"所有解析器都失败: {e}")
            raise RuntimeError(f"无法解析文件 {file_path}: {e}")

    def _convert_roslyn_result(self, roslyn_result: Dict[str, Any], file_path: Path) -> ProjectStructure:
        """将 Roslyn 分析结果转换为 ProjectStructure"""
        # 获取语言元数据
        metadata = get_language_metadata(Language.CSHARP)

        # 转换函数/方法
        functions = []
        for cls in roslyn_result.get('classes', []):
            for method in cls.get('methods', []):
                func = Function(
                    name=method['name'],
                    parameters=[
                        {
                            'name': p['name'],
                            'type': p['type'],
                            'default': p.get('hasDefaultValue', False)
                        }
                        for p in method.get('parameters', [])
                    ],
                    return_type=method['returnType'],
                    is_async=method.get('isAsync', False),
                    access_level=method.get('modifiers', ['public'])[0] if method.get('modifiers') else 'public',
                    language_specific={
                        'type': 'method',
                        'full_signature': f"{method['returnType']} {method['name']}({', '.join(p['type'] + ' ' + p['name'] for p in method.get('parameters', []))})"
                    }
                )
                functions.append(func)

        # 转换类
        classes = []
        for cls_data in roslyn_result.get('classes', []):
            cls = Class(
                name=cls_data['name'],
                base_classes=cls_data.get('interfaces', []),
                methods=[],
                properties=[],
                is_interface=cls_data['kind'] == 'InterfaceDeclaration',
                is_abstract='abstract' in cls_data.get('modifiers', []),
                access_level=cls_data.get('modifiers', ['public'])[0] if cls_data.get('modifiers') else 'public',
                language_specific={
                    'kind': cls_data['kind'],
                    'documentation': cls_data.get('documentation'),
                    'properties': cls_data.get('properties', []),
                    'fields': cls_data.get('fields', []),
                    'events': cls_data.get('events', [])
                }
            )
            classes.append(cls)

        # 转换导入
        imports = []
        for imp in roslyn_result.get('imports', []):
            import_obj = Import(
                module=imp['name'],
                alias=imp.get('alias'),
                is_wildcard=False,
                language_specific={
                    'isStatic': imp.get('isStatic', False)
                }
            )
            imports.append(import_obj)

        return ProjectStructure(
            language=Language.CSHARP,
            functions=functions,
            classes=classes,
            imports=imports,
            namespaces=roslyn_result.get('namespaces', []),
            language_metadata=metadata
        )

    def _merge_structures(
        self,
        primary: ProjectStructure,
        secondary: ProjectStructure
    ) -> ProjectStructure:
        """合并两个解析结果，优先使用 primary 的数据"""
        # 使用 primary 的基本结构
        merged = ProjectStructure(
            language=primary.language,
            functions=primary.functions,
            classes=primary.classes,
            imports=primary.imports,
            namespaces=primary.namespaces,
            language_metadata=primary.language_metadata
        )

        # 补充 secondary 中有但 primary 中没有的数据
        # （这里可以根据需要实现更复杂的合并逻辑）

        return merged

    def clear_cache(self):
        """清除解析缓存"""
        if self._parse_cache:
            self._parse_cache.clear()
            logger.debug("解析缓存已清除")

    def get_cache_info(self) -> Dict[str, Any]:
        """获取缓存信息"""
        if not self._parse_cache:
            return {"enabled": False, "size": 0}

        return {
            "enabled": True,
            "size": len(self._parse_cache),
            "files": list(self._parse_cache.keys())
        }

    def __enter__(self):
        """支持上下文管理器"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """支持上下文管理器"""
        # 清理资源
        if self._roslyn_wrapper:
            self._roslyn_wrapper.__exit__(exc_type, exc_val, exc_tb)
        self.clear_cache()