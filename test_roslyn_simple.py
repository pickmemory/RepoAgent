#!/usr/bin/env python
"""简化的 Roslyn 包装器测试"""

import sys
import os
sys.path.insert(0, '.')

# 设置临时的 API 密钥以避免验证错误
os.environ['OPENAI_API_KEY'] = 'test-key-for-configuration-testing'

try:
    from repo_agent.parsers.roslyn_wrapper import RoslynWrapper
    from pathlib import Path

    print("[OK] Roslyn 包装器模块导入成功")

    # 创建包装器实例
    wrapper = RoslynWrapper()
    print(f"[OK] 分析器路径: {wrapper.analyzer_path}")

    # 使用内置的测试文件
    test_file = Path("tools/roslyn_analyzer/test.cs")
    if test_file.exists():
        print(f"\n测试文件: {test_file}")

        # 输出到文件
        output_file = wrapper.analyze_file_to_json(
            test_file,
            output_path="roslyn_test_result.json",
            verbose=True
        )
        print(f"[OK] 分析结果已保存到: {output_file}")

        # 读取并显示部分内容
        if output_file.exists():
            size = output_file.stat().st_size
            print(f"文件大小: {size} 字节")

            # 读取前10行
            with open(output_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()[:10]
                print("\n文件内容预览:")
                for line in lines:
                    print(f"  {line.rstrip()}")

            print(f"\n完整 JSON 文件位置: {output_file.absolute()}")
    else:
        print(f"[ERROR] 测试文件不存在: {test_file}")

except Exception as e:
    print(f"[ERROR] {e}")
    import traceback
    traceback.print_exc()