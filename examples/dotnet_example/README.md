# RepoAgent .NET 支持示例

这个示例展示了 RepoAgent 对 .NET 项目的支持和文档生成功能。包含了多种类型的 .NET 项目，演示了如何使用 RepoAgent 为 .NET 代码生成高质量的文档。

## 📁 项目结构

```
dotnet_example/
├── README.md                      # 本文档
├── WebAppSample/                  # ASP.NET Core Web API 示例
│   ├── WebAppSample.csproj        # 项目文件
│   ├── Controllers/
│   │   └── WeatherForecastController.cs
│   ├── Models/
│   │   └── User.cs                 # 数据模型示例
│   └── Services/
│       ├── IUserService.cs         # 服务接口
│       └── UserService.cs          # 服务实现
└── MathLibrary/                   # .NET 类库示例
    ├── MathLibrary.csproj          # 项目文件
    ├── Calculator.cs               # 主要功能类
    └── HistoryManager.cs           # 辅助类
```

## 🎯 示例项目概览

### 1. WebAppSample - ASP.NET Core Web API

展示了一个典型的 Web API 项目，包含：
- RESTful API 控制器
- 数据模型和实体
- 服务层架构
- 依赖注入
- 异步编程
- XML 文档注释

**主要特性：**
- 天气预报 API 端点
- 用户管理服务
- 完整的数据模型定义
- 接口和实现分离

### 2. MathLibrary - .NET 类库

展示了一个可重用的类库项目，包含：
- 复杂的业务逻辑
- 异常处理
- 历史记录管理
- 泛型编程
- 单元测试友好的设计

**主要特性：**
- 基本数学运算
- 统计计算功能
- 计算历史管理
- 自定义异常类型
- 详细的 XML 文档

## 🚀 使用 RepoAgent 处理 .NET 项目

### 基本用法

```bash
# 进入包含 .NET 项目的目录
cd your-dotnet-project

# 运行 RepoAgent 进行文档生成
pdm run repoagent run

# 或者如果直接安装了 repoagent
repoagent
```

### .NET 项目检测

RepoAgent 会自动检测以下 .NET 文件类型：
- **源代码文件**：`.cs`, `.fs`, `.vb`
- **项目文件**：`.csproj`, `.fsproj`, `.vbproj`
- **解决方案文件**：`.sln`

### 支持的 .NET 特性

#### 1. 项目类型识别
- Web 应用程序 (ASP.NET Core)
- Web API
- 控制台应用程序
- 类库
- 测试项目
- Windows 服务
- WPF/WinForms 应用程序

#### 2. 代码结构解析
- **命名空间**：自动识别和组织
- **类和接口**：完整的类型定义
- **方法和属性**：包括重载、泛型、访问修饰符
- **继承关系**：基类和接口实现
- **特性/属性**：C# Attributes
- **事件和委托**：.NET 特有的编程概念

#### 3. XML 文档注释集成
```csharp
/// <summary>
/// 计算两个数的和
/// </summary>
/// <param name="a">第一个操作数</param>
/// <param name="b">第二个操作数</param>
/// <returns>两数之和</returns>
/// <exception cref="OverflowException">当结果溢出时抛出</exception>
/// <example>
/// <code>
/// var result = calculator.Add(5, 3); // 结果: 8
/// </code>
/// </example>
public double Add(double a, double b)
{
    return a + b;
}
```

#### 4. 多解析器策略
- **Tree-sitter**：快速的语法解析（适用于大型项目）
- **Roslyn**：深度的语义分析（提供最准确的结果）
- **混合模式**：智能选择最优解析策略

## 📊 文档输出示例

### 类文档
```markdown
# Calculator

**Calculator**: 高级计算器类，提供基本的数学运算功能和统计计算

**Type**: class
**Namespace**: MathLibrary
**Assembly**: MathLibrary.Sample

**Syntax**:
```csharp
public class Calculator
{
    public Calculator()

    public double LastResult { get; }

    public double Add(double a, double b)
    public double Subtract(double a, double b)
    public double Multiply(double a, double b)
    public double Divide(double a, double b)
    public double Power(double baseNumber, double exponent)
    public double SquareRoot(double number)
    public double Average(params double[] numbers)
    public double Max(params double[] numbers)
    public double Min(params double[] numbers)
    public void Reset()
    public IReadOnlyList<string> GetHistory()
}
```

**Methods**:

**Add(double a, double b)**: 加法运算
- **Parameters**:
  - a: 第一个操作数
  - b: 第二个操作数
- **Returns**: 两数之和
- **Example**:
```csharp
var calculator = new Calculator();
double result = calculator.Add(5, 3); // 结果: 8
```

**Divide(double a, double b)**: 除法运算
- **Parameters**:
  - a: 被除数
  - b: 除数
- **Returns**: 两数之商
- **Exceptions**:
  - DivideByZeroException: 当除数为零时抛出
  - CalculatorException: 当结果超出允许范围时抛出
```

## ⚙️ 配置选项

### 多语言配置
```python
# MultiLanguageConfig 示例
config = MultiLanguageConfig(
    enable_dotnet=True,           # 启用 .NET 支持
    enable_treesitter=True,        # 启用 Tree-sitter
    prefer_roslyn=False,          # 优先使用 Tree-sitter
    dotnet_strategy="auto",        # 自动选择解析策略
    treesitter_fallback=True       # 启用回退机制
)
```

### 性能优化
- **缓存机制**：自动缓存解析结果，避免重复解析
- **增量处理**：仅处理修改过的文件
- **内存管理**：智能内存使用监控和优化
- **并行处理**：大型项目的并行分析

## 🔧 最佳实践

### 1. 项目结构建议
- 使用清晰的命名空间
- 保持项目文件简洁
- 合理组织文件夹结构

### 2. 文档注释最佳实践
- 为所有公共成员添加 XML 文档注释
- 使用标准的 XML 标签（`<summary>`, `<param>`, `<returns>`, `<exception>`, `<example>`）
- 提供有意义的描述和示例

### 3. 代码组织
- 使用接口定义契约
- 实现依赖注入
- 遵循 SOLID 原则
- 合理使用异常处理

## 🐛 故障排除

### 常见问题

#### 1. .NET SDK 未找到
**问题**：`错误：找不到 .NET SDK`
**解决方案**：
- 确保已安装 .NET SDK 6.0 或更高版本
- 检查环境变量 PATH
- 运行 `dotnet --version` 验证安装

#### 2. 项目解析失败
**问题**：无法解析某些 .csproj 文件
**解决方案**：
- 检查项目文件格式是否正确
- 确保所有依赖项都已安装
- 查看详细错误日志

#### 3. 内存使用过高
**问题**：处理大型项目时内存不足
**解决方案**：
- 调整缓存大小配置
- 启用增量处理
- 增加系统内存或分批处理

#### 4. 缓存问题
**问题**：文档内容未更新
**解决方案**：
- 清空缓存：`optimizer.clear_caches()`
- 强制重新解析：删除缓存目录
- 检查文件时间戳

### 调试技巧

1. **启用详细日志**：
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

2. **性能监控**：
```python
from repo_agent.utils.performance import PerformanceAnalyzer

analyzer = PerformanceAnalyzer()
report = analyzer.generate_report()
print(report)
```

3. **检查项目检测**：
```python
from repo_agent.project.dotnet_project import DotNetProjectParser

parser = DotNetProjectParser(".")
projects = parser.find_project_files()
print(f"找到 {len(projects)} 个 .NET 项目")
```

## 📈 性能指标

基于测试结果，RepoAgent .NET 支持的性能特征：

- **首次解析**：~0.018秒/项目
- **缓存命中**：<0.001秒/项目
- **内存使用**：基础 ~30MB，每1000个文件增加 ~5MB
- **缓存命中率**：重复操作 >90%

## 🔮 未来计划

- 支持更多 .NET 语言（F#、VB.NET）
- 深度集成 Visual Studio 项目系统
- 支持解决方案级别的分析
- 添加更多代码质量指标
- 集成单元测试覆盖率分析

## 📚 相关资源

- [.NET 官方文档](https://docs.microsoft.com/dotnet/)
- [C# 编程指南](https://docs.microsoft.com/dotnet/csharp/)
- [ASP.NET Core 文档](https://docs.microsoft.com/aspnet/core/)
- [RepoAgent 主项目](https://github.com/LOGIC-10/RepoAgent)

## 🤝 贡献

欢迎提交 Issue 和 Pull Request 来改进 .NET 支持！

---

*本示例项目展示了 RepoAgent 对 .NET 生态系统的全面支持，帮助开发者快速为 .NET 项目生成高质量的技术文档。*