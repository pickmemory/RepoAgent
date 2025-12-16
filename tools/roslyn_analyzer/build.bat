@echo off
REM 构建 Roslyn 分析器
REM 用于 Windows 环境

echo 正在构建 Roslyn 分析器...

REM 检查 .NET SDK
dotnet --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误：未找到 .NET SDK
    echo 请安装 .NET 6.0 SDK 或更高版本
    exit /b 1
)

REM 恢复包
echo 正在恢复 NuGet 包...
dotnet restore
if %errorlevel% neq 0 (
    echo 错误：包恢复失败
    exit /b 1
)

REM 构建
echo 正在构建项目...
dotnet build --configuration Release
if %errorlevel% neq 0 (
    echo 错误：构建失败
    exit /b 1
)

REM 发布为可执行文件
echo 正在发布可执行文件...
dotnet publish --configuration Release --runtime win-x64 --self-contained true -p:PublishSingleFile=true
if %errorlevel% neq 0 (
    echo 警告：发布失败，但构建成功
)

echo 构建完成！
echo 可执行文件位置：bin\Release\net6.0\RoslynAnalyzer.exe
echo 自包含发布位置：bin\Release\net6.0\win-x64\publish\RoslynAnalyzer.exe

pause