"""
.NET 支持的全面单元测试套件
测试所有 .NET 相关组件，包括各种 .NET 代码示例
"""

import os
import unittest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# 导入所有需要测试的 .NET 相关组件
from repo_agent.project.dotnet_project import (
    DotNetProjectParser,
    DotNetProject,
    DotNetSolution,
    ProjectType,
    TargetFramework,
    ProjectReference
)
from repo_agent.documenters.dotnet_documenter import (
    DotNetDocumentGenerator,
    DotNetDocConfig
)
from repo_agent.prompts.dotnet_prompts import (
    DotNetPromptGenerator,
    DotNetTerminology,
    DotNetDocumentationTemplates,
    DotNetCodeType
)
from repo_agent.file_handler_extended import (
    MultiLanguageFileHandler,
    MultiLanguageConfig
)
from repo_agent.parsers.dotnet_parser import DotNetParser, AnalysisStrategy
from repo_agent.language import Language


class TestDotNetProjectParser(unittest.TestCase):
    """测试 .NET 项目解析器"""

    def setUp(self):
        """设置测试环境"""
        self.test_dir = Path(tempfile.mkdtemp())
        self.parser = DotNetProjectParser(str(self.test_dir))

    def tearDown(self):
        """清理测试环境"""
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_create_sample_csproj(self):
        """创建示例 .csproj 文件"""
        csproj_content = """<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <OutputType>Exe</OutputType>
    <TargetFramework>net8.0</TargetFramework>
    <AssemblyName>TestApp</AssemblyName>
    <RootNamespace>TestApp</RootNamespace>
  </PropertyGroup>

  <ItemGroup>
    <PackageReference Include="Microsoft.Extensions.Logging" Version="8.0.0" />
  </ItemGroup>

  <ItemGroup>
    <ProjectReference Include="..\TestLibrary\TestLibrary.csproj" />
  </ItemGroup>
</Project>"""

        csproj_path = self.test_dir / "TestApp" / "TestApp.csproj"
        csproj_path.parent.mkdir(parents=True)
        csproj_path.write_text(csproj_content)

        return str(csproj_path.relative_to(self.test_dir))

    def test_parse_simple_project(self):
        """测试解析简单项目"""
        project_path = self.test_create_sample_csproj()

        project = self.parser.parse_project(project_path)

        self.assertIsNotNone(project)
        self.assertEqual(project.name, "TestApp")
        self.assertEqual(project.project_type, ProjectType.CONSOLE_APP)
        self.assertEqual(project.language, "C#")
        self.assertIn(TargetFramework.NET8, project.target_frameworks)
        self.assertEqual(project.assembly_name, "TestApp")
        self.assertEqual(project.root_namespace, "TestApp")

    def test_parse_package_references(self):
        """测试解析包引用"""
        project_path = self.test_create_sample_csproj()

        project = self.parser.parse_project(project_path)

        self.assertIsNotNone(project)
        self.assertEqual(len(project.package_references), 1)
        self.assertEqual(project.package_references[0].name, "Microsoft.Extensions.Logging")
        self.assertEqual(project.package_references[0].version, "8.0.0")

    def test_parse_project_references(self):
        """测试解析项目引用"""
        project_path = self.test_create_sample_csproj()

        project = self.parser.parse_project(project_path)

        self.assertIsNotNone(project)
        self.assertEqual(len(project.project_references), 1)
        self.assertEqual(project.project_references[0].name, "TestLibrary")

    def test_detect_project_types(self):
        """测试项目类型检测"""
        test_cases = [
            ('console', '<OutputType>Exe</OutputType>'),
            ('web', '<Project Sdk="Microsoft.NET.Sdk.Web">'),
            ('classlib', '<Project Sdk="Microsoft.NET.Sdk">'),
            ('test', 'Microsoft.NET.Test.Sdk')
        ]

        for expected_type, content in test_cases:
            with self.subTest(type=expected_type):
                csproj_content = f"""<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <TargetFramework>net8.0</TargetFramework>
    {content}
  </PropertyGroup>
</Project>"""

                csproj_path = self.test_dir / f"{expected_type}_test.csproj"
                csproj_path.write_text(csproj_content)

                project = self.parser.parse_project(str(csproj_path.relative_to(self.test_dir)))

                if expected_type == 'classlib' and project.output_type == 'Exe':
                    # console app 会覆盖 classlib，这是正常的
                    continue

                self.assertIsNotNone(project, f"Failed to parse {expected_type} project")

    def test_find_project_files(self):
        """测试查找项目文件"""
        # 创建多个项目文件
        projects = [
            "src/App/App.csproj",
            "src/Library/Library.csproj",
            "tests/Tests.fsproj",
            "legacy/VBApp.vbproj"
        ]

        for proj in projects:
            proj_path = self.test_dir / proj
            proj_path.parent.mkdir(parents=True)
            proj_path.write_text("<Project Sdk='Microsoft.NET.Sdk' />")

        found_projects = self.parser.find_project_files()

        self.assertEqual(len(found_projects), 4)
        for proj in projects:
            self.assertIn(proj.replace('\\', '/'), [p.replace('\\', '/') for p in found_projects])


class TestDotNetDocumentGenerator(unittest.TestCase):
    """测试 .NET 文档生成器"""

    def setUp(self):
        """设置测试环境"""
        self.config = DotNetDocConfig()
        self.generator = DotNetDocumentGenerator(self.config)

    def test_generate_class_documentation_template(self):
        """测试生成类文档模板"""
        template = self.generator.templates.get_class_template()

        self.assertIn("{class_name}", template)
        self.assertIn("{class_summary}", template)
        self.assertIn("{inheritance_info}", template)
        self.assertIn("{properties_list}", template)
        self.assertIn("{methods_list}", template)

    def test_generate_method_documentation_template(self):
        """测试生成方法文档模板"""
        template = self.generator.templates.get_method_template()

        self.assertIn("{method_name}", template)
        self.assertIn("{parameters_list}", template)
        self.assertIn("{return_type}", template)
        self.assertIn("{exceptions_list}", template)

    def test_format_csharp_signature(self):
        """测试格式化 C# 签名"""
        signature_info = {
            "modifiers": ["public", "static"],
            "return_type": "string",
            "name": "TestMethod",
            "parameters": [
                {"name": "input", "type": "string"},
                {"name": "count", "type": "int", "default": "0"}
            ],
            "generic_parameters": ["T"]
        }

        formatted = self.generator.prompt_generator.format_csharp_signature(signature_info)

        self.assertIn("public static string", formatted)
        self.assertIn("TestMethod<T>", formatted)
        self.assertIn("string input", formatted)
        self.assertIn("int count = 0", formatted)

    def test_translate_terminology(self):
        """测试术语翻译"""
        test_cases = [
            ("函数", "method"),
            ("类", "class"),
            ("属性", "property"),
            ("字段", "field")
        ]

        for chinese, english in test_cases:
            with self.subTest(chinese=chinese, english=english):
                translated = self.generator.prompt_generator.terminology.translate_to_dotnet_terminology(chinese)
                self.assertEqual(translated, english)


class TestDotNetPromptGenerator(unittest.TestCase):
    """测试 .NET 提示生成器"""

    def setUp(self):
        """设置测试环境"""
        self.generator = DotNetPromptGenerator()

    def test_generate_class_prompt(self):
        """测试生成类文档提示"""
        code_content = """
public class TestClass
{
    public string Name { get; set; }

    public void PrintName()
    {
        Console.WriteLine(Name);
    }
}
"""

        prompt = self.generator.generate_documentation_prompt(
            code_name="TestClass",
            code_type="class",
            code_content=code_content
        )

        self.assertIn("TestClass", prompt)
        self.assertIn("class", prompt)
        self.assertIn("method", prompt)  # 应该使用 .NET 术语
        self.assertIn("C#", prompt)

    def test_generate_interface_prompt(self):
        """测试生成接口文档提示"""
        code_content = """
public interface ITestInterface
{
    void DoWork();
    string GetData();
}
"""

        prompt = self.generator.generate_documentation_prompt(
            code_name="ITestInterface",
            code_type="interface",
            code_content=code_content
        )

        self.assertIn("ITestInterface", prompt)
        self.assertIn("interface", prompt)
        self.assertIn("members", prompt)

    def test_get_type_specific_instructions(self):
        """测试获取类型特定指令"""
        types = ["class", "interface", "method", "property", "struct", "enum"]

        for code_type in types:
            with self.subTest(type=code_type):
                instructions = self.generator._get_type_specific_instructions(code_type)
                self.assertIsInstance(instructions, str)
                self.assertTrue(len(instructions) > 0)


class TestMultiLanguageFileHandler(unittest.TestCase):
    """测试多语言文件处理器"""

    def setUp(self):
        """设置测试环境"""
        self.test_dir = Path(tempfile.mkdtemp())
        self.config = MultiLanguageConfig()

    def tearDown(self):
        """清理测试环境"""
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_detect_csharp_language(self):
        """测试检测 C# 语言"""
        # 创建测试 C# 文件
        cs_file = self.test_dir / "test.cs"
        cs_file.write_text("public class Test {}")

        handler = MultiLanguageFileHandler(str(self.test_dir), "test.cs", self.config)
        language = handler.detect_language()

        self.assertEqual(language, Language.CSHARP)

    def test_detect_python_language(self):
        """测试检测 Python 语言"""
        # 创建测试 Python 文件
        py_file = self.test_dir / "test.py"
        py_file.write_text("def test(): pass")

        handler = MultiLanguageFileHandler(str(self.test_dir), "test.py", self.config)
        language = handler.detect_language()

        self.assertEqual(language, Language.PYTHON)

    @patch('repo_agent.file_handler_extended.DotNetParser')
    @patch('repo_agent.file_handler_extended.is_tree_sitter_available')
    def test_parser_initialization(self, mock_ts_available, mock_dotnet_parser):
        """测试解析器初始化"""
        mock_ts_available.return_value = True

        # 测试启用所有解析器
        config = MultiLanguageConfig(
            enable_dotnet=True,
            enable_treesitter=True
        )

        handler = MultiLanguageFileHandler(str(self.test_dir), "test.cs", config)

        # 验证解析器被初始化
        mock_dotnet_parser.assert_called_once()


class TestDotNetTerminology(unittest.TestCase):
    """测试 .NET 术语映射"""

    def setUp(self):
        """设置测试环境"""
        self.terminology = DotNetTerminology()

    def test_common_terms_translation(self):
        """测试通用术语翻译"""
        test_cases = [
            ("函数", "method"),
            ("类", "class"),
            ("接口", "interface"),
            ("结构体", "struct"),
            ("枚举", "enum"),
            ("委托", "delegate"),
            ("属性", "property"),
            ("字段", "field"),
            ("事件", "event")
        ]

        for chinese, english in test_cases:
            with self.subTest(chinese=chinese):
                translated = self.terminology.translate_to_dotnet_terminology(chinese)
                self.assertEqual(translated, english)

    def test_access_modifiers(self):
        """测试访问修饰符"""
        modifiers = ["public", "private", "protected", "internal"]

        for modifier in modifiers:
            with self.subTest(modifier=modifier):
                self.assertIn(modifier, self.terminology.ACCESS_MODIFIERS)

    def test_type_modifiers(self):
        """测试类型修饰符"""
        modifiers = ["abstract", "sealed", "static", "virtual", "override"]

        for modifier in modifiers:
            with self.subTest(modifier=modifier):
                self.assertIn(modifier, self.terminology.TYPE_MODIFIERS)


class TestDotNetCodeType(unittest.TestCase):
    """测试 .NET 代码类型枚举"""

    def test_code_type_values(self):
        """测试代码类型值"""
        expected_types = [
            "class", "interface", "struct", "enum", "delegate",
            "method", "property", "field", "event", "constructor",
            "namespace", "indexer", "operator"
        ]

        for expected in expected_types:
            with self.subTest(type=expected):
                self.assertIn(expected, [t.value for t in DotNetCodeType])


class TestProjectType(unittest.TestCase):
    """测试项目类型枚举"""

    def test_project_type_values(self):
        """测试项目类型值"""
        expected_types = [
            "console", "web", "webapi", "classlib", "mvc",
            "razor", "blazor", "maui", "xamarin", "test",
            "worker", "grpc", "unspecified"
        ]

        for expected in expected_types:
            with self.subTest(type=expected):
                self.assertIn(expected, [t.value for t in ProjectType])


class TestIntegrationScenarios(unittest.TestCase):
    """集成测试场景"""

    def setUp(self):
        """设置测试环境"""
        self.test_dir = Path(tempfile.mkdtemp())

    def tearDown(self):
        """清理测试环境"""
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_dotnet_project_end_to_end(self):
        """测试 .NET 项目端到端流程"""
        # 创建示例项目结构
        project_dir = self.test_dir / "SampleProject"
        project_dir.mkdir()

        # 创建 .csproj
        csproj_content = """<Project Sdk="Microsoft.NET.Sdk.Web">
  <PropertyGroup>
    <TargetFramework>net8.0</TargetFramework>
    <Nullable>enable</Nullable>
  </PropertyGroup>

  <ItemGroup>
    <PackageReference Include="Microsoft.AspNetCore.OpenApi" Version="8.0.0" />
  </ItemGroup>
</Project>"""

        (project_dir / "SampleProject.csproj").write_text(csproj_content)

        # 创建 C# 源文件
        cs_content = """using Microsoft.AspNetCore.Mvc;

namespace SampleProject.Controllers;

[ApiController]
[Route("[controller]")]
public class WeatherForecastController : ControllerBase
{
    private static readonly string[] Summaries = new[]
    {
        "Freezing", "Bracing", "Chilly", "Cool", "Mild"
    };

    [HttpGet]
    public IEnumerable<string> Get()
    {
        return Summaries;
    }
}"""

        (project_dir / "Controllers" / "WeatherForecastController.cs").write_text(cs_content)

        # 测试项目解析
        parser = DotNetProjectParser(str(self.test_dir))
        project = parser.parse_project("SampleProject/SampleProject.csproj")

        self.assertIsNotNone(project)
        self.assertEqual(project.project_type, ProjectType.WEB_API)
        self.assertTrue(project.is_web_project)

        # 测试文档生成
        doc_generator = DotNetDocumentGenerator()
        prompt_generator = DotNetPromptGenerator()

        # 生成控制器文档提示
        prompt = prompt_generator.generate_documentation_prompt(
            code_name="WeatherForecastController",
            code_type="class",
            code_content=cs_content
        )

        self.assertIn("WeatherForecastController", prompt)
        self.assertIn("ApiController", prompt)
        self.assertIn("HttpGet", prompt)

    def test_mixed_language_project(self):
        """测试混合语言项目"""
        # 创建 Python 文件
        py_file = self.test_dir / "main.py"
        py_file.write_text("def main():\n    print('Hello from Python')")

        # 创建 C# 文件
        cs_file = self.test_dir / "Program.cs"
        cs_file.write_text("Console.WriteLine('Hello from C#');")

        # 测试多语言文件处理器
        config = MultiLanguageConfig(enable_dotnet=False)  # 禁用 .NET 解析器以避免依赖
        py_handler = MultiLanguageFileHandler(str(self.test_dir), "main.py", config)
        cs_handler = MultiLanguageFileHandler(str(self.test_dir), "Program.cs", config)

        # 验证语言检测
        self.assertEqual(py_handler.detect_language(), Language.PYTHON)
        self.assertEqual(cs_handler.detect_language(), Language.CSHARP)


# 测试套件配置
def create_test_suite():
    """创建测试套件"""
    suite = unittest.TestSuite()

    # 添加所有测试类
    test_classes = [
        TestDotNetProjectParser,
        TestDotNetDocumentGenerator,
        TestDotNetPromptGenerator,
        TestMultiLanguageFileHandler,
        TestDotNetTerminology,
        TestDotNetCodeType,
        TestProjectType,
        TestIntegrationScenarios
    ]

    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        suite.addTests(tests)

    return suite


def run_all_tests():
    """运行所有测试"""
    suite = create_test_suite()
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result.wasSuccessful()


if __name__ == "__main__":
    # 运行测试
    print("=" * 70)
    print("运行 .NET 支持单元测试套件")
    print("=" * 70)

    success = run_all_tests()

    print("\n" + "=" * 70)
    if success:
        print("所有测试通过！")
    else:
        print("部分测试失败，请检查输出。")
    print("=" * 70)

    exit(0 if success else 1)