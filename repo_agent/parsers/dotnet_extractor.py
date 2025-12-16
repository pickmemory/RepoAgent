"""
.NET 特定结构提取器 - 从 Tree-sitter AST 提取 .NET 特有概念
"""

import re
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path

from repo_agent.language import (
    Language, Function, Class, Import, ProjectStructure,
    LanguageMetadata, get_language_metadata
)
from repo_agent.log import logger


class DotNetStructureExtractor:
    """.NET 特定结构提取器"""

    def __init__(self):
        """初始化提取器"""
        # C# 关键字和模式
        self.namespace_pattern = re.compile(r'namespace\s+([\w\.]+)')
        self.class_pattern = re.compile(r'(?:public|private|protected|internal)\s+(?:abstract\s+)?(?:sealed\s+)?(?:static\s+)?class\s+(\w+)')
        self.interface_pattern = re.compile(r'(?:public|private|protected|internal)\s+(?:abstract\s+)?(?:static\s+)?interface\s+(\w+)')
        self.struct_pattern = re.compile(r'(?:public|private|protected|internal)\s+(?:abstract\s+)?(?:static\s+)?struct\s+(\w+)')
        self.enum_pattern = re.compile(r'(?:public|private|protected|internal)\s+enum\s+(\w+)')
        self.delegate_pattern = re.compile(r'(?:public|private|protected|internal)\s+delegate\s+[\w\s]+\s+(\w+)\s*\(')

        # 方法模式
        self.method_pattern = re.compile(
            r'(?:public|private|protected|internal|static)\s+(?:abstract\s+)?(?:virtual\s+)?(?:override\s+)?(?:async\s+)?(?:extern\s+)?(?:unsafe\s+)?(?:partial\s+)?'
            r'(?:(?:\w+(?:<[^>]+>)?\??|\s+void)\s+)?'  # 返回类型
            r'(\w+)\s*\(([^)]*)\)\s*(?:\{|;)'  # 方法名和参数
        )

        # 属性模式
        self.property_pattern = re.compile(
            r'(?:public|private|protected|internal)\s+(?:virtual\s+)?(?:override\s+)?(?:static\s+)?'
            r'(\w+(?:<[^>]+>)?\??)\s+(\w+)\s*\{[^}]*\}'  # 类型 属性名
        )

        # 字段模式
        self.field_pattern = re.compile(
            r'(?:public|private|protected|internal)\s+(?:readonly\s+|static\s+|const\s+)?'
            r'(\w+(?:<[^>]+>)?(?:\[\])?)\s+(\w+(?:\[\])?)\s*(?:=\s*[^;]+)?\s*;'  # 类型 名称 赋值
        )

        # using 语句模式
        self.using_pattern = re.compile(r'using\s+(?:static\s+)?([^\s;]+)\s*;')

    def extract_from_source(self, source_code: str, file_path: Path) -> ProjectStructure:
        """
        从源代码提取 .NET 结构

        Args:
            source_code: C# 源代码
            file_path: 文件路径

        Returns:
            提取的项目结构
        """
        logger.debug(f"Extracting .NET structures from {file_path}")

        # 获取语言元数据
        metadata = get_language_metadata(Language.CSHARP)

        # 提取各种结构
        namespaces = self._extract_namespaces(source_code)
        functions = self._extract_functions(source_code, namespaces)
        classes = self._extract_classes(source_code, namespaces)
        imports = self._extract_imports(source_code)

        # 创建项目结构
        structure = ProjectStructure(
            language=Language.CSHARP,
            functions=functions,
            classes=classes,
            imports=imports,
            namespaces=namespaces,
            language_metadata=metadata
        )

        logger.debug(f"Extracted from {file_path}: "
                   f"{len(namespaces)} namespaces, "
                   f"{len(functions)} functions, "
                   f"{len(classes)} classes, "
                   f"{len(imports)} imports")

        return structure

    def _extract_namespaces(self, source_code: str) -> List[str]:
        """提取命名空间"""
        namespaces = []

        # 查找 namespace 声明
        for match in self.namespace_pattern.finditer(source_code):
            namespace = match.group(1)
            if namespace and namespace not in namespaces:
                namespaces.append(namespace)

        # 查找嵌套命名空间（简化处理）
        # 例如：namespace A.B.C
        nested_namespaces = set()
        for ns in namespaces:
            parts = ns.split('.')
            for i in range(1, len(parts)):
                parent = '.'.join(parts[:i])
                nested_namespaces.add(parent)

        namespaces = sorted(namespaces + list(nested_namespaces))

        return namespaces

    def _extract_functions(self, source_code: str, namespaces: List[str]) -> List[Function]:
        """提取方法/函数"""
        functions = []

        # 查找方法声明
        for match in self.method_pattern.finditer(source_code):
            # 解析方法信息
            access_level = self._extract_access_level(match.group(0) or "")
            return_type = "void"  # 简化处理，实际应该从匹配中提取
            method_name = match.group(1).strip()
            parameters_str = match.group(2) or ""
            is_async = "async" in (match.group(0) or "")

            # 解析参数
            parameters = self._parse_parameters(parameters_str)

            # 确定函数类型
            if self._is_constructor(method_name, namespaces):
                func_type = "constructor"
            elif self._is_property_accessor(method_name, parameters_str):
                func_type = "property_accessor"
            else:
                func_type = "method"

            # 创建函数对象
            function = Function(
                name=method_name,
                parameters=parameters,
                return_type=return_type,
                is_async=is_async,
                access_level=access_level,
                language_specific={
                    "type": func_type,
                    "full_signature": match.group(0).strip()
                }
            )

            functions.append(function)

        return functions

    def _extract_classes(self, source_code: str, namespaces: List[str]) -> List[Class]:
        """提取类、接口、结构体等"""
        classes = []

        # 提取类
        for match in self.class_pattern.finditer(source_code):
            class_name = match.group(1)
            access_level = self._extract_access_level(match.group(0))
            is_abstract = "abstract" in (match.group(0) or "")
            is_static = "static" in (match.group(0) or "")
            is_sealed = "sealed" in (match.group(0) or "")

            # 提取基类
            base_classes = self._extract_base_classes(source_code, match.start(), class_name)

            cls = Class(
                name=class_name,
                base_classes=base_classes,
                methods=[],
                properties=[],
                is_interface=False,
                is_abstract=is_abstract,
                access_level=access_level,
                language_specific={
                    "is_static": is_static,
                    "is_sealed": is_sealed
                }
            )
            classes.append(cls)

        # 提取接口
        for match in self.interface_pattern.finditer(source_code):
            interface_name = match.group(1)
            access_level = self._extract_access_level(match.group(0))

            base_interfaces = self._extract_base_classes(source_code, match.start(), interface_name)

            cls = Class(
                name=interface_name,
                base_classes=base_interfaces,
                methods=[],
                properties=[],
                is_interface=True,
                is_abstract=True,
                access_level=access_level
            )
            classes.append(cls)

        # 提取结构体
        for match in self.struct_pattern.finditer(source_code):
            struct_name = match.group(1)
            access_level = self._extract_access_level(match.group(0))

            base_structs = self._extract_base_classes(source_code, match.start(), struct_name)

            cls = Class(
                name=struct_name,
                base_classes=base_structs,
                methods=[],
                properties=[],
                is_interface=False,
                is_abstract=False,
                access_level=access_level,
                language_specific={
                    "is_struct": True
                }
            )
            classes.append(cls)

        # 提取枚举
        for match in self.enum_pattern.finditer(source_code):
            enum_name = match.group(1)
            access_level = self._extract_access_level(match.group(0))

            cls = Class(
                name=enum_name,
                base_classes=[],
                methods=[],
                properties=[],
                is_interface=False,
                is_abstract=False,
                access_level=access_level,
                language_specific={
                    "is_enum": True
                }
            )
            classes.append(cls)

        return classes

    def _extract_imports(self, source_code: str) -> List[Import]:
        """提取 using 语句"""
        imports = []

        for match in self.using_pattern.finditer(source_code):
            import_name = match.group(1).strip()

            # 解析别名（using Alias = Namespace.Type）
            alias = None
            module = import_name

            if '=' in import_name:
                parts = import_name.split('=', 1)
                if len(parts) == 2:
                    alias = parts[0].strip()
                    module = parts[1].strip()

            import_obj = Import(
                module=module,
                name=None,
                alias=alias,
                is_wildcard=False
            )
            imports.append(import_obj)

        return imports

    def _parse_parameters(self, parameters_str: str) -> List[Dict[str, Any]]:
        """解析方法参数"""
        parameters = []

        if not parameters_str.strip():
            return parameters

        # 简化的参数解析
        # 注意：这是一个简化版本，不处理所有 C# 参数语法
        param_parts = parameters_str.split(',')

        for param_part in param_parts:
            param_part = param_part.strip()
            if not param_part:
                continue

            # 解析参数：类型 名称，或仅名称
            parts = param_part.split()
            if len(parts) >= 2:
                param_type = ' '.join(parts[:-1])
                param_name = parts[-1]
            else:
                param_type = "var"  # 默认为 var（C# 3.0+）
                param_name = parts[0] if parts else "param"

            # 处理默认值
            if '=' in param_name:
                param_name, default_value = param_name.split('=', 1)
                param_name = param_name.strip()
                param_default = default_value.strip()
            else:
                param_default = None

            parameters.append({
                "name": param_name,
                "type": param_type,
                "default": param_default
            })

        return parameters

    def _extract_base_classes(self, source_code: str, start_pos: int, class_name: str) -> List[str]:
        """提取基类或接口"""
        base_classes = []

        # 在类声明之后查找 : 或 : where
        # 这是一个简化的实现
        source_after_class = source_code[start_pos:start_pos + 500]  # 查看后面 500 字符

        # 查找冒号后的基类列表
        lines = source_after_class.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith(':') or line.startswith('{'):
                if line.startswith(':'):
                    # 提取基类列表
                    base_part = line[1:].strip()
                    if base_part:
                        # 简单分割（不处理泛型约束）
                        bases = [b.strip() for b in base_part.split(',') if b.strip()]
                        base_classes.extend([b for b in bases if b and b != class_name])
                break
            else:
                break

        return base_classes

    def _extract_access_level(self, text: str) -> str:
        """提取访问级别"""
        if 'public' in text:
            return "public"
        elif 'private' in text:
            return "private"
        elif 'protected' in text:
            return "protected"
        elif 'internal' in text:
            return "internal"
        return "internal"  # 默认

    def _is_constructor(self, method_name: str, namespaces: List[str]) -> bool:
        """判断是否是构造函数"""
        # 如果方法名与类名相同，可能是构造函数
        # 这是一个简化判断，实际实现需要更复杂的上下文分析
        simple_names = [ns.split('.')[-1] for ns in namespaces]
        return method_name in simple_names

    def _is_property_accessor(self, method_name: str, parameters_str: str) -> bool:
        """判断是否是属性访问器（get/set）"""
        return (method_name.startswith(('get_', 'set_')) and not parameters_str.strip())

    def extract_dotnet_specific_features(self, source_code: str) -> Dict[str, Any]:
        """提取 .NET 特有特性"""
        features = {
            "attributes": self._extract_attributes(source_code),
            "events": self._extract_events(source_code),
            "properties": self._extract_properties(source_code),
            "indexers": self._extract_indexers(source_code),
            "generics": self._extract_generics(source_code),
            "linq_queries": self._extract_linq_queries(source_code),
            "async_methods": self._extract_async_methods(source_code)
        }

        return features

    def _extract_attributes(self, source_code: str) -> List[Dict[str, Any]]:
        """提取特性（Attributes）"""
        attributes = []
        # 简化实现：查找 [AttributeName(...)] 模式
        attr_pattern = re.compile(r'\[([^\]]+)\]')

        for match in attr_pattern.finditer(source_code):
            attr_content = match.group(1)
            attributes.append({
                "content": attr_content,
                "raw": match.group(0)
            })

        return attributes

    def _extract_events(self, source_code: str) -> List[Dict[str, Any]]:
        """提取事件（Events）"""
        events = []
        event_pattern = re.compile(
            r'(?:public|private|protected|internal)\s+'
            r'event\s+([\w\s<>]+?)\s+(\w+)\s*(?:{|;)'
        )

        for match in event_pattern.finditer(source_code):
            event_type = match.group(1).strip()
            event_name = match.group(2)
            events.append({
                "type": event_type,
                "name": event_name,
                "declaration": match.group(0).strip()
            })

        return events

    def _extract_properties(self, source_code: str) -> List[Dict[str, Any]]:
        """提取属性（Properties）"""
        properties = []

        for match in self.property_pattern.finditer(source_code):
            property_type = match.group(1).strip()
            property_name = match.group(2).strip()

            properties.append({
                "type": property_type,
                "name": property_name,
                "declaration": match.group(0).strip()
            })

        return properties

    def _extract_indexers(self, source_code: str) -> List[Dict[str, Any]]:
        """提取索引器（Indexers）"""
        indexers = []
        indexer_pattern = re.compile(
            r'(?:public|private|protected|internal)\s+'
            r'([\w\s<>?,\[\]]+)\s+this\s*\[([^\]]+)\]\s*(?:{|;)'
        )

        for match in indexer_pattern.finditer(source_code):
            indexer_type = match.group(1).strip()
            index_params = match.group(2).strip()

            indexers.append({
                "return_type": indexer_type,
                "parameters": index_params,
                "declaration": match.group(0).strip()
            })

        return indexers

    def _extract_generics(self, source_code: str) -> List[str]:
        """提取泛型定义"""
        generics = []
        generic_pattern = re.compile(r'<[^>]+>')

        for match in generic_pattern.finditer(source_code):
            generics.append(match.group(0))

        return generics

    def _extract_linq_queries(self, source_code: str) -> List[str]:
        """提取 LINQ 查询"""
        linq_patterns = [
            r'\.from\s*\(',
            r'\.where\s*\(',
            r'\.select\s*\(',
            r'\.orderby\s*\(',
            r'\.groupby\s*\(',
            r'\.join\s*\(',
        ]

        queries = []
        for pattern in linq_patterns:
            for match in re.finditer(pattern, source_code):
                queries.append(match.group(0))

        return queries

    def _extract_async_methods(self, source_code: str) -> List[str]:
        """提取异步方法"""
        async_methods = []

        # 查找 async 方法声明
        async_pattern = re.compile(
            r'(?:public|private|protected|internal|static)\s+async\s+[^{]+\s+(\w+)\s*\('
        )

        for match in async_pattern.finditer(source_code):
            method_name = match.group(1)
            async_methods.append(method_name)

        return async_methods