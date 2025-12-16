# 任务分解文档 - RepoAgent .NET 支持

## Phase 1: 基础架构搭建

- [x] 1.1 创建语言抽象接口
  - 文件: repo_agent/language/__init__.py
  - 定义 Language 枚举和基础数据结构
  - 创建 ILanguageAnalyzer、ILanguageParser、ILanguageDocumentGenerator 接口
  - 目的: 建立多语言支持的抽象基础
  - _依赖: repo_agent/settings.py_
  - _需求: 1.1, 2.1_
  - _Prompt: 角色: Python 架构师，专注于接口设计和抽象 | 任务: 实现多语言支持的抽象接口系统，包括 Language 枚举和三个核心接口，遵循现有的 settings.py 模式 | 限制: 必须使用 Python 抽象基类，保持与现有代码风格一致，接口设计要考虑未来扩展性 | 成功标准: 所有接口正确定义，通过 mypy 类型检查，支持 .NET 和 Python 语言的抽象_

- [x] 1.2 扩展配置系统支持多语言
  - 文件: repo_agent/settings.py (修改现有)
  - 添加 LanguageSettings 类和语言相关配置选项
  - 更新 SettingsManager 以处理语言配置
  - 目的: 支持 .NET 语言配置和选择
  - _依赖: 现有的 SettingsManager 和 ProjectSettings_
  - _需求: 5.1, 5.2_
  - _Prompt: 角色: Python 开发者，精通 Pydantic 和配置管理 | 任务: 扩展现有的 settings.py 以支持多语言配置，添加 LanguageSettings 类并更新 SettingsManager，遵循现有的 Pydantic 模式 | 限制: 必须保持向后兼容性，不能破坏现有 Python 配置，使用 Pydantic 验证器 | 成功标准: 配置系统支持语言选择，验证规则正确，现有功能不受影响_

- [x] 1.3 创建语言检测器实现
  - 文件: repo_agent/language/detector.py
  - 实现 LanguageDetector 类
  - 添加文件扩展名映射和项目文件识别
  - 目的: 自动检测仓库中的编程语言
  - _依赖: 1.1 创建的接口_
  - _需求: 1.1, 1.2_
  - _Prompt: 角色: Python 开发者，专注于文件系统操作和模式匹配 | 任务: 实现 LanguageDetector 类，能够识别 .cs、.vb、.fs 文件和 .sln、.csproj 项目文件，使用 glob 模式匹配 | 限制: 必须高效处理大型仓库，遵守 .gitignore 规则，支持混合语言项目 | 成功标准: 正确识别 .NET 项目文件，处理混合语言仓库，性能满足要求_

## Phase 2: Tree-sitter 集成

- [x] 2.1 设置 Tree-sitter 环境和依赖
  - 文件: pyproject.toml (修改现有)
  - 添加 tree-sitter 和 tree-sitter-c-sharp 依赖
  - 创建 Tree-sitter 初始化脚本
  - 目的: 为 .NET 代码解析准备基础环境
  - _依赖: 项目依赖管理系统_
  - _需求: 2.1_
  - _Prompt: 角色: Python/DevOps 工程师，精通包管理和环境配置 | 任务: 更新项目依赖，添加 Tree-sitter Python 绑定和相关语法包，创建初始化脚本确保正确安装 | 限制: 必须保持与现有依赖兼容，考虑跨平台兼容性，提供离线安装选项 | 成功标准: Tree-sitter 正确安装，C# 语法包可用，初始化脚本可靠运行_

- [x] 2.2 实现 Tree-sitter 解析器包装器
  - 文件: repo_agent/parsers/tree_sitter_parser.py
  - 创建 TreeSitterWrapper 类
  - 实现 C# 语法树解析和节点查询
  - 目的: 提供轻量级的 .NET 代码解析能力
  - _依赖: 2.1 设置的 Tree-sitter 环境_
  - _需求: 2.1, 2.2_
  - _Prompt: 角色: Python 开发者，有解析器开发经验 | 任务: 实现 TreeSitterWrapper 类，能够解析 C# 文件并提取函数、类、命名空间等结构，使用 Tree-sitter 的查询 API | 限制: 必须处理 C# 1-13 的语法特性，优雅地处理解析错误，提供增量解析支持 | 成功标准: 正确解析 C# 代码结构，提取所有需要的 AST 节点，错误处理完善_

- [x] 2.3 实现 .NET 特定结构提取器
  - 文件: repo_agent/parsers/dotnet_extractor.py
  - 创建 DotNetStructureExtractor 类
  - 提取 .NET 特有结构（命名空间、类、接口、委托等）
  - 目的: 将 Tree-sitter AST 转换为内部数据结构
  - _依赖: 2.2 TreeSitterWrapper_
  - _需求: 2.2, 2.3_
  - _Prompt: 角色: .NET 开发者转 Python，精通 C# 语言特性 | 任务: 实现 DotNetStructureExtractor，从 Tree-sitter AST 中提取 .NET 特有概念如属性、事件、泛型、async/await 等 | 限制: 必须准确处理 C# 语言特性，保持与现有 Python AST 兼容的数据格式，支持 VB.NET 和 F# 扩展 | 成功标准: 准确提取所有 .NET 代码元素，数据结构一致，为文档生成做好准备_

## Phase 3: Roslyn 深度分析

- [x] 3.1 创建 Roslyn 分析器工具项目
  - 文件: tools/roslyn_analyzer/RoslynAnalyzer.csproj
  - 创建 .NET 控制台应用程序项目
  - 实现代码分析和 JSON 输出功能
  - 目的: 提供深度语义分析能力
  - _依赖: .NET SDK 6.0+
  - _需求: 2.1, 2.3_
  - _Prompt: 角色: .NET 开发者，精通 Roslyn API 和代码分析 | 任务: 创建 RoslynAnalyzer 控制台应用，使用 Roslyn API 进行深度语义分析，输出包含依赖关系、XML 文档、调用图等信息的 JSON | 限制: 必须支持 .NET Framework 和 .NET Core，处理大型项目时的内存管理，提供进度反馈 | 成功标准: 分析器能处理复杂的 .NET 解决方案，输出格式化的 JSON，包含所需的语义信息_

- [x] 3.2 实现 Roslyn 包装器
  - 文件: repo_agent/parsers/roslyn_wrapper.py
  - 创建 RoslynWrapper 类
  - 实现与 Roslyn 分析器的进程间通信
  - 目的: 从 Python 调用 Roslyn 分析功能
  - _依赖: 3.1 Roslyn 分析器_
  - _需求: 2.3_
  - _Prompt: 角色: Python 开发者，精通进程通信和外部工具集成 | 任务: 实现 RoslynWrapper，能够自动构建和执行 Roslyn 分析器，解析输出 JSON，处理进程生命周期和错误 | 限制: 必须优雅处理 .NET SDK 缺失情况，提供超时机制，支持并行执行多个文件 | 成功标准: 成功调用 Roslyn 分析器，正确解析输出，错误处理完善_

- [x] 3.3 实现混合解析策略
  - 文件: repo_agent/parsers/dotnet_parser.py
  - 创建 DotNetParser 类
  - 结合 Tree-sitter 和 Roslyn 的优势
  - 目的: 提供最佳的解析性能和质量
  - _依赖: 2.2 TreeSitterWrapper, 3.2 RoslynWrapper_
  - _需求: 2.2, 2.3_
  - _Prompt: 角色: 软件架构师，精通策略模式和性能优化 | 任务: 实现 DotNetParser，根据文件大小和复杂度选择最优解析策略，结合 Tree-sitter 的速度和 Roslyn 的深度 | 限制: 必须提供一致的输出格式，支持回退机制，性能满足大型项目需求 | 成功标准: 解析器智能选择策略，输出质量高，性能优化明显_

## Phase 4: 文档生成增强

- [ ] 4.1 扩展文档模板支持 .NET
  - 文件: repo_agent/prompts/dotnet_prompts.py
  - 创建 .NET 特定的文档生成提示
  - 定义 .NET 术语和约定映射
  - 目的: 生成符合 .NET 习惯的文档
  - _依赖: 现有的 prompt.py_
  - _需求: 4.1, 4.2_
  - _Prompt: 角色: 技术写作者，精通 .NET 文档约定 | 任务: 创建 .NET 特定的文档生成提示，包括 .NET 术语映射、XML 文档注释处理、API 文档格式 | 限制: 必须与现有提示系统兼容，支持中英文输出，遵循 .NET 官方文档风格 | 成功标准: 生成的文档符合 .NET 约定，术语正确，格式专业_

- [ ] 4.2 实现 .NET 文档生成器
  - 文件: repo_agent/documenters/dotnet_documenter.py
  - 创建 DotNetDocumentGenerator 类
  - 实现符合 .NET 约定的文档格式化
  - 目的: 生成高质量的 .NET 代码文档
  - _依赖: 4.1 .NET 提示模板_
  - _需求: 4.1, 4.2, 4.3_
  - _Prompt: 角色: .NET 技术文档专家，精通 API 文档生成 | 任务: 实现 DotNetDocumentGenerator，能够格式化 .NET 特有结构如泛型、委托、事件的文档，集成 XML 文档注释 | 限制: 必须保持与现有 Markdown 生成器兼容，支持代码示例格式化，处理重载方法 | 成功标准: 文档格式正确，包含所有必要信息，代码示例高亮正确_

- [ ] 4.3 扩展文件处理器支持 .NET
  - 文件: repo_agent/file_handler.py (修改现有)
  - 更新 generate_file_structure 支持多种解析器
  - 修改 get_functions_and_classes 处理 .NET 结构
  - 目的: 集成 .NET 支持到现有流程
  - _依赖: 3.3 DotNetParser_
  - _需求: 1.1, 2.1_
  - _Prompt: 角色: Python 开发者，精通现有代码库重构 | 任务: 修改 FileHandler 类，集成多语言支持，保持现有 Python 功能的同时添加 .NET 处理能力 | 限制: 必须保持向后兼容，不破坏现有功能，遵循现有代码模式 | 成功标准: Python 功能正常，.NET 文件正确处理，统一的工作流程_

## Phase 5: 项目结构理解

- [ ] 5.1 实现 .NET 项目解析器
  - 文件: repo_agent/project/dotnet_project.py
  - 创建 DotNetProjectParser 类
  - 解析 .sln 和 .csproj 文件
  - 目的: 理解 .NET 项目结构和依赖
  - _依赖: 现有的 ProjectManager_
  - _需求: 3.1, 3.2_
  - _Prompt: 角色: .NET 解决方案架构师，精通 MSBuild 和项目系统 | 任务: 实现 DotNetProjectParser，能够解析解决方案文件、项目引用、包依赖、配置映射等 | 限制: 必须支持旧版和新版项目格式，处理条件编译，理解多框架目标 | 成功标准: 正确解析项目结构，依赖关系准确，支持复杂解决方案_

- [ ] 5.2 更新项目结构生成
  - 文件: repo_agent/project_manager.py (修改现有)
  - 集成 .NET 项目解析到现有流程
  - 更新 get_project_structure 处理混合项目
  - 目的: 统一的项目结构展示
  - _依赖: 5.1 DotNetProjectParser_
  - _需求: 3.1, 3.2_
  - _Prompt: 角色: Python 开发者，熟悉现有项目管理系统 | 任务: 修改 ProjectManager 类，集成 .NET 项目解析，保持现有功能同时支持多语言项目 | 限制: 必须维护现有 API 兼容性，处理混合语言项目的层次结构 | 成功标准: 正确显示混合项目结构，层次关系清晰，信息完整_

## Phase 6: 集成测试和优化

- [ ] 6.1 创建单元测试套件
  - 文件: tests/test_dotnet_support.py
  - 测试所有 .NET 相关组件
  - 包含各种 .NET 代码示例
  - 目的: 确保 .NET 功能的可靠性
  - _依赖: 所有前面的组件_
  - _需求: 所有需求_
  - _Prompt: 角色: 测试工程师，精通 Python 测试框架和 .NET 代码 | 任务: 创建全面的单元测试，覆盖所有 .NET 支持组件，包含各种 C# 语法特性的测试用例 | 限制: 必须测试成功和失败场景，使用模拟对象隔离依赖，保持测试性能 | 成功标准: 测试覆盖率高，所有边界情况测试，CI/CD 集成成功_

- [ ] 6.2 性能优化和内存管理
  - 文件: repo_agent/utils/performance.py
  - 实现缓存和增量处理
  - 优化大型项目处理性能
  - 目的: 确保良好的性能表现
  - _依赖: 所有核心组件_
  - _需求: 非功能性需求_
  - _Prompt: 角色: 性能优化专家，精通 Python 性能调优 | 任务: 实现性能优化策略，包括解析结果缓存、增量处理、内存使用优化 | 限制: 必须保持功能完整性，提供性能监控，支持配置调优 | 成功标准: 大型项目处理时间合理，内存使用可控，有明确的性能指标_

- [ ] 6.3 创建示例和文档
  - 文件: examples/dotnet_example/README.md
  - 创建 .NET 示例项目
  - 编写使用指南和最佳实践
  - 目的: 帮助用户使用 .NET 功能
  - _依赖: 完整的功能实现_
  - _需求: 用户体验_
  - _Prompt: 角色: 技术写作专家，精通开发者文档 | 任务: 创建完整的 .NET 示例项目，包含各种场景的使用指南，编写清晰的文档 | 限制: 必须覆盖常见使用场景，提供故障排除指南，包含实际代码示例 | 成功标准: 示例项目可直接运行，文档清晰易懂，用户能够快速上手_

## Phase 7: 最终集成和发布

- [ ] 7.1 端到端测试
  - 文件: tests/test_e2e_dotnet.py
  - 使用真实 .NET 开源项目测试
  - 验证完整工作流程
  - 目的: 确保生产环境可用性
  - _依赖: 所有功能组件_
  - _需求: 所有需求_
  - _Prompt: 角色: QA 工程师，精通端到端测试 | 任务: 使用真实的 .NET 开源项目进行端到端测试，验证从扫描到文档生成的完整流程 | 限制: 必须使用多样化的大型项目，测试各种边界情况，验证文档质量 | 成功标准: 真实项目测试通过，生成的文档质量高，性能满足要求_

- [ ] 7.2 最终代码审查和清理
  - 文件: 所有修改的文件
  - 代码质量检查和优化
  - 文档更新和注释完善
  - 目的: 确保代码质量和可维护性
  - _依赖: 所有实现_
  - _需求: 代码质量标准_
  - _Prompt: 角色: 高级开发工程师，精通代码审查 | 任务: 进行全面的代码审查，确保代码质量、性能和可维护性，完善文档和注释 | 限制: 必须遵循项目编码规范，保持向后兼容，处理所有审查意见 | 成功标准: 代码质量达标，文档完整，无明显技术债务_