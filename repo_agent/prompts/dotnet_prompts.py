"""
.NET 特定的文档生成提示模板
提供符合 .NET 开发习惯的术语、格式和约定
"""

from typing import Dict, List, Optional
from enum import Enum


class DotNetCodeType(Enum):
    """.NET 代码类型枚举"""
    CLASS = "class"
    INTERFACE = "interface"
    STRUCT = "struct"
    ENUM = "enum"
    DELEGATE = "delegate"
    METHOD = "method"
    PROPERTY = "property"
    FIELD = "field"
    EVENT = "event"
    CONSTRUCTOR = "constructor"
    NAMESPACE = "namespace"
    INDEXER = "indexer"
    OPERATOR = "operator"


class DotNetTerminology:
    """.NET 术语映射"""

    # 通用术语映射
    COMMON_TERMS = {
        "function": "method",
        "函数": "方法",
        "类": "class",
        "接口": "interface",
        "结构体": "struct",
        "枚举": "enum",
        "委托": "delegate",
        "属性": "property",
        "字段": "field",
        "事件": "event",
        "构造函数": "constructor",
        "命名空间": "namespace",
        "索引器": "indexer",
        "运算符": "operator",
        "泛型": "generic",
        "继承": "inheritance",
        "实现": "implementation",
        "重写": "override",
        "重载": "overload",
        "抽象": "abstract",
        "虚函数": "virtual method",
        "静态": "static",
        "异步": "async",
        "等待": "await",
        "Lambda表达式": "lambda expression",
        "LINQ": "LINQ (Language Integrated Query)",
        "特性": "attribute",
        "扩展方法": "extension method",
        "局部函数": "local function",
        "可空": "nullable",
        "元组": "tuple"
    }

    # 访问修饰符
    ACCESS_MODIFIERS = {
        "public": "public",
        "private": "private",
        "protected": "protected",
        "internal": "internal",
        "protected internal": "protected internal",
        "private protected": "private protected"
    }

    # 类型修饰符
    TYPE_MODIFIERS = {
        "abstract": "abstract",
        "sealed": "sealed",
        "static": "static",
        "virtual": "virtual",
        "override": "override",
        "readonly": "readonly",
        "const": "const",
        "volatile": "volatile"
    }

    def translate_to_dotnet_terminology(self, text: str) -> str:
        """将通用术语转换为 .NET 术语"""
        # 使用术语映射进行转换
        for generic, dotnet_term in self.COMMON_TERMS.items():
            text = text.replace(generic, dotnet_term)
        return text


class DotNetDocumentationTemplates:
    """.NET 文档生成模板"""

    @staticmethod
    def get_class_template() -> str:
        """获取类文档模板"""
        return """
**{class_name}**: {class_summary}

**Type**: {code_type}
**Namespace**: {namespace}
**Assembly**: {assembly}

**Inheritance**:
{inheritance_info}

**Implemented Interfaces**:
{interfaces_info}

**Syntax**:
```csharp
{syntax_declaration}
```

**Properties**:
{properties_list}

**Methods**:
{methods_list}

**Events**:
{events_list}

**Fields**:
{fields_list}

**Remarks**:
{remarks}

**Examples**:
{examples}

**See Also**:
{see_also}
""".strip()

    @staticmethod
    def get_method_template() -> str:
        """获取方法文档模板"""
        return """
**{method_name}**({generic_params}): {method_summary}

**Namespace**: {namespace}
**Class**: {class_name}
**Assembly**: {assembly}

**Syntax**:
```csharp
{syntax_declaration}
```

**Parameters**:
{parameters_list}

**Return Value**:
{return_type} - {return_description}

**Exceptions**:
{exceptions_list}

**Examples**:
{examples}

**Remarks**:
{remarks}

**See Also**:
{see_also}
""".strip()

    @staticmethod
    def get_interface_template() -> str:
        """获取接口文档模板"""
        return """
**{interface_name}**: {interface_summary}

**Type**: interface
**Namespace**: {namespace}
**Assembly**: {assembly}

**Generic Parameters**:
{generic_params}

**Syntax**:
```csharp
{syntax_declaration}
```

**Properties**:
{properties_list}

**Methods**:
{methods_list}

**Events**:
{events_list}

**Remarks**:
{remarks}

**Examples**:
{examples}

**See Also**:
{see_also}
""".strip()

    @staticmethod
    def get_struct_template() -> str:
        """获取结构体文档模板"""
        return """
**{struct_name}**: {struct_summary}

**Type**: struct
**Namespace**: {namespace}
**Assembly**: {assembly}

**Syntax**:
```csharp
{syntax_declaration}
```

**Implements**:
{interfaces_info}

**Fields**:
{fields_list}

**Properties**:
{properties_list}

**Methods**:
{methods_list}

**Constructors**:
{constructors_list}

**Operators**:
{operators_list}

**Examples**:
{examples}

**Remarks**:
{remarks}

**See Also**:
{see_also}
""".strip()


class DotNetPromptGenerator:
    """.NET 文档提示生成器"""

    def __init__(self):
        self.terminology = DotNetTerminology()
        self.templates = DotNetDocumentationTemplates()

    def generate_documentation_prompt(
        self,
        code_name: str,
        code_type: str,
        code_content: str,
        language: str = "Chinese",
        project_context: Optional[Dict] = None
    ) -> str:
        """
        生成 .NET 文档生成的提示

        Args:
            code_name: 代码元素名称
            code_type: 代码类型
            code_content: 代码内容
            language: 输出语言
            project_context: 项目上下文信息

        Returns:
            格式化的提示字符串
        """
        # 基础指令
        base_instruction = f"""
You are an expert .NET documentation assistant specializing in creating high-quality technical documentation for .NET code.

Your task is to generate comprehensive documentation for a {code_type} named "{code_name}".

## Documentation Requirements:

1. **Use .NET Terminology**: Use standard .NET terminology and naming conventions:
   - Use "method" instead of "function"
   - Use "property" instead of "attribute"
   - Use "field" for class variables
   - Use "event" for event handlers
   - Use "namespace" for organization
   - Use proper C# syntax highlighting

2. **Follow .NET Documentation Standards**:
   - Include XML documentation comments when available
   - Show method signatures with proper C# syntax
   - Document all public and protected members
   - Include inheritance hierarchies
   - Document generic parameters and constraints
   - Show accessibility levels (public, private, protected, internal)

3. **Code Examples**:
   - Provide practical C# code examples
   - Show usage patterns
   - Include error handling examples where relevant
   - Demonstrate async/await patterns for async methods

4. **Structure**:
   Start with the element name and a one-sentence summary
   Include syntax declarations in code blocks
   Document all parameters, return values, and exceptions
   Add examples and remarks sections
   Include cross-references to related types

## Code Content:
```csharp
{code_content}
```

## Project Context:
{self._format_project_context(project_context)}

## Output Language: {language}

Please generate professional .NET documentation following these guidelines.
"""

        # 特定类型的额外指令
        type_specific_instructions = self._get_type_specific_instructions(code_type)

        return base_instruction + "\n\n" + type_specific_instructions

    def _get_type_specific_instructions(self, code_type: str) -> str:
        """获取特定类型的额外指令"""
        instructions = {
            "class": """
For classes, please include:
- Inheritance hierarchy (base class and derived classes)
- Implemented interfaces
- All public and protected members
- Constructors and their overloads
- Static members vs instance members
- Thread safety information if applicable
""",
            "interface": """
For interfaces, please include:
- All method and property signatures
- Generic type parameters and constraints
- Default interface methods (if any)
- Common implementation patterns
- Relationship to other interfaces
""",
            "method": """
For methods, please include:
- All overloads of the method
- Generic type parameters and constraints
- Parameter descriptions with types and nullability
- Return type and possible null values
- Exceptions that may be thrown
- Thread safety considerations
- Async patterns (if method is asynchronous)
""",
            "property": """
For properties, please include:
- Property type and nullability
- Get and set accessor visibility
- Validation logic (if applicable)
- Computed property behavior
- Indexer patterns (if applicable)
""",
            "struct": """
For structs, please include:
- Value type semantics
- Default values
- Immutability considerations
- Performance implications
- Comparison methods (Equals, GetHashCode)
""",
            "enum": """
For enums, please include:
- Underlying type
- All enum values and their meanings
- Flags enumeration patterns (if applicable)
- Common usage scenarios
"""
        }

        return instructions.get(code_type.lower(), "")

    def _format_project_context(self, project_context: Optional[Dict]) -> str:
        """格式化项目上下文信息"""
        if not project_context:
            return "No specific project context provided."

        context_parts = []

        if "namespace" in project_context:
            context_parts.append(f"Namespace: {project_context['namespace']}")

        if "assembly" in project_context:
            context_parts.append(f"Assembly: {project_context['assembly']}")

        if "dependencies" in project_context:
            deps = project_context["dependencies"]
            if isinstance(deps, list) and deps:
                context_parts.append(f"Key Dependencies: {', '.join(deps[:5])}")

        if "related_types" in project_context:
            related = project_context["related_types"]
            if isinstance(related, list) and related:
                context_parts.append(f"Related Types: {', '.join(related[:5])}")

        return "\n".join(context_parts) if context_parts else "No specific project context provided."

    def translate_to_dotnet_terminology(self, text: str) -> str:
        """将通用术语转换为 .NET 术语"""
        # 使用术语映射进行转换
        for generic, dotnet_term in self.terminology.COMMON_TERMS.items():
            text = text.replace(generic, dotnet_term)

        return text

    def format_csharp_signature(self, signature_info: Dict) -> str:
        """格式化 C# 方法签名"""
        modifiers = signature_info.get("modifiers", [])
        return_type = signature_info.get("return_type", "void")
        name = signature_info.get("name", "")
        parameters = signature_info.get("parameters", [])
        generic_params = signature_info.get("generic_parameters", [])

        # 构建泛型参数
        generic_str = ""
        if generic_params:
            generic_str = f"<{', '.join(generic_params)}>"

        # 构建参数列表
        param_str = ""
        if parameters:
            param_list = []
            for param in parameters:
                param_type = param.get("type", "")
                param_name = param.get("name", "")
                default_val = param.get("default", "")
                if default_val:
                    param_list.append(f"{param_type} {param_name} = {default_val}")
                else:
                    param_list.append(f"{param_type} {param_name}")
            param_str = f"({', '.join(param_list)})"
        else:
            param_str = "()"

        # 组装完整签名
        modifier_str = " ".join(modifiers)
        if modifier_str:
            return f"{modifier_str} {return_type} {name}{generic_str}{param_str}"
        else:
            return f"{return_type} {name}{generic_str}{param_str}"


# 便捷函数
def create_dotnet_prompt_generator() -> DotNetPromptGenerator:
    """创建 .NET 提示生成器实例"""
    return DotNetPromptGenerator()


def generate_dotnet_doc_prompt(
    code_name: str,
    code_type: str,
    code_content: str,
    language: str = "Chinese",
    **kwargs
) -> str:
    """生成 .NET 文档提示的便捷函数"""
    generator = create_dotnet_prompt_generator()
    return generator.generate_documentation_prompt(
        code_name=code_name,
        code_type=code_type,
        code_content=code_content,
        language=language,
        **kwargs
    )