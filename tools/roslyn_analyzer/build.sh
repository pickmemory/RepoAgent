#!/bin/bash
# 构建 Roslyn 分析器
# 用于 Linux/macOS 环境

echo "正在构建 Roslyn 分析器..."

# 检查 .NET SDK
if ! command -v dotnet &> /dev/null; then
    echo "错误：未找到 .NET SDK"
    echo "请安装 .NET 6.0 SDK 或更高版本"
    exit 1
fi

# 恢复包
echo "正在恢复 NuGet 包..."
dotnet restore
if [ $? -ne 0 ]; then
    echo "错误：包恢复失败"
    exit 1
fi

# 构建
echo "正在构建项目..."
dotnet build --configuration Release
if [ $? -ne 0 ]; then
    echo "错误：构建失败"
    exit 1
fi

# 发布为可执行文件
echo "正在发布可执行文件..."
dotnet publish --configuration Release --runtime linux-x64 --self-contained true -p:PublishSingleFile=true
if [ $? -ne 0 ]; then
    echo "警告：发布失败，但构建成功"
fi

echo "构建完成！"
echo "可执行文件位置：bin/Release/net6.0/RoslynAnalyzer"
echo "自包含发布位置：bin/Release/net6.0/linux-x64/publish/RoslynAnalyzer"