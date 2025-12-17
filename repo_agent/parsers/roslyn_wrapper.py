"""
Roslyn 分析器包装器 - 从 Python 调用 .NET Roslyn 分析器
"""

import os
import sys
import json
import subprocess
import tempfile
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass

from repo_agent.log import logger


@dataclass
class RoslynAnalysisResult:
    """Roslyn 分析结果的数据类"""
    file_path: str
    analyzed_at: str
    language: str
    language_version: str
    namespaces: List[str]
    imports: List[Dict[str, Any]]
    classes: List[Dict[str, Any]]
    delegates: List[Dict[str, Any]]
    enums: List[Dict[str, Any]]
    dotnet_features: Dict[str, List[Any]]

    @classmethod
    def from_json(cls, json_data: Dict[str, Any]) -> 'RoslynAnalysisResult':
        """从 JSON 数据创建结果对象"""
        return cls(
            file_path=json_data.get('filePath', ''),
            analyzed_at=json_data.get('analyzedAt', ''),
            language=json_data.get('language', ''),
            language_version=json_data.get('languageVersion', ''),
            namespaces=json_data.get('namespaces', []),
            imports=json_data.get('imports', []),
            classes=json_data.get('classes', []),
            delegates=json_data.get('delegates', []),
            enums=json_data.get('enums', []),
            dotnet_features=json_data.get('dotNetFeatures', {})
        )


class RoslynWrapper:
    """Roslyn 分析器的 Python 包装器"""

    def __init__(self, analyzer_path: Optional[Union[str, Path]] = None):
        """
        初始化 Roslyn 包装器

        Args:
            analyzer_path: RoslynAnalyzer.exe 的路径，如果为 None 则自动查找
        """
        self.analyzer_path = self._find_analyzer(analyzer_path)
        self.timeout = 30  # 默认超时时间（秒）
        self._verify_analyzer()

    def _find_analyzer(self, analyzer_path: Optional[Union[str, Path]]) -> Path:
        """查找 RoslynAnalyzer.exe 的路径"""
        if analyzer_path:
            path = Path(analyzer_path)
            if path.exists():
                return path.resolve()
            logger.warning(f"指定的分析器路径不存在: {analyzer_path}")

        # 自动查找路径
        repo_root = Path(__file__).parent.parent.parent
        search_paths = [
            repo_root / "tools" / "roslyn_analyzer" / "bin" / "Debug" / "net8.0" / "RoslynAnalyzer.exe",
            repo_root / "tools" / "roslyn_analyzer" / "bin" / "Release" / "net8.0" / "RoslynAnalyzer.exe",
            repo_root / "tools" / "roslyn_analyzer" / "RoslynAnalyzer.exe",
        ]

        for path in search_paths:
            if path.exists():
                logger.debug(f"找到 Roslyn 分析器: {path}")
                return path.resolve()

        # 如果找不到，尝试在 PATH 中查找
        analyzer_in_path = shutil.which("RoslynAnalyzer")
        if analyzer_in_path:
            return Path(analyzer_in_path)

        raise FileNotFoundError(
            "找不到 RoslynAnalyzer.exe。请确保已构建 Roslyn 分析器项目。\n"
            f"搜索路径: {search_paths}"
        )

    def _verify_analyzer(self):
        """验证分析器是否可用"""
        try:
            result = subprocess.run(
                [str(self.analyzer_path), "--help"],
                capture_output=True,
                text=True,
                timeout=5,
                encoding='utf-8',
                errors='replace'  # 替换无法解码的字符
            )

            # 分析器应该返回非零退出码（因为没有提供 --file 参数）
            # 但应该包含帮助信息
            if "Roslyn" in result.stderr or "Roslyn" in result.stdout:
                logger.debug("Roslyn 分析器验证成功")
                return
        except subprocess.TimeoutExpired:
            logger.debug("Roslyn 分析器响应超时（这可能是正常的）")
            return
        except Exception as e:
            logger.warning(f"验证 Roslyn 分析器时出错: {e}")

        logger.warning("无法完全验证 Roslyn 分析器，但将继续尝试使用它")

    def analyze_file(
        self,
        file_path: Union[str, Path],
        timeout: Optional[int] = None,
        verbose: bool = False
    ) -> RoslynAnalysisResult:
        """
        分析单个 C# 文件

        Args:
            file_path: 要分析的 C# 文件路径
            timeout: 超时时间（秒），None 表示使用默认值
            verbose: 是否启用详细输出

        Returns:
            分析结果对象

        Raises:
            FileNotFoundError: 文件不存在
            subprocess.TimeoutExpired: 分析超时
            RuntimeError: 分析失败
        """
        file_path = Path(file_path).resolve()

        if not file_path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")

        if not file_path.suffix.lower() in ['.cs', '.csx']:
            logger.warning(f"文件扩展名可能不是 C# 文件: {file_path.suffix}")

        timeout = timeout or self.timeout

        logger.debug(f"开始分析文件: {file_path}")

        # 构建命令
        cmd = [
            str(self.analyzer_path),
            "--file", str(file_path)
        ]

        if verbose:
            cmd.append("--verbose")

        try:
            # 执行分析器
            result = subprocess.run(
                cmd,
                capture_output=True,
                timeout=timeout
            )

            # 手动解码输出
            import chardet

            def decode_output(data: bytes) -> str:
                """智能解码字节流"""
                if not data:
                    return ""

                # 先尝试 UTF-8（.NET 默认）
                try:
                    return data.decode('utf-8')
                except UnicodeDecodeError:
                    pass

                # 使用 chardet 检测编码
                detected = chardet.detect(data)
                if detected and detected['confidence'] > 0.7:
                    try:
                        return data.decode(detected['encoding'])
                    except:
                        pass

                # 最后使用替换模式
                return data.decode('utf-8', errors='replace')

            # 解码输出
            stdout = decode_output(result.stdout)
            stderr = decode_output(result.stderr)

            # 创建一个模拟的结果对象
            class ProcessResult:
                def __init__(self, returncode, stdout, stderr):
                    self.returncode = returncode
                    self.stdout = stdout
                    self.stderr = stderr

            result = ProcessResult(result.returncode, stdout, stderr)

            # 检查退出码
            if result.returncode != 0:
                error_msg = f"Roslyn 分析器失败，退出码: {result.returncode}"
                if result.stderr:
                    error_msg += f"\n错误输出: {result.stderr}"
                if result.stdout:
                    error_msg += f"\n标准输出: {result.stdout}"
                raise RuntimeError(error_msg)

            # 确保 stdout 不为 None
            if result.stdout is None:
                raise RuntimeError("分析器没有输出标准内容")

            # 解析 JSON 输出
            try:
                json_data = json.loads(result.stdout.strip())
            except json.JSONDecodeError as e:
                raise RuntimeError(f"解析分析器 JSON 输出失败: {e}\n输出内容: {result.stdout[:500]}...")  # 只显示前500个字符

            # 创建结果对象
            analysis_result = RoslynAnalysisResult.from_json(json_data)

            logger.debug(f"分析完成: {analysis_result.classes.count()} 个类, "
                        f"{sum(len(c.get('methods', [])) for c in analysis_result.classes)} 个方法")

            return analysis_result

        except subprocess.TimeoutExpired:
            raise subprocess.TimeoutExpired(cmd, timeout)
        except Exception as e:
            if isinstance(e, (FileNotFoundError, subprocess.TimeoutExpired, RuntimeError)):
                raise
            raise RuntimeError(f"分析文件时发生未预期的错误: {e}")

    def analyze_file_to_json(
        self,
        file_path: Union[str, Path],
        output_path: Optional[Union[str, Path]] = None,
        timeout: Optional[int] = None,
        verbose: bool = False
    ) -> Path:
        """
        分析 C# 文件并直接输出到 JSON 文件

        Args:
            file_path: 要分析的 C# 文件路径
            output_path: 输出 JSON 文件路径，None 表示使用临时文件
            timeout: 超时时间（秒）
            verbose: 是否启用详细输出

        Returns:
            输出 JSON 文件的路径
        """
        file_path = Path(file_path).resolve()

        if output_path is None:
            # 创建临时文件
            temp_fd, output_path = tempfile.mkstemp(suffix='.json', prefix='roslyn_analysis_')
            os.close(temp_fd)
            output_path = Path(output_path)

        output_path = Path(output_path).resolve()

        # 构建命令
        cmd = [
            str(self.analyzer_path),
            "--file", str(file_path),
            "--output", str(output_path)
        ]

        if verbose:
            cmd.append("--verbose")

        timeout = timeout or self.timeout

        try:
            # 执行分析器
            raw_result = subprocess.run(
                cmd,
                capture_output=True,
                timeout=timeout
            )

            # 手动解码输出
            import chardet

            def decode_output(data: bytes) -> str:
                """智能解码字节流"""
                if not data:
                    return ""

                # 先尝试 UTF-8（.NET 默认）
                try:
                    return data.decode('utf-8')
                except UnicodeDecodeError:
                    pass

                # 使用 chardet 检测编码
                detected = chardet.detect(data)
                if detected and detected['confidence'] > 0.7:
                    try:
                        return data.decode(detected['encoding'])
                    except:
                        pass

                # 最后使用替换模式
                return data.decode('utf-8', errors='replace')

            # 解码输出
            stdout = decode_output(raw_result.stdout)
            stderr = decode_output(raw_result.stderr)

            # 创建一个模拟的结果对象
            class ProcessResult:
                def __init__(self, returncode, stdout, stderr):
                    self.returncode = returncode
                    self.stdout = stdout
                    self.stderr = stderr

            result = ProcessResult(raw_result.returncode, stdout, stderr)

            # 检查退出码
            if result.returncode != 0:
                error_msg = f"Roslyn 分析器失败，退出码: {result.returncode}"
                if result.stderr:
                    error_msg += f"\n错误输出: {result.stderr}"
                raise RuntimeError(error_msg)

            # 验证输出文件是否存在
            if not output_path.exists():
                raise RuntimeError(f"分析器未生成输出文件: {output_path}")

            logger.debug(f"分析结果已保存到: {output_path}")
            return output_path

        except subprocess.TimeoutExpired:
            if output_path.exists():
                output_path.unlink(missing_ok=True)
            raise subprocess.TimeoutExpired(cmd, timeout)
        except Exception as e:
            if output_path.exists():
                output_path.unlink(missing_ok=True)
            if isinstance(e, (FileNotFoundError, subprocess.TimeoutExpired, RuntimeError)):
                raise
            raise RuntimeError(f"分析文件时发生未预期的错误: {e}")

    def is_available(self) -> bool:
        """检查 Roslyn 分析器是否可用"""
        try:
            result = subprocess.run(
                [str(self.analyzer_path), "--help"],
                capture_output=True,
                text=True,
                timeout=2
            )
            # 只检查是否能执行，不关心退出码
            return True
        except Exception:
            return False

    def get_version(self) -> Optional[str]:
        """尝试获取分析器版本信息"""
        try:
            result = subprocess.run(
                [str(self.analyzer_path), "--help"],
                capture_output=True,
                text=True,
                timeout=5,
                encoding='utf-8',
                errors='replace'  # 替换无法解码的字符
            )

            # 从输出中提取版本信息（如果有的话）
            output = result.stderr + result.stdout
            for line in output.split('\n'):
                if 'version' in line.lower() or '版本' in line:
                    return line.strip()

            return None
        except Exception:
            return None

    def __enter__(self):
        """支持上下文管理器"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """支持上下文管理器"""
        pass


# 导入需要的模块（可能不在标准库中）
try:
    import shutil
except ImportError:
    logger.warning("shutil 模块不可用，某些功能可能受限")
    shutil = None