#!/usr/bin/env python
"""测试 .NET 文档生成提示"""

import sys
import os
sys.path.insert(0, '.')

# 设置临时的 API 密钥以避免验证错误
os.environ['OPENAI_API_KEY'] = 'test-key-for-configuration-testing'

try:
    from repo_agent.prompts.dotnet_prompts import (
        DotNetPromptGenerator,
        DotNetTerminology,
        DotNetCodeType,
        generate_dotnet_doc_prompt
    )
    from pathlib import Path

    print("[OK] .NET 提示模块导入成功")

    # 测试术语映射
    print("\n=== 测试术语映射 ===")
    terminology = DotNetTerminology()
    test_terms = ["函数", "类", "接口", "属性", "方法", "异步"]

    for term in test_terms:
        translated = terminology.translate_to_dotnet_terminology(f"这是一个{term}")
        print(f"  '{term}' -> '{translated}'")

    # 测试 C# 签名格式化
    print("\n=== 测试签名格式化 ===")
    generator = DotNetPromptGenerator()

    method_signature = {
        "modifiers": ["public", "async"],
        "return_type": "Task<string>",
        "name": "GetUserAsync",
        "parameters": [
            {"type": "int", "name": "userId"},
            {"type": "bool", "name": "includeDetails", "default": "false"}
        ],
        "generic_parameters": []
    }

    formatted_signature = generator.format_csharp_signature(method_signature)
    print(f"格式化签名:\n{formatted_signature}")

    # 测试模板获取
    print("\n=== 测试文档模板 ===")
    templates = [
        ("类模板", generator.templates.get_class_template),
        ("方法模板", generator.templates.get_method_template),
        ("接口模板", generator.templates.get_interface_template)
    ]

    for name, template_func in templates:
        template = template_func()
        print(f"\n{name}:")
        print(f"  长度: {len(template)} 字符")
        print(f"  包含占位符: {template.count('{')}")
        # 显示前两行
        lines = template.split('\n')[:2]
        for line in lines:
            print(f"  {line}")

    # 测试生成完整提示
    print("\n=== 测试生成完整提示 ===")
    sample_code = """
public class UserService : IUserService
{
    private readonly IRepository<User> _userRepository;

    public UserService(IRepository<User> userRepository)
    {
        _userRepository = userRepository ?? throw new ArgumentNullException(nameof(userRepository));
    }

    public async Task<User> GetUserAsync(int userId, bool includeDetails = false)
    {
        var user = await _userRepository.GetByIdAsync(userId);
        if (user == null) return null;

        if (includeDetails)
        {
            user.Profile = await GetProfileAsync(userId);
        }

        return user;
    }
}""".strip()

    prompt = generator.generate_documentation_prompt(
        code_name="UserService",
        code_type="class",
        code_content=sample_code,
        language="Chinese",
        project_context={
            "namespace": "MyApp.Services",
            "assembly": "MyApp.Core",
            "dependencies": ["Microsoft.Extensions.DependencyInjection", "System.Threading.Tasks"],
            "related_types": ["User", "IUserService", "IRepository<User>"]
        }
    )

    print(f"生成的提示长度: {len(prompt)} 字符")
    print(f"包含术语 'method': {prompt.count('method')} 次")
    print(f"包含术语 'property': {prompt.count('property')} 次")
    print(f"包含 'C#': {prompt.count('C#')} 次")

    # 显示提示的前几行
    print("\n提示预览:")
    for i, line in enumerate(prompt.split('\n')[:10]):
        print(f"  {line}")

    # 测试便捷函数
    print("\n=== 测试便捷函数 ===")
    quick_prompt = generate_dotnet_doc_prompt(
        code_name="CalculateSum",
        code_type="method",
        code_content="public int CalculateSum(int a, int b) => a + b;",
        language="English"
    )
    print(f"便捷函数生成成功: {len(quick_prompt)} 字符")

    print("\n所有测试完成！")

except ImportError as e:
    print(f"[ERROR] 导入错误: {e}")
    import traceback
    traceback.print_exc()
except Exception as e:
    print(f"[ERROR] 运行错误: {e}")
    import traceback
    traceback.print_exc()