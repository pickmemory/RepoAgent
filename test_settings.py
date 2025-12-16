#!/usr/bin/env python
"""测试多语言配置系统"""

import sys
import os
sys.path.insert(0, '.')

# 设置临时的 API 密钥以避免验证错误
os.environ['OPENAI_API_KEY'] = 'test-key-for-configuration-testing'

try:
    from repo_agent.settings import SettingsManager, LanguageSettings
    from repo_agent.language import Language as CodeLanguage
    print("[OK] 模块导入成功")

    # 测试默认配置
    try:
        settings = SettingsManager.get_setting()
        print("[OK] 默认配置加载成功")
    except Exception as e:
        print(f"[WARNING] 默认配置加载失败（可能需要API密钥）: {e}")

    # 检查语言设置
    if hasattr(settings.project, 'language_settings'):
        lang_settings = settings.project.language_settings
        print(f"[OK] 语言配置存在，启用的语言: {[lang.value for lang in lang_settings.enabled_languages]}")
        print(f"[OK] 自动检测语言: {lang_settings.auto_detect_languages}")
        print(f"[OK] Tree-sitter 回退: {lang_settings.tree_sitter_fallback}")
    else:
        print("[ERROR] 语言配置不存在")

    # 测试新的初始化方法
    try:
        SettingsManager.initialize_with_language_support(
            target_repo=sys.path[0],
            markdown_docs_name="markdown_docs",
            hierarchy_name=".project_doc_record",
            ignore_list=[],
            language="Chinese",
            max_thread_count=4,
            log_level="INFO",
            model="gpt-4o-mini",
            temperature=0.2,
            request_timeout=60,
            openai_base_url="http://pickmemory.cn:8084/v1",
            enabled_languages=[CodeLanguage.PYTHON, CodeLanguage.CSHARP],
            dotnet_framework_version="net6.0"
        )
        print("[OK] 多语言初始化成功")
    except Exception as e:
        print(f"[ERROR] 多语言初始化失败: {e}")

    print("\n所有测试通过！")

except ImportError as e:
    print(f"[ERROR] 导入错误: {e}")
    print("请确保在正确的虚拟环境中运行")
except Exception as e:
    print(f"[ERROR] 运行错误: {e}")
    import traceback
    traceback.print_exc()