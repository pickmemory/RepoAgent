"""
.NET 文档生成器 - 生成符合 .NET 约定的高质量代码文档
"""

import re
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
from dataclasses import dataclass
import logging

from repo_agent.language import (
    Language, Function, Class, Import, ProjectStructure
)
from repo_agent.log import logger
from repo_agent.prompts.dotnet_prompts import (
    DotNetPromptGenerator,
    DotNetTerminology,
    DotNetCodeType,
    DotNetDocumentationTemplates
)


@dataclass
class DotNetDocConfig:
    """.NET 文档生成配置"""
    language: str = "Chinese"  # 输出语言
    include_xml_comments: bool = True  # 是否包含 XML 文档注释
    include_examples: bool = True  # 是否包含示例代码
    include_syntax_highlighting: bool = True  # 是否包含语法高亮
    include_namespace_info: bool = True  # 是否包含命名空间信息
    include_inheritance_info: bool = True  # 是否包含继承信息
    format_markdown: bool = True  # 是否使用 Markdown 格式
    max_example_lines: int = 10  # 示例代码最大行数


class DotNetDocumentGenerator:
    """.NET 文档生成器 - 生成符合 .NET 约定的专业文档"""

    def __init__(self, config: Optional[DotNetDocConfig] = None):
        """
        初始化文档生成器

        Args:
            config: 文档生成配置
        """
        self.config = config or DotNetDocConfig()
        self.prompt_generator = DotNetPromptGenerator()
        self.terminology = DotNetTerminology()
        self.templates = DotNetDocumentationTemplates()

        # XML 文档注释正则表达式
        self.xml_comment_pattern = re.compile(r'///\s*(<[^>]*>.*?</.*?>)', re.DOTALL)
        self.param_pattern = re.compile(r'<param\s+name="([^"]+)">\s*(.*?)\s*</param>', re.DOTALL)
        self.returns_pattern = re.compile(r'<returns>\s*(.*?)\s*</returns>', re.DOTALL)
        self.exception_pattern = re.compile(r'<exception\s+cref="[^"]*">\s*(.*?)\s*</exception>', re.DOTALL)
        self.summary_pattern = re.compile(r'<summary>\s*(.*?)\s*</summary>', re.DOTALL)

    def generate_documentation(
        self,
        project_structure: ProjectStructure,
        output_path: Optional[Union[str, Path]] = None,
        file_filter: Optional[List[str]] = None
    ) -> Dict[str, str]:
        """
        生成项目文档

        Args:
            project_structure: 项目结构数据
            output_path: 输出文件路径
            file_filter: 文件过滤器

        Returns:
            生成的文档字典 {文件路径: 文档内容}
        """
        logger.debug("开始生成 .NET 文档")

        documents = {}

        # 生成命名空间文档
        if self.config.include_namespace_info:
            namespace_docs = self._generate_namespace_documentation(project_structure)
            documents.update(namespace_docs)

        # 生成类文档
        class_docs = self._generate_class_documentation(project_structure)
        documents.update(class_docs)

        # 生成方法文档
        method_docs = self._generate_method_documentation(project_structure)
        documents.update(method_docs)

        # 如果指定了输出路径，保存文档
        if output_path:
            self._save_documents(documents, output_path)

        logger.debug(f"文档生成完成: {len(documents)} 个文档")
        return documents

    def generate_single_document(
        self,
        item_type: str,
        item_name: str,
        item_data: Dict[str, Any],
        project_context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        生成单个文档

        Args:
            item_type: 项目类型 (class, method, interface 等)
            item_name: 项目名称
            item_data: 项目数据
            project_context: 项目上下文

        Returns:
            生成的文档内容
        """
        # 生成提示
        prompt = self.prompt_generator.generate_documentation_prompt(
            code_name=item_name,
            code_type=item_type,
            code_content=item_data.get('content', ''),
            language=self.config.language,
            project_context=project_context or {}
        )

        # 这里应该调用 LLM 来生成实际文档
        # 由于我们专注于文档结构，返回格式化的模板内容
        template = self._get_template_for_type(item_type)

        # 填充模板
        formatted_doc = self._fill_template(template, item_name, item_data)

        return formatted_doc

    def _generate_namespace_documentation(self, project_structure: ProjectStructure) -> Dict[str, str]:
        """生成命名空间文档"""
        documents = {}

        for namespace in project_structure.namespaces:
            # 获取该命名空间下的所有类和方法
            namespace_classes = [cls for cls in project_structure.classes
                                if cls.name.startswith(namespace) or any(ns in cls.name for ns in namespace.split('.'))]
            namespace_methods = [func for func in project_structure.functions
                               if any(ns in func.name for ns in namespace.split('.'))]

            doc_content = f"""
# {namespace}

## Overview

This namespace contains {len(namespace_classes)} classes and {len(namespace_methods)} methods.

## Classes

{self._format_class_list(namespace_classes)}

## Methods

{self._format_method_list(namespace_methods)}

## Dependencies

{self._format_imports(project_structure.imports)}
""".strip()

            documents[f"{namespace}.md"] = doc_content

        return documents

    def _generate_class_documentation(self, project_structure: ProjectStructure) -> Dict[str, str]:
        """生成类文档"""
        documents = {}

        for cls in project_structure.classes:
            doc_content = self._generate_class_doc(cls, project_structure)
            documents[f"{cls.name}.md"] = doc_content

        return documents

    def _generate_method_documentation(self, project_structure: ProjectStructure) -> Dict[str, str]:
        """生成方法文档"""
        documents = {}

        for func in project_structure.functions:
            doc_content = self._generate_method_doc(func, project_structure)
            documents[f"{func.name}.md"] = doc_content

        return documents

    def _generate_class_doc(self, cls: Class, project_structure: ProjectStructure) -> str:
        """生成单个类的文档"""
        # 提取类的相关信息
        cls_type = "interface" if cls.is_interface else "struct" if cls.language_specific.get("is_struct") else "class"
        cls_name = cls.name

        # 从 language_specific 中提取更多信息
        language_specific = cls.language_specific or {}

        # 构建文档内容
        doc_content = self.templates.get_class_template()

        # 填充模板
        replacements = {
            "class_name": cls_name,
            "class_summary": self._extract_summary(cls),
            "code_type": cls_type,
            "namespace": ", ".join(project_structure.namespaces) if project_structure.namespaces else "Global",
            "assembly": "Unknown Assembly",  # 可以从项目结构中提取
            "inheritance_info": self._format_inheritance(cls),
            "interfaces_info": self._format_interfaces(cls),
            "syntax_declaration": self._format_class_syntax(cls),
            "properties_list": self._format_properties(cls.language_specific.get("properties", [])),
            "methods_list": self._format_methods(cls.methods),
            "events_list": self._format_events(cls.language_specific.get("events", [])),
            "fields_list": self._format_fields(cls.language_specific.get("fields", [])),
            "remarks": self._extract_remarks(cls),
            "examples": self._generate_class_examples(cls),
            "see_also": self._generate_see_also(cls)
        }

        # 执行替换
        for key, value in replacements.items():
            doc_content = doc_content.replace(f"{{{key}}}", str(value))

        return doc_content

    def _generate_method_doc(self, func: Function, project_structure: ProjectStructure) -> str:
        """生成单个方法的文档"""
        doc_content = self.templates.get_method_template()

        # 填充模板
        replacements = {
            "method_name": func.name,
            "method_summary": self._extract_method_summary(func),
            "generic_params": "",  # 从 language_specific 中提取
            "namespace": ", ".join(project_structure.namespaces) if project_structure.namespaces else "Global",
            "class_name": "",  # 需要从上下文获取
            "assembly": "Unknown Assembly",
            "syntax_declaration": self._format_method_syntax(func),
            "parameters_list": self._format_parameters(func.parameters),
            "return_type": func.return_type,
            "return_description": "",  # 需要分析返回值
            "exceptions_list": "",  # 需要分析异常
            "examples": self._generate_method_examples(func),
            "remarks": self._extract_method_remarks(func),
            "see_also": ""
        }

        # 执行替换
        for key, value in replacements.items():
            doc_content = doc_content.replace(f"{{{key}}}", str(value))

        return doc_content

    def _extract_xml_comments(self, source_code: str) -> Dict[str, str]:
        """从源代码中提取 XML 文档注释"""
        if not self.config.include_xml_comments:
            return {}

        xml_comments = {}

        # 提取所有 XML 注释
        matches = self.xml_comment_pattern.findall(source_code)
        for match in matches:
            # 解析不同类型的 XML 标签
            if "<summary>" in match:
                summary_match = self.summary_pattern.search(match)
                if summary_match:
                    xml_comments["summary"] = summary_match.group(1).strip()

            if "<param" in match:
                param_matches = self.param_pattern.findall(match)
                for param_name, param_desc in param_matches:
                    xml_comments[f"param_{param_name}"] = param_desc.strip()

            if "<returns>" in match:
                returns_match = self.returns_pattern.search(match)
                if returns_match:
                    xml_comments["returns"] = returns_match.group(1).strip()

            if "<exception" in match:
                exception_matches = self.exception_pattern.findall(match)
                for exception_desc in exception_matches:
                    xml_comments["exception"] = exception_desc.strip()

        return xml_comments

    def _format_class_syntax(self, cls: Class) -> str:
        """格式化类的语法声明"""
        modifiers = cls.access_level if cls.access_level else "public"

        if cls.is_interface:
            syntax = f"{modifiers} interface {cls.name}"
        elif cls.language_specific.get("is_struct"):
            syntax = f"{modifiers} struct {cls.name}"
        else:
            syntax = f"{modifiers} class {cls.name}"

        # 添加继承信息
        if cls.base_classes:
            syntax += f" : {', '.join(cls.base_classes)}"

        return syntax

    def _format_method_syntax(self, func: Function) -> str:
        """格式化方法的语法声明"""
        modifiers = " ".join([func.access_level] + (["async"] if func.is_async else []))
        params = ", ".join([f"{p.get('type', 'object')} {p['name']}" for p in func.parameters])

        syntax = f"{modifiers} {func.return_type} {func.name}({params})"
        return syntax

    def _format_properties(self, properties: List[Dict]) -> str:
        """格式化属性列表"""
        if not properties:
            return "No properties."

        formatted = []
        for prop in properties[:10]:  # 限制显示数量
            prop_name = prop.get('name', 'Unknown')
            prop_type = prop.get('type', 'object')
            formatted.append(f"- **{prop_name}** ({prop_type}): {prop.get('description', 'No description available')}")

        if len(properties) > 10:
            formatted.append(f"... and {len(properties) - 10} more properties")

        return "\n".join(formatted)

    def _format_methods(self, methods: List[Function]) -> str:
        """格式化方法列表"""
        if not methods:
            return "No methods."

        formatted = []
        for method in methods[:10]:  # 限制显示数量
            method_name = method.name
            return_type = method.return_type
            async_mark = "async " if method.is_async else ""
            formatted.append(f"- **{method_name}** ({async_mark}{return_type})")

        if len(methods) > 10:
            formatted.append(f"... and {len(methods) - 10} more methods")

        return "\n".join(formatted)

    def _format_events(self, events: List[Dict]) -> str:
        """格式化事件列表"""
        if not events:
            return "No events."

        formatted = []
        for event in events:
            event_name = event.get('name', 'Unknown')
            event_type = event.get('type', 'EventHandler')
            formatted.append(f"- **{event_name}** ({event_type})")

        return "\n".join(formatted)

    def _format_fields(self, fields: List[Dict]) -> str:
        """格式化字段列表"""
        if not fields:
            return "No fields."

        formatted = []
        for field in fields:
            field_name = field.get('name', 'Unknown')
            field_type = field.get('type', 'object')
            formatted.append(f"- **{field_name}** ({field_type})")

        return "\n".join(formatted)

    def _format_parameters(self, parameters: List[Dict]) -> str:
        """格式化参数列表"""
        if not parameters:
            return "No parameters."

        formatted = []
        for param in parameters:
            param_name = param.get('name', 'Unknown')
            param_type = param.get('type', 'object')
            param_desc = param.get('description', '')
            default_val = f" = {param.get('default', '')}" if param.get('default') else ""
            formatted.append(f"- **{param_name}** ({param_type}{default_val}): {param_desc}")

        return "\n".join(formatted)

    def _format_inheritance(self, cls: Class) -> str:
        """格式化继承信息"""
        if not cls.base_classes:
            return "No base class."
        return f"Inherits from: {', '.join(cls.base_classes)}"

    def _format_interfaces(self, cls: Class) -> str:
        """格式化接口信息"""
        if not cls.base_classes:
            return "No implemented interfaces."
        return f"Implements: {', '.join(cls.base_classes)}"

    def _extract_summary(self, cls: Class) -> str:
        """提取类的摘要信息"""
        # 从 language_specific 中获取 XML 文档注释
        docs = cls.language_specific.get("documentation", "")
        if docs:
            # 简单提取 summary 标签内容
            if "<summary>" in docs:
                match = self.summary_pattern.search(docs)
                if match:
                    return match.group(1).strip()

        return f"The {cls.name} class provides functionality for {cls.name.lower()} operations."

    def _extract_method_summary(self, func: Function) -> str:
        """提取方法摘要信息"""
        return f"The {func.name} method {self._verb_for_return_type(func.return_type)} {func.return_type} value."

    def _verb_for_return_type(self, return_type: str) -> str:
        """根据返回类型返回适当的动词"""
        if return_type == "void":
            return "performs"
        elif "Task" in return_type:
            return "asynchronously returns"
        elif return_type == "bool":
            return "returns a boolean indicating"
        elif return_type in ["int", "float", "double", "decimal"]:
            return "returns a numeric"
        elif return_type == "string":
            return "returns a string"
        else:
            return "returns an"

    def _extract_remarks(self, item: Union[Class, Function]) -> str:
        """提取备注信息"""
        return "No additional remarks available."

    def _extract_method_remarks(self, func: Function) -> str:
        """提取方法备注信息"""
        if func.is_async:
            return "This method is asynchronous and should be awaited."
        return "No additional remarks available."

    def _generate_class_examples(self, cls: Class) -> str:
        """生成类使用示例"""
        example = f"""
```csharp
// Example usage of {cls.name}
var instance = new {cls.name}();
// TODO: Add specific usage example
```
        """.strip()

        if not self.config.include_examples:
            return "No examples available."

        return example

    def _generate_method_examples(self, func: Function) -> str:
        """生成方法使用示例"""
        if func.is_async:
            example = f"""
```csharp
// Example usage of {func.name}
var result = await instance.{func.name}(/* parameters */);
```
            """.strip()
        else:
            example = f"""
```csharp
// Example usage of {func.name}
var result = instance.{func.name}(/* parameters */);
```
            """.strip()

        if not self.config.include_examples:
            return "No examples available."

        return example

    def _generate_see_also(self, item: Union[Class, Function]) -> str:
        """生成参见信息"""
        return "- Related documentation"

    def _format_class_list(self, classes: List[Class]) -> str:
        """格式化类列表"""
        if not classes:
            return "No classes in this namespace."

        formatted = []
        for cls in classes[:10]:
            cls_name = cls.name
            cls_type = "Interface" if cls.is_interface else "Struct" if cls.language_specific.get("is_struct") else "Class"
            formatted.append(f"- [{cls_type}] **{cls_name}**")

        return "\n".join(formatted)

    def _format_method_list(self, methods: List[Function]) -> str:
        """格式化方法列表"""
        if not methods:
            return "No methods in this namespace."

        formatted = []
        for method in methods[:10]:
            method_name = method.name
            async_mark = "🔄 " if method.is_async else ""
            formatted.append(f"- {async_mark}**{method_name}** ({method.return_type})")

        return "\n".join(formatted)

    def _format_imports(self, imports: List[Import]) -> str:
        """格式化导入信息"""
        if not imports:
            return "No external dependencies."

        # 按命名空间分组
        namespaces = {}
        for imp in imports:
            ns = imp.module.split('.')[0]
            if ns not in namespaces:
                namespaces[ns] = []
            namespaces[ns].append(imp.module)

        formatted = []
        for ns, modules in sorted(namespaces.items()):
            formatted.append(f"**{ns}**:")
            for module in sorted(set(modules)):
                formatted.append(f"- `{module}`")

        return "\n".join(formatted)

    def _get_template_for_type(self, item_type: str) -> str:
        """根据类型获取模板"""
        type_map = {
            "class": self.templates.get_class_template,
            "interface": self.templates.get_interface_template,
            "struct": self.templates.get_struct_template,
            "method": self.templates.get_method_template,
            "property": self.templates.get_class_template,  # 使用类模板作为基础
            "field": self.templates.get_class_template,
            "event": self.templates.get_class_template
        }

        template_func = type_map.get(item_type.lower(), self.templates.get_class_template)
        return template_func()

    def _fill_template(self, template: str, item_name: str, item_data: Dict[str, Any]) -> str:
        """填充模板"""
        # 基础替换
        result = template
        result = result.replace("{class_name}", item_name)
        result = result.replace("{method_name}", item_name)
        result = result.replace("{interface_name}", item_name)
        result = result.replace("{struct_name}", item_name)
        result = result.replace("{property_name}", item_name)
        result = result.replace("{field_name}", item_name)
        result = result.replace("{event_name}", item_name)

        # 从 item_data 中提取信息并替换
        for key, value in item_data.items():
            placeholder = f"{{{key}}}"
            if placeholder in result:
                result = result.replace(placeholder, str(value))

        return result

    def _save_documents(self, documents: Dict[str, str], output_path: Union[str, Path]):
        """保存文档到文件"""
        output_path = Path(output_path)
        output_path.mkdir(parents=True, exist_ok=True)

        for filename, content in documents.items():
            file_path = output_path / filename
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            logger.debug(f"文档已保存: {file_path}")


# 便捷函数
def create_dotnet_documenter(config: Optional[DotNetDocConfig] = None) -> DotNetDocumentGenerator:
    """创建 .NET 文档生成器实例"""
    return DotNetDocumentGenerator(config)