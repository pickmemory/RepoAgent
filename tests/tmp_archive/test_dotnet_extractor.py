#!/usr/bin/env python
"""测试 .NET 结构提取器"""

import sys
import os
sys.path.insert(0, '.')

# 设置临时的 API 密钥以避免验证错误
os.environ['OPENAI_API_KEY'] = 'test-key-for-configuration-testing'

try:
    from repo_agent.parsers.dotnet_extractor import DotNetStructureExtractor
    from pathlib import Path

    print("[OK] .NET 结构提取器模块导入成功")

    # 创建测试用的 C# 代码
    test_csharp_code = '''
using System;
using System.Collections.Generic;
using System.Threading.Tasks;

namespace MyNamespace.SubNamespace
{
    /// <summary>
    /// 示例类
    /// </summary>
    public class Calculator
    {
        private List<string> _history = new List<string>();

        /// <summary>
        /// 构造函数
        /// </summary>
        public Calculator()
        {
        }

        /// <summary>
        /// 加法方法
        /// </summary>
        /// <param name="x">第一个数</param>
        /// <param name="y">第二个数</param>
        /// <returns>和</returns>
        public int Add(int x, int y)
        {
            return x + y;
        }

        /// <summary>
        /// 异步加法方法
        /// </summary>
        public async Task<int> AddAsync(int x, int y)
        {
            await Task.Delay(100);
            return x + y;
        }

        /// <summary>
        /// 只读属性
        /// </summary>
        public int Count => _history.Count;

        /// <summary>
        /// 索引器
        /// </summary>
        public int this[int index]
        {
            get { return _history[index]; }
            set { _history[index] = value; }
        }

        /// <summary>
        /// 静态方法
        /// </summary>
        public static int Multiply(int x, int y)
        {
            return x * y;
        }

        /// <summary>
        /// 私有方法
        /// </summary>
        private void LogOperation(string operation)
        {
            Console.WriteLine(operation);
        }

        /// <summary>
        /// LINQ 查询
        /// </summary>
        public List<string> GetRecentOperations()
        {
            return _history.Take(10).ToList();
        }
    }

    /// <summary>
    /// 示例接口
    /// </summary>
    public interface ICalculator
    {
        int Add(int x, int y);
        Task<int> AddAsync(int x, int y);
    }

    /// <summary>
    /// 示例结构体
    /// </summary>
    public struct Point
    {
        public int X { get; set; }
        public int Y { get; set; }

        public Point(int x, int y)
        {
            X = x;
            Y = y;
        }
    }

    /// <summary>
    /// 示例枚举
    /// </summary>
    public enum OperationType
    {
        Add,
        Subtract,
        Multiply,
        Divide
    }

    /// <summary>
    /// 示例委托
    /// </summary>
    public delegate int OperationDelegate(int x, int y);

    /// <summary>
    /// 自定义特性
    /// </summary>
    [AttributeUsage(AttributeTargets.Class)]
    public class DocumentationAttribute : Attribute
    {
        public string Description { get; set; }

        public DocumentationAttribute(string description)
        {
            Description = description;
        }
    }

    [Documentation("这是一个示例类")]
    public class DocumentedClass
    {
    }
'''

    # 创建提取器
    extractor = DotNetStructureExtractor()

    # 提取结构
    print("\n=== 提取 .NET 结构 ===")
    structure = extractor.extract_from_source(test_csharp_code, Path("test.cs"))

    print(f"命名空间 ({len(structure.namespaces)}):")
    for ns in structure.namespaces:
        print(f"  - {ns}")

    print(f"\n函数/方法 ({len(structure.functions)}):")
    for func in structure.functions:
        func_type = func.language_specific.get("type", "method")
        print(f"  - {func.name} ({func_type})")
        print(f"    类型: {func.return_type}, 异步: {func.is_async}, 访问级别: {func.access_level}")
        print(f"    参数: {[p['name'] for p in func.parameters]}")

    print(f"\n类/接口/结构体 ({len(structure.classes)}):")
    for cls in structure.classes:
        cls_type = "接口" if cls.is_interface else ("结构体" if cls.language_specific.get("is_struct") else "类")
        print(f"  - {cls.name} ({cls_type})")
        print(f"    访问级别: {cls.access_level}, 抽象: {cls.is_abstract}")
        if cls.base_classes:
            print(f"    基类: {', '.join(cls.base_classes)}")
        if cls.language_specific:
            extras = []
            if cls.language_specific.get("is_static"):
                extras.append("静态")
            if cls.language_specific.get("is_sealed"):
                extras.append("密封")
            if cls.language_specific.get("is_struct"):
                extras.append("结构体")
            if cls.language_specific.get("is_enum"):
                extras.append("枚举")
            if extras:
                print(f"    特殊: {', '.join(extras)}")

    print(f"\n导入语句 ({len(structure.imports)}):")
    for imp in structure.imports:
        print(f"  - {imp.module}")
        if imp.alias:
            print(f"    别名: {imp.alias}")

    # 测试 .NET 特有特性提取
    print("\n=== .NET 特有特性 ===")
    features = extractor.extract_dotnet_specific_features(test_csharp_code)

    print(f"特性数量: {len(features['attributes'])}")
    print(f"事件数量: {len(features['events'])}")
    print(f"属性数量: {len(features['properties'])}")
    print(f"索引器数量: {len(features['indexers'])}")
    print(f"泛型数量: {len(features['generics'])}")
    print(f"LINQ查询数量: {len(features['linq_queries'])}")
    print(f"异步方法数量: {len(features['async_methods'])}")

    # 显示一些具体内容
    if features['attributes']:
        print(f"\n特性示例:")
        for attr in features['attributes'][:3]:
            print(f"  - {attr['raw']}")

    if features['events']:
        print(f"\n事件示例:")
        for event in features['events']:
            print(f"  - {event['name']}: {event['type']}")

    print("\n所有测试完成！")

except ImportError as e:
    print(f"[ERROR] 导入错误: {e}")
    import traceback
    traceback.print_exc()
except Exception as e:
    print(f"[ERROR] 运行错误: {e}")
    import traceback
    traceback.print_exc()