using System.Text.Json.Serialization;

namespace RoslynAnalyzer;

/// <summary>
/// 代码分析结果
/// </summary>
public class AnalysisResult
{
    [JsonPropertyName("filePath")]
    public string FilePath { get; set; } = "";

    [JsonPropertyName("analyzedAt")]
    public DateTime AnalyzedAt { get; set; }

    [JsonPropertyName("language")]
    public string Language { get; set; } = "C#";

    [JsonPropertyName("languageVersion")]
    public string LanguageVersion { get; set; } = "";

    [JsonPropertyName("namespaces")]
    public List<string> Namespaces { get; set; } = new();

    [JsonPropertyName("imports")]
    public List<ImportInfo> Imports { get; set; } = new();

    [JsonPropertyName("classes")]
    public List<ClassInfo> Classes { get; set; } = new();

    [JsonPropertyName("delegates")]
    public List<DelegateInfo> Delegates { get; set; } = new();

    [JsonPropertyName("enums")]
    public List<EnumInfo> Enums { get; set; } = new();

    [JsonPropertyName("dotNetFeatures")]
    public DotNetFeatures DotNetFeatures { get; set; } = new();
}

/// <summary>
/// 导入信息
/// </summary>
public class ImportInfo
{
    [JsonPropertyName("name")]
    public string Name { get; set; } = "";

    [JsonPropertyName("alias")]
    public string? Alias { get; set; }

    [JsonPropertyName("isStatic")]
    public bool IsStatic { get; set; }
}

/// <summary>
/// 类型信息（类、结构体、接口）
/// </summary>
public class ClassInfo
{
    [JsonPropertyName("name")]
    public string Name { get; set; } = "";

    [JsonPropertyName("kind")]
    public string Kind { get; set; } = ""; // Class, Struct, Interface, Record

    [JsonPropertyName("modifiers")]
    public List<string> Modifiers { get; set; } = new(); // public, private, static, abstract, etc.

    [JsonPropertyName("baseType")]
    public string? BaseType { get; set; }

    [JsonPropertyName("interfaces")]
    public List<string> Interfaces { get; set; } = new();

    [JsonPropertyName("genericParameters")]
    public List<string> GenericParameters { get; set; } = new();

    [JsonPropertyName("documentation")]
    public string? Documentation { get; set; }

    [JsonPropertyName("properties")]
    public List<PropertyInfo> Properties { get; set; } = new();

    [JsonPropertyName("fields")]
    public List<FieldInfo> Fields { get; set; } = new();

    [JsonPropertyName("methods")]
    public List<MethodInfo> Methods { get; set; } = new();

    [JsonPropertyName("events")]
    public List<EventInfo> Events { get; set; } = new();

    [JsonPropertyName("indexers")]
    public List<IndexerInfo> Indexers { get; set; } = new();
}

/// <summary>
/// 属性信息
/// </summary>
public class PropertyInfo
{
    [JsonPropertyName("name")]
    public string Name { get; set; } = "";

    [JsonPropertyName("type")]
    public string Type { get; set; } = "";

    [JsonPropertyName("modifiers")]
    public List<string> Modifiers { get; set; } = new();

    [JsonPropertyName("hasGet")]
    public bool HasGet { get; set; }

    [JsonPropertyName("hasSet")]
    public bool HasSet { get; set; }

    [JsonPropertyName("isExpressionBodied")]
    public bool IsExpressionBodied { get; set; }

    [JsonPropertyName("documentation")]
    public string? Documentation { get; set; }
}

/// <summary>
/// 字段信息
/// </summary>
public class FieldInfo
{
    [JsonPropertyName("name")]
    public string Name { get; set; } = "";

    [JsonPropertyName("type")]
    public string Type { get; set; } = "";

    [JsonPropertyName("modifiers")]
    public List<string> Modifiers { get; set; } = new();

    [JsonPropertyName("hasInitializer")]
    public bool HasInitializer { get; set; }

    [JsonPropertyName("documentation")]
    public string? Documentation { get; set; }
}

/// <summary>
/// 方法信息
/// </summary>
public class MethodInfo
{
    [JsonPropertyName("name")]
    public string Name { get; set; } = "";

    [JsonPropertyName("returnType")]
    public string ReturnType { get; set; } = "";

    [JsonPropertyName("modifiers")]
    public List<string> Modifiers { get; set; } = new();

    [JsonPropertyName("parameters")]
    public List<ParameterInfo> Parameters { get; set; } = new();

    [JsonPropertyName("isAsync")]
    public bool IsAsync { get; set; }

    [JsonPropertyName("isExpressionBodied")]
    public bool IsExpressionBodied { get; set; }

    [JsonPropertyName("isGeneric")]
    public bool IsGeneric { get; set; }

    [JsonPropertyName("documentation")]
    public string? Documentation { get; set; }
}

/// <summary>
/// 参数信息
/// </summary>
public class ParameterInfo
{
    [JsonPropertyName("name")]
    public string Name { get; set; } = "";

    [JsonPropertyName("type")]
    public string Type { get; set; } = "";

    [JsonPropertyName("hasDefaultValue")]
    public bool HasDefaultValue { get; set; }
}

/// <summary>
/// 委托信息
/// </summary>
public class DelegateInfo
{
    [JsonPropertyName("name")]
    public string Name { get; set; } = "";

    [JsonPropertyName("returnType")]
    public string ReturnType { get; set; } = "";

    [JsonPropertyName("parameters")]
    public List<ParameterInfo> Parameters { get; set; } = new();
}

/// <summary>
/// 枚举信息
/// </summary>
public class EnumInfo
{
    [JsonPropertyName("name")]
    public string Name { get; set; } = "";

    [JsonPropertyName("baseType")]
    public string? BaseType { get; set; }

    [JsonPropertyName("members")]
    public List<string> Members { get; set; } = new();
}

/// <summary>
/// 事件信息
/// </summary>
public class EventInfo
{
    [JsonPropertyName("name")]
    public string Name { get; set; } = "";

    [JsonPropertyName("type")]
    public string Type { get; set; } = "";

    [JsonPropertyName("modifiers")]
    public List<string> Modifiers { get; set; } = new();

    [JsonPropertyName("documentation")]
    public string? Documentation { get; set; }
}

/// <summary>
/// 索引器信息
/// </summary>
public class IndexerInfo
{
    [JsonPropertyName("type")]
    public string Type { get; set; } = "";

    [JsonPropertyName("modifiers")]
    public List<string> Modifiers { get; set; } = new();

    [JsonPropertyName("parameters")]
    public List<ParameterInfo> Parameters { get; set; } = new();

    [JsonPropertyName("hasGet")]
    public bool HasGet { get; set; }

    [JsonPropertyName("hasSet")]
    public bool HasSet { get; set; }

    [JsonPropertyName("documentation")]
    public string? Documentation { get; set; }
}

/// <summary>
/// .NET 特定特性
/// </summary>
public class DotNetFeatures
{
    [JsonPropertyName("attributes")]
    public List<string> Attributes { get; set; } = new();

    [JsonPropertyName("linqQueries")]
    public List<string> LinqQueries { get; set; } = new();

    [JsonPropertyName("linqMethodCalls")]
    public List<string> LinqMethodCalls { get; set; } = new();

    [JsonPropertyName("asyncMethods")]
    public List<string> AsyncMethods { get; set; } = new();

    [JsonPropertyName("lambdaExpressions")]
    public List<string> LambdaExpressions { get; set; } = new();

    [JsonPropertyName("genericConstraints")]
    public List<string> GenericConstraints { get; set; } = new();

    [JsonPropertyName("localFunctions")]
    public List<string> LocalFunctions { get; set; } = new();
}