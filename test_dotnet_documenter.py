#!/usr/bin/env python
"""测试 .NET 文档生成器"""

import sys
import os
sys.path.insert(0, '.')

# 设置临时的 API 密钥以避免验证错误
os.environ['OPENAI_API_KEY'] = 'test-key-for-configuration-testing'

try:
    from repo_agent.documenters.dotnet_documenter import (
        DotNetDocumentGenerator,
        DotNetDocConfig,
        create_dotnet_documenter
    )
    from repo_agent.language import (
        Language, Function, Class, Import, ProjectStructure,
        get_language_metadata
    )
    from pathlib import Path

    print("[OK] .NET 文档生成器模块导入成功")

    # 创建测试用的项目结构
    print("\n=== 创建测试数据 ===")

    # 创建测试函数
    test_functions = [
        Function(
            name="CalculateSum",
            parameters=[
                {"name": "a", "type": "int", "default": None},
                {"name": "b", "type": "int", "default": None}
            ],
            return_type="int",
            is_async=False,
            access_level="public",
            language_specific={
                "full_signature": "public int CalculateSum(int a, int b)",
                "description": "计算两个整数的和"
            }
        ),
        Function(
            name="GetUserAsync",
            parameters=[
                {"name": "userId", "type": "int", "default": None},
                {"name": "cancellationToken", "type": "CancellationToken", "default": "default"}
            ],
            return_type="Task<User>",
            is_async=True,
            access_level="public",
            language_specific={
                "full_signature": "public async Task<User> GetUserAsync(int userId, CancellationToken cancellationToken = default)",
                "description": "异步获取用户信息"
            }
        )
    ]

    # 创建测试类
    test_classes = [
        Class(
            name="Calculator",
            base_classes=["BaseCalculator"],
            methods=test_functions,
            properties=[],
            is_interface=False,
            is_abstract=False,
            access_level="public",
            language_specific={
                "is_struct": False,
                "documentation": """<summary>
    计算器类，提供基本的数学运算功能
    </summary>
                <param name="result">当前计算结果</param>
                <returns>计算器实例</returns>""",
                "properties": [
                    {
                        "name": "Result",
                        "type": "double",
                        "description": "获取当前计算结果"
                    }
                ],
                "fields": [
                    {
                        "name": "_result",
                        "type": "double",
                        "description": "私有字段存储计算结果"
                    }
                ],
                "events": []
            }
        ),
        Class(
            name="ICalculator",
            base_classes=[],
            methods=[test_functions[0]],  # 只包含 CalculateSum 方法
            properties=[],
            is_interface=True,
            is_abstract=True,
            access_level="public",
            language_specific={
                "is_struct": False,
                "documentation": "<summary>计算器接口定义</summary>"
            }
        )
    ]

    # 创建测试导入
    test_imports = [
        Import(
            module="System",
            name=None,
            alias=None,
            is_wildcard=False
        ),
        Import(
            module="System.Threading.Tasks",
            name=None,
            alias=None,
            is_wildcard=False
        )
    ]

    # 创建项目结构
    project_structure = ProjectStructure(
        language=Language.CSHARP,
        functions=test_functions,
        classes=test_classes,
        imports=test_imports,
        namespaces=["MathOperations", "MathOperations.Advanced"],
        language_metadata=get_language_metadata(Language.CSHARP)
    )

    print(f"创建了 {len(test_functions)} 个函数, {len(test_classes)} 个类, {len(test_imports)} 个导入")

    # 创建文档生成器
    print("\n=== 初始化文档生成器 ===")
    config = DotNetDocConfig(
        language="Chinese",
        include_xml_comments=True,
        include_examples=True,
        include_syntax_highlighting=True
    )
    documenter = DotNetDocumentGenerator(config)
    print("[OK] 文档生成器初始化成功")

    # 测试单个类文档生成
    print("\n=== 测试单个类文档生成 ===")
    test_class = test_classes[0]  # Calculator 类

    class_data = {
        "content": """
public class Calculator : BaseCalculator
{
    private double _result;

    public Calculator() { _result = 0; }

    public int CalculateSum(int a, int b) => a + b;
}""".strip(),
        "access_level": "public",
        "is_abstract": False
    }

    class_doc = documenter.generate_single_document(
        item_type="class",
        item_name="Calculator",
        item_data=class_data,
        project_context={
            "namespace": "MathOperations",
            "assembly": "MathLibrary"
        }
    )

    print(f"[OK] 类文档生成成功")
    print(f"  文档长度: {len(class_doc)} 字符")
    print(f"  包含模板占位符: {class_doc.count('{')}")

    # 显示文档前几行
    print("\n文档预览:")
    for i, line in enumerate(class_doc.split('\n')[:8]):
        print(f"  {line}")

    # 测试单个方法文档生成
    print("\n=== 测试单个方法文档生成 ===")
    method_data = {
        "content": "public async Task<User> GetUserAsync(int userId) { /* 实现 */ }",
        "return_type": "Task<User>",
        "is_async": True
    }

    method_doc = documenter.generate_single_document(
        item_type="method",
        item_name="GetUserAsync",
        item_data=method_data
    )

    print(f"[OK] 方法文档生成成功")
    print(f"  文档长度: {len(method_doc)} 字符")

    # 测试完整项目文档生成
    print("\n=== 测试完整项目文档生成 ===")
    try:
        documents = documenter.generate_documentation(project_structure)
        print(f"[OK] 项目文档生成成功")
        print(f"  生成文档数量: {len(documents)}")

        # 显示生成的文档列表
        for filename in sorted(documents.keys())[:5]:
            doc_length = len(documents[filename])
            print(f"    - {filename} ({doc_length} 字符)")

        if len(documents) > 5:
            print(f"    ... and {len(documents) - 5} more documents")

        # 测试保存到文件
        output_dir = Path("test_dotnet_docs_output")
        documenter._save_documents(documents, output_dir)
        print(f"[OK] 文档已保存到: {output_dir}")

    except Exception as e:
        print(f"[ERROR] 项目文档生成失败: {e}")
        import traceback
        traceback.print_exc()

    # 测试配置选项
    print("\n=== 测试配置选项 ===")

    # 英文配置
    english_config = DotNetDocConfig(language="English")
    english_documenter = DotNetDocumentGenerator(english_config)

    # 不包含示例的配置
    no_examples_config = DotNetDocConfig(
        language="Chinese",
        include_examples=False
    )
    no_examples_documenter = DotNetDocumentGenerator(no_examples_config)

    print("[OK] 不同配置的文档生成器创建成功")

    print("\n所有测试完成！")

except ImportError as e:
    print(f"[ERROR] 导入错误: {e}")
    import traceback
    traceback.print_exc()
except Exception as e:
    print(f"[ERROR] 运行错误: {e}")
    import traceback
    traceback.print_exc()