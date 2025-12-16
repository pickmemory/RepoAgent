using System.CommandLine;
using Microsoft.CodeAnalysis;
using Microsoft.CodeAnalysis.CSharp;
using Microsoft.CodeAnalysis.CSharp.Syntax;
using Microsoft.Extensions.Logging;
using System.Text.Json;
using System.Text.Json.Serialization;

namespace RoslynAnalyzer;

/// <summary>
/// Roslyn 代码分析器 - 为 RepoAgent 提供深度语义分析
/// </summary>
class Program
{
    private static readonly ILogger<Program> logger =
        LoggerFactory.Create(builder => builder.AddConsole()).CreateLogger<Program>();

    static async Task<int> Main(string[] args)
    {
        try
        {
            var rootCommand = CreateRootCommand();
            return await rootCommand.InvokeAsync(args);
        }
        catch (Exception ex)
        {
            logger.LogError(ex, "程序执行失败");
            return 1;
        }
    }

    private static RootCommand CreateRootCommand()
    {
        var fileOption = new Option<FileInfo?>(
            name: "--file",
            description: "要分析的 C# 文件路径")
        {
            IsRequired = true
        };

        var outputOption = new Option<string?>(
            name: "--output",
            description: "输出 JSON 文件路径 (默认输出到控制台)",
            getDefaultValue: () => null);

        var verboseOption = new Option<bool>(
            name: "--verbose",
            description: "启用详细输出",
            getDefaultValue: () => false);

        var rootCommand = new RootCommand("Roslyn 代码分析器 - 为 RepoAgent 提供深度语义分析")
        {
            fileOption,
            outputOption,
            verboseOption
        };

        rootCommand.SetHandler(async (file, output, verbose) =>
        {
            await AnalyzeFile(file!, output, verbose);
        }, fileOption, outputOption, verboseOption);

        return rootCommand;
    }

    /// <summary>
    /// 分析单个 C# 文件
    /// </summary>
    private static async Task AnalyzeFile(FileInfo file, string? output, bool verbose)
    {
        logger.LogInformation("开始分析文件: {FilePath}", file.FullName);

        try
        {
            // 读取源代码
            var sourceCode = await File.ReadAllTextAsync(file.FullName);

            // 创建分析结果
            var analysisResult = await AnalyzeCSharpCode(sourceCode, file.FullName, verbose);

            // 序列化为 JSON
            var jsonOptions = new JsonSerializerOptions
            {
                WriteIndented = true,
                PropertyNamingPolicy = JsonNamingPolicy.CamelCase,
                DefaultIgnoreCondition = JsonIgnoreCondition.WhenWritingNull
            };

            var json = JsonSerializer.Serialize(analysisResult, jsonOptions);

            // 输出结果
            if (!string.IsNullOrEmpty(output))
            {
                await File.WriteAllTextAsync(output, json);
                logger.LogInformation("分析结果已保存到: {OutputPath}", output);
            }
            else
            {
                Console.WriteLine(json);
            }

            logger.LogInformation("分析完成 - 发现 {ClassCount} 个类, {MethodCount} 个方法",
                analysisResult.Classes.Count,
                analysisResult.Classes.Sum(c => c.Methods.Count));
        }
        catch (Exception ex)
        {
            logger.LogError(ex, "分析文件失败: {FilePath}", file.FullName);
            throw;
        }
    }

    /// <summary>
    /// 使用 Roslyn 分析 C# 代码
    /// </summary>
    private static async Task<AnalysisResult> AnalyzeCSharpCode(string sourceCode, string filePath, bool verbose)
    {
        // 解析源代码
        var tree = CSharpSyntaxTree.ParseText(sourceCode, CSharpParseOptions.Default, filePath);
        var root = await tree.GetRootAsync();

        // 创建分析结果
        var result = new AnalysisResult
        {
            FilePath = filePath,
            AnalyzedAt = DateTime.UtcNow,
            Language = "C#",
            LanguageVersion = "C# 10.0+" // 简化版本检测
        };

        // 提取 using 语句
        result.Imports = root
            .DescendantNodes()
            .OfType<UsingDirectiveSyntax>()
            .Select(u => new ImportInfo
            {
                Name = u.Name?.ToString() ?? "",
                Alias = u.Alias?.ToString(),
                IsStatic = u.StaticKeyword.IsKind(SyntaxKind.StaticKeyword)
            })
            .Where(i => !string.IsNullOrEmpty(i.Name))
            .ToList();

        // 提取命名空间
        var namespaces = root
            .DescendantNodes()
            .OfType<NamespaceDeclarationSyntax>()
            .ToList();

        result.Namespaces = namespaces
            .Select(ns => ns.Name?.ToString() ?? "")
            .Where(name => !string.IsNullOrEmpty(name))
            .Distinct()
            .ToList();

        // 提取类、接口、结构体等
        var typeDeclarations = root
            .DescendantNodes()
            .OfType<TypeDeclarationSyntax>()
            .ToList();

        foreach (var typeDecl in typeDeclarations)
        {
            var classInfo = ExtractClassInfo(typeDecl);
            if (classInfo != null)
            {
                result.Classes.Add(classInfo);
            }
        }

        // 提取委托声明
        var delegateDeclarations = root
            .DescendantNodes()
            .OfType<DelegateDeclarationSyntax>()
            .Select(d => new DelegateInfo
            {
                Name = d.Identifier.ValueText,
                ReturnType = d.ReturnType.ToString(),
                Parameters = d.ParameterList.Parameters.Select(p => new ParameterInfo
                {
                    Name = p.Identifier.ValueText,
                    Type = p.Type?.ToString() ?? ""
                }).ToList()
            })
            .ToList();

        result.Delegates = delegateDeclarations;

        // 提析枚举声明
        var enumDeclarations = root
            .DescendantNodes()
            .OfType<EnumDeclarationSyntax>()
            .Select(e => new EnumInfo
            {
                Name = e.Identifier.ValueText,
                Members = e.Members.Select(m => m.Identifier.ValueText).ToList(),
                BaseType = e.BaseList?.Types.FirstOrDefault()?.ToString()
            })
            .ToList();

        result.Enums = enumDeclarations;

        // 提取 .NET 特定特性
        result.DotNetFeatures = ExtractDotNetFeatures(root);

        if (verbose)
        {
            logger.LogDebug("提取完成: 命名空间 {NamespaceCount}, 类型 {TypeCount}, 导入 {ImportCount}",
                result.Namespaces.Count, result.Classes.Count, result.Imports.Count);
        }

        return result;
    }

    /// <summary>
    /// 提取类/结构体/接口信息
    /// </summary>
    private static ClassInfo? ExtractClassInfo(TypeDeclarationSyntax typeDecl)
    {
        var name = typeDecl.Identifier.ValueText;
        if (string.IsNullOrEmpty(name))
            return null;

        var classInfo = new ClassInfo
        {
            Name = name,
            Kind = typeDecl.Kind().ToString(),
            Modifiers = typeDecl.Modifiers.Select(m => m.ValueText).ToList(),
            BaseType = typeDecl.BaseList?.Types.FirstOrDefault()?.ToString(),
            Interfaces = typeDecl.BaseList?.Types.Skip(1).Select(t => t.ToString()).ToList() ?? new List<string>(),
            Documentation = ExtractDocumentation(typeDecl.GetLeadingTrivia())
        };

        // 提取泛型参数
        if (typeDecl.TypeParameterList != null)
        {
            classInfo.GenericParameters = typeDecl.TypeParameterList.Parameters
                .Select(p => p.Identifier.ValueText)
                .ToList();
        }

        // 提取属性
        var properties = typeDecl.Members
            .OfType<PropertyDeclarationSyntax>()
            .Select(p => new PropertyInfo
            {
                Name = p.Identifier.ValueText,
                Type = p.Type.ToString(),
                Modifiers = p.Modifiers.Select(m => m.ValueText).ToList(),
                HasGet = p.AccessorList?.Accessors.Any(a => a.IsKind(SyntaxKind.GetAccessorDeclaration)) ?? false,
                HasSet = p.AccessorList?.Accessors.Any(a => a.IsKind(SyntaxKind.SetAccessorDeclaration)) ?? false,
                IsExpressionBodied = p.ExpressionBody != null,
                Documentation = ExtractDocumentation(p.GetLeadingTrivia())
            })
            .ToList();

        classInfo.Properties = properties;

        // 提取字段
        var fields = typeDecl.Members
            .OfType<FieldDeclarationSyntax>()
            .SelectMany(f => f.Declaration.Variables.Select(v => new FieldInfo
            {
                Name = v.Identifier.ValueText,
                Type = f.Declaration.Type.ToString(),
                Modifiers = f.Modifiers.Select(m => m.ValueText).ToList(),
                HasInitializer = v.Initializer != null,
                Documentation = ExtractDocumentation(f.GetLeadingTrivia())
            }))
            .ToList();

        classInfo.Fields = fields;

        // 提取方法
        var methods = typeDecl.Members
            .OfType<MethodDeclarationSyntax>()
            .Select(m => new MethodInfo
            {
                Name = m.Identifier.ValueText,
                ReturnType = m.ReturnType.ToString(),
                Modifiers = m.Modifiers.Select(m => m.ValueText).ToList(),
                Parameters = m.ParameterList.Parameters.Select(p => new ParameterInfo
                {
                    Name = p.Identifier.ValueText,
                    Type = p.Type?.ToString() ?? "",
                    HasDefaultValue = p.Default != null
                }).ToList(),
                IsAsync = m.Modifiers.Any(m => m.IsKind(SyntaxKind.AsyncKeyword)),
                IsExpressionBodied = m.ExpressionBody != null,
                IsGeneric = m.TypeParameterList != null,
                Documentation = ExtractDocumentation(m.GetLeadingTrivia())
            })
            .ToList();

        classInfo.Methods = methods;

        // 提取事件
        var events = typeDecl.Members
            .OfType<EventDeclarationSyntax>()
            .Select(e => new EventInfo
            {
                Name = e.Identifier.ValueText,
                Type = e.Type.ToString(),
                Modifiers = e.Modifiers.Select(m => m.ValueText).ToList(),
                Documentation = ExtractDocumentation(e.GetLeadingTrivia())
            })
            .ToList();

        classInfo.Events = events;

        // 提取索引器
        var indexers = typeDecl.Members
            .OfType<IndexerDeclarationSyntax>()
            .Select(i => new IndexerInfo
            {
                Type = i.Type.ToString(),
                Modifiers = i.Modifiers.Select(m => m.ValueText).ToList(),
                Parameters = i.ParameterList.Parameters.Select(p => new ParameterInfo
                {
                    Name = p.Identifier.ValueText,
                    Type = p.Type?.ToString() ?? "",
                    HasDefaultValue = p.Default != null
                }).ToList(),
                HasGet = i.AccessorList?.Accessors.Any(a => a.IsKind(SyntaxKind.GetAccessorDeclaration)) ?? false,
                HasSet = i.AccessorList?.Accessors.Any(a => a.IsKind(SyntaxKind.SetAccessorDeclaration)) ?? false,
                Documentation = ExtractDocumentation(i.GetLeadingTrivia())
            })
            .ToList();

        classInfo.Indexers = indexers;

        return classInfo;
    }

    /// <summary>
    /// 提取 XML 文档注释
    /// </summary>
    private static string? ExtractDocumentation(SyntaxTriviaList trivia)
    {
        var xmlComment = trivia
            .Where(t => t.IsKind(SyntaxKind.SingleLineDocumentationCommentTrivia) ||
                       t.IsKind(SyntaxKind.MultiLineDocumentationCommentTrivia))
            .FirstOrDefault();

        if (xmlComment.IsKind(SyntaxKind.None))
            return null;

        // 简化的 XML 提取，实际项目中可以使用更复杂的解析
        return xmlComment.ToString();
    }

    /// <summary>
    /// 提取 .NET 特定特性
    /// </summary>
    private static DotNetFeatures ExtractDotNetFeatures(SyntaxNode root)
    {
        var features = new DotNetFeatures();

        // 提取特性
        features.Attributes = root
            .DescendantNodes()
            .OfType<AttributeSyntax>()
            .Select(a => a.ToString())
            .ToList();

        // 提取 LINQ 查询表达式
        features.LinqQueries = root
            .DescendantNodes()
            .OfType<QueryExpressionSyntax>()
            .Select(q => q.ToString())
            .ToList();

        // 提取 LINQ 方法调用
        var linqMethods = new[] { "Where", "Select", "OrderBy", "GroupBy", "Join", "SelectMany", "FirstOrDefault", "ToList", "ToArray" };
        features.LinqMethodCalls = root
            .DescendantNodes()
            .OfType<InvocationExpressionSyntax>()
            .Where(ie => linqMethods.Any(method =>
                ie.Expression is MemberAccessExpressionSyntax maes &&
                maes.Name.Identifier.ValueText == method))
            .Select(ie => ie.ToString())
            .ToList();

        // 提取异步方法
        features.AsyncMethods = root
            .DescendantNodes()
            .OfType<MethodDeclarationSyntax>()
            .Where(m => m.Modifiers.Any(mod => mod.IsKind(SyntaxKind.AsyncKeyword)))
            .Select(m => m.Identifier.ValueText)
            .ToList();

        // 提取 lambda 表达式
        features.LambdaExpressions = root
            .DescendantNodes()
            .OfType<ParenthesizedLambdaExpressionSyntax>()
            .Select(l => l.ToString())
            .Concat(
                root.DescendantNodes()
                    .OfType<SimpleLambdaExpressionSyntax>()
                    .Select(l => l.ToString())
            )
            .ToList();

        // 提取泛型约束
        features.GenericConstraints = root
            .DescendantNodes()
            .OfType<TypeParameterConstraintClauseSyntax>()
            .Select(c => c.ToString())
            .ToList();

        // 提取局部函数
        features.LocalFunctions = root
            .DescendantNodes()
            .OfType<LocalFunctionStatementSyntax>()
            .Select(lf => lf.Identifier.ValueText)
            .ToList();

        return features;
    }
}