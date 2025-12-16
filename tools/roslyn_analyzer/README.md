# Roslyn 代码分析器

这是为 RepoAgent 项目开发的 Roslyn 代码分析器工具，提供对 .NET 代码的深度语义分析功能。

## 功能特性

- **深度语法分析**：使用 Microsoft.CodeAnalysis (Roslyn) 进行精确的代码解析
- **全面代码元素提取**：
  - 类、接口、结构体、枚举
  - 方法、属性、字段、事件
  - 委托和索引器
  - 命名空间和导入语句
- **.NET 特性识别**：
  - 特性 (Attributes)
  - LINQ 查询和方法调用
  - 异步方法 (async/await)
  - Lambda 表达式
  - 泛型约束
  - 局部函数
- **XML 文档注释提取**：支持提取方法的 XML 文档注释
- **JSON 输出格式**：结构化的 JSON 输出，便于 Python 端处理

## 构建和使用

### 前置条件

- .NET 6.0 SDK 或更高版本
- 对于解决方案分析：MSBuild Tools

### 构建

```bash
cd tools/roslyn_analyzer
dotnet build
```

### 使用方法

#### 分析单个文件

```bash
# 基本用法 - 输出到控制台
dotnet run -- --file "path/to/your/file.cs"

# 输出到文件
dotnet run -- --file "path/to/your/file.cs" --output "result.json"

# 启用详细输出
dotnet run -- --file "path/to/your/file.cs" --verbose
```

#### 示例输出

```json
{
  "filePath": "C:/code/example.cs",
  "analyzedAt": "2025-12-16T08:00:00Z",
  "language": "C#",
  "languageVersion": "C# 10.0+",
  "namespaces": [
    "MyApp.Services",
    "MyApp.Models"
  ],
  "imports": [
    {
      "name": "System",
      "alias": null,
      "isStatic": false
    },
    {
      "name": "System.Collections.Generic",
      "alias": null,
      "isStatic": false
    }
  ],
  "classes": [
    {
      "name": "UserService",
      "kind": "ClassDeclaration",
      "modifiers": ["public"],
      "baseType": "BaseService",
      "interfaces": [],
      "genericParameters": ["T"],
      "documentation": "/// <summary>\n/// 用户服务\n/// </summary>",
      "properties": [
        {
          "name": "UserCount",
          "type": "int",
          "modifiers": ["public"],
          "hasGet": true,
          "hasSet": false,
          "isExpressionBodied": true,
          "documentation": null
        }
      ],
      "fields": [],
      "methods": [
        {
          "name": "GetUserAsync",
          "returnType": "Task<User>",
          "modifiers": ["public", "async"],
          "parameters": [
            {
              "name": "id",
              "type": "int",
              "hasDefaultValue": false
            }
          ],
          "isAsync": true,
          "isExpressionBodied": false,
          "isGeneric": false,
          "documentation": null
        }
      ],
      "events": [],
      "indexers": []
    }
  ],
  "delegates": [],
  "enums": [],
  "dotNetFeatures": {
    "attributes": [],
    "linqQueries": [],
    "linqMethodCalls": [
      "users.Where(u => u.IsActive)"
    ],
    "asyncMethods": ["GetUserAsync"],
    "lambdaExpressions": ["u => u.IsActive"],
    "genericConstraints": [],
    "localFunctions": []
  }
}
```

## 与 RepoAgent 集成

Roslyn 分析器作为外部进程被 Python 端调用，通过以下方式集成：

1. **进程管理**：Python 端负责启动和管理分析器进程
2. **输入/输出**：通过命令行参数传递文件路径，接收 JSON 输出
3. **错误处理**：分析器会返回适当的退出码和错误信息
4. **性能优化**：支持批量处理和结果缓存

## 技术细节

### 支持的 C# 版本

- C# 1.0 到 C# 13.0
- 最新语言特性
- .NET Framework 和 .NET Core/5/6/7/8+

### 解析能力

- 完整的语法树分析
- 语义信息提取
- 符号解析（可扩展）
- 编译器级准确性

### 输出格式

- 标准 JSON 格式
- CamelCase 命名约定
- 空值省略
- 类型化数据结构

## 故障排除

### 常见问题

1. **编译错误**：确保已安装正确版本的 .NET SDK
2. **路径问题**：使用绝对路径分析文件
3. **编码问题**：确保源文件使用 UTF-8 编码
4. **大文件处理**：对于非常大的文件，可能需要增加内存限制

### 调试技巧

- 使用 `--verbose` 标志获取详细日志
- 检查文件的编码格式
- 验证 C# 语法是否正确
- 确保所有依赖项可用

## 扩展开发

### 添加新功能

1. 在 `Models.cs` 中定义新的数据模型
2. 在 `Program.cs` 的 `AnalyzeCSharpCode` 方法中添加提取逻辑
3. 更新 JSON 序列化选项（如需要）

### 自定义分析规则

可以扩展分析器以支持：
- 自定义代码度量
- 特定模式检测
- 代码质量评估
- 依赖关系分析

## 许可证

本项目遵循与 RepoAgent 主项目相同的许可证。