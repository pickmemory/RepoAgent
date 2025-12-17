"""
性能优化和内存管理模块
实现缓存、增量处理和性能监控功能，优化大型 .NET 项目处理性能
"""

import os
import time
import hashlib
import functools
import threading
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable, Union, Tuple
from dataclasses import dataclass, field
from collections import OrderedDict
from contextlib import contextmanager
import weakref
import gc
import psutil
import logging

from repo_agent.log import logger


@dataclass
class PerformanceMetrics:
    """性能指标数据类"""
    operation_name: str
    start_time: float = field(default_factory=time.time)
    end_time: Optional[float] = None
    duration: Optional[float] = None
    memory_start: Optional[int] = None
    memory_end: Optional[int] = None
    memory_peak: Optional[int] = None
    items_processed: int = 0
    success: bool = True
    error_message: Optional[str] = None

    def finish(self, items_processed: int = 0, success: bool = True, error_message: str = None):
        """完成性能测量"""
        self.end_time = time.time()
        self.duration = self.end_time - self.start_time
        self.items_processed = items_processed
        self.success = success
        self.error_message = error_message

    @property
    def throughput(self) -> float:
        """计算吞吐量（项目/秒）"""
        if self.duration and self.duration > 0:
            return self.items_processed / self.duration
        return 0.0

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'operation': self.operation_name,
            'duration': self.duration,
            'items_processed': self.items_processed,
            'throughput': self.throughput,
            'memory_start': self.memory_start,
            'memory_end': self.memory_end,
            'memory_peak': self.memory_peak,
            'success': self.success,
            'error_message': self.error_message
        }


class LRUCache:
    """线程安全的LRU缓存实现"""

    def __init__(self, max_size: int = 1000, ttl: Optional[float] = None):
        """
        初始化LRU缓存

        Args:
            max_size: 最大缓存项数
            ttl: 生存时间（秒），None表示永不过期
        """
        self.max_size = max_size
        self.ttl = ttl
        self.cache = OrderedDict()
        self.timestamps = {}
        self.lock = threading.RLock()
        self.hits = 0
        self.misses = 0

    def _is_expired(self, key: Any) -> bool:
        """检查缓存项是否过期"""
        if self.ttl is None:
            return False
        timestamp = self.timestamps.get(key, 0)
        return time.time() - timestamp > self.ttl

    def get(self, key: Any) -> Optional[Any]:
        """获取缓存值"""
        with self.lock:
            if key not in self.cache:
                self.misses += 1
                return None

            # 检查是否过期
            if self._is_expired(key):
                self._remove_key(key)
                self.misses += 1
                return None

            # 移动到末尾（最近使用）
            value = self.cache.pop(key)
            self.cache[key] = value
            self.hits += 1
            return value

    def put(self, key: Any, value: Any):
        """设置缓存值"""
        with self.lock:
            # 如果已存在，先删除
            if key in self.cache:
                self.cache.pop(key)
            elif len(self.cache) >= self.max_size:
                # 删除最久未使用的项
                oldest_key = next(iter(self.cache))
                self._remove_key(oldest_key)

            self.cache[key] = value
            self.timestamps[key] = time.time()

    def _remove_key(self, key: Any):
        """删除缓存项"""
        self.cache.pop(key, None)
        self.timestamps.pop(key, None)

    def clear(self):
        """清空缓存"""
        with self.lock:
            self.cache.clear()
            self.timestamps.clear()
            self.hits = 0
            self.misses = 0

    def size(self) -> int:
        """获取缓存大小"""
        with self.lock:
            return len(self.cache)

    def hit_rate(self) -> float:
        """获取缓存命中率"""
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0.0

    def stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        with self.lock:
            return {
                'size': len(self.cache),
                'max_size': self.max_size,
                'hits': self.hits,
                'misses': self.misses,
                'hit_rate': self.hit_rate()
            }


class MemoryMonitor:
    """内存使用监控器"""

    def __init__(self):
        self.process = psutil.Process()
        self.peak_memory = 0
        self.measurements = []

    def get_memory_usage(self) -> int:
        """获取当前内存使用量（字节）"""
        return self.process.memory_info().rss

    def get_memory_mb(self) -> float:
        """获取当前内存使用量（MB）"""
        return self.get_memory_usage() / (1024 * 1024)

    def start_monitoring(self):
        """开始监控"""
        self.peak_memory = self.get_memory_usage()
        self.measurements = []

    def record_measurement(self, label: str = None):
        """记录内存测量"""
        current = self.get_memory_usage()
        self.peak_memory = max(self.peak_memory, current)
        self.measurements.append({
            'timestamp': time.time(),
            'memory': current,
            'label': label
        })

    def get_peak_memory(self) -> int:
        """获取峰值内存使用量"""
        return self.peak_memory

    def get_memory_stats(self) -> Dict[str, Any]:
        """获取内存统计信息"""
        if not self.measurements:
            current = self.get_memory_usage()
        else:
            current = self.measurements[-1]['memory']

        return {
            'current_mb': current / (1024 * 1024),
            'peak_mb': self.peak_memory / (1024 * 1024),
            'measurements_count': len(self.measurements),
            'process_memory_percent': self.process.memory_percent()
        }


class PerformanceOptimizer:
    """性能优化器主类"""

    def __init__(self, cache_size: int = 1000, cache_ttl: Optional[float] = 3600):
        """
        初始化性能优化器

        Args:
            cache_size: 缓存大小
            cache_ttl: 缓存生存时间（秒）
        """
        self.file_cache = LRUCache(cache_size, cache_ttl)
        self.parse_cache = LRUCache(cache_size * 2, cache_ttl)
        self.memory_monitor = MemoryMonitor()
        self.metrics_history: List[PerformanceMetrics] = []
        self.lock = threading.RLock()

        # 性能配置
        self.config = {
            'large_file_threshold': 1024 * 1024,  # 1MB
            'parallel_processing_threshold': 10,   # 文件数量
            'max_memory_usage_mb': 1024,            # 1GB
            'gc_frequency': 100,                    # 每100次操作执行一次GC
            'operation_count': 0
        }

    @contextmanager
    def measure_performance(self, operation_name: str):
        """性能测量上下文管理器"""
        metrics = PerformanceMetrics(operation_name)
        metrics.memory_start = self.memory_monitor.get_memory_usage()

        try:
            self.memory_monitor.start_monitoring()
            yield metrics
        except Exception as e:
            metrics.finish(success=False, error_message=str(e))
            raise
        finally:
            metrics.memory_end = self.memory_monitor.get_memory_usage()
            metrics.memory_peak = self.memory_monitor.get_peak_memory()

            # 记录指标
            with self.lock:
                self.metrics_history.append(metrics)

                # 限制历史记录大小
                if len(self.metrics_history) > 1000:
                    self.metrics_history = self.metrics_history[-500:]

            # 定期执行垃圾回收
            self._maybe_gc()

    def _maybe_gc(self):
        """条件性垃圾回收"""
        self.config['operation_count'] += 1
        if self.config['operation_count'] >= self.config['gc_frequency']:
            gc.collect()
            self.config['operation_count'] = 0
            logger.debug("执行垃圾回收")

    def get_cache_key(self, file_path: str, content_hash: Optional[str] = None) -> str:
        """生成缓存键"""
        if not content_hash:
            # 快速哈希文件路径和修改时间
            file_path_obj = Path(file_path)
            try:
                mtime = file_path_obj.stat().st_mtime
                content_hash = f"{file_path}_{mtime}"
            except OSError:
                content_hash = file_path

        return hashlib.md5(content_hash.encode()).hexdigest()

    def get_file_content_hash(self, file_path: str) -> Optional[str]:
        """计算文件内容哈希"""
        try:
            file_path_obj = Path(file_path)
            if not file_path_obj.exists():
                return None

            # 对于大文件，使用部分哈希
            if file_path_obj.stat().st_size > self.config['large_file_threshold']:
                return self._get_partial_hash(file_path_obj)
            else:
                return self._get_full_hash(file_path_obj)

        except Exception as e:
            logger.warning(f"计算文件哈希失败: {file_path}, 错误: {e}")
            return None

    def _get_full_hash(self, file_path: Path) -> str:
        """计算完整文件哈希"""
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    def _get_partial_hash(self, file_path: Path) -> str:
        """计算部分文件哈希（用于大文件）"""
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            # 读取开头、中间和结尾的部分内容
            size = file_path.stat().st_size

            # 开头 4KB
            chunk = f.read(4096)
            hash_md5.update(chunk)

            # 中间 4KB
            if size > 8192:
                f.seek(size // 2)
                chunk = f.read(4096)
                hash_md5.update(chunk)

            # 结尾 4KB
            if size > 12288:
                f.seek(-4096, 2)
                chunk = f.read(4096)
                hash_md5.update(chunk)

        return hash_md5.hexdigest()

    def cached_parse(self, file_path: str, parse_func: Callable[[str], Any]) -> Any:
        """
        带缓存的解析函数

        Args:
            file_path: 文件路径
            parse_func: 解析函数

        Returns:
            解析结果（可能来自缓存）
        """
        # 检查内存使用情况
        if self.memory_monitor.get_memory_mb() > self.config['max_memory_usage_mb']:
            logger.warning("内存使用过高，清空缓存")
            self.file_cache.clear()
            self.parse_cache.clear()

        # 获取文件内容哈希
        content_hash = self.get_file_content_hash(file_path)
        if not content_hash:
            # 无法获取哈希，直接解析
            return parse_func(file_path)

        cache_key = self.get_cache_key(file_path, content_hash)

        # 尝试从缓存获取
        result = self.parse_cache.get(cache_key)
        if result is not None:
            logger.debug(f"缓存命中: {file_path}")
            return result

        # 缓存未命中，执行解析
        logger.debug(f"缓存未命中，解析文件: {file_path}")
        result = parse_func(file_path)

        # 存入缓存
        if result is not None:
            self.parse_cache.put(cache_key, result)

        return result

    def get_performance_stats(self) -> Dict[str, Any]:
        """获取性能统计信息"""
        with self.lock:
            # 计算平均性能
            recent_metrics = self.metrics_history[-20:]  # 最近20次操作

            stats = {
                'cache_stats': {
                    'file_cache': self.file_cache.stats(),
                    'parse_cache': self.parse_cache.stats()
                },
                'memory_stats': self.memory_monitor.get_memory_stats(),
                'recent_operations': len(recent_metrics),
                'total_operations': len(self.metrics_history)
            }

            if recent_metrics:
                durations = [m.duration for m in recent_metrics if m.duration]
                throughputs = [m.throughput for m in recent_metrics if m.throughput > 0]
                success_rate = sum(1 for m in recent_metrics if m.success) / len(recent_metrics)

                stats.update({
                    'avg_duration': sum(durations) / len(durations) if durations else 0,
                    'max_duration': max(durations) if durations else 0,
                    'min_duration': min(durations) if durations else 0,
                    'avg_throughput': sum(throughputs) / len(throughputs) if throughputs else 0,
                    'success_rate': success_rate
                })

            return stats

    def get_slow_operations(self, threshold_seconds: float = 1.0) -> List[Dict[str, Any]]:
        """获取慢操作列表"""
        with self.lock:
            slow_ops = []
            for metric in self.metrics_history:
                if metric.duration and metric.duration > threshold_seconds:
                    slow_ops.append(metric.to_dict())
            return slow_ops

    def clear_caches(self):
        """清空所有缓存"""
        self.file_cache.clear()
        self.parse_cache.clear()
        logger.info("已清空所有缓存")

    def optimize_memory(self):
        """内存优化"""
        # 执行垃圾回收
        gc.collect()

        # 清空缓存如果内存使用过高
        current_memory_mb = self.memory_monitor.get_memory_mb()
        if current_memory_mb > self.config['max_memory_usage_mb'] * 0.8:
            logger.info(f"内存使用较高 ({current_memory_mb:.1f}MB)，清空缓存")
            self.clear_caches()

        return current_memory_mb


# 全局性能优化器实例
_global_optimizer: Optional[PerformanceOptimizer] = None
_optimizer_lock = threading.Lock()


def get_global_optimizer() -> PerformanceOptimizer:
    """获取全局性能优化器实例"""
    global _global_optimizer
    if _global_optimizer is None:
        with _optimizer_lock:
            if _global_optimizer is None:
                _global_optimizer = PerformanceOptimizer()
    return _global_optimizer


def performance_monitor(operation_name: str):
    """性能监控装饰器"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            optimizer = get_global_optimizer()
            with optimizer.measure_performance(operation_name) as metrics:
                try:
                    result = func(*args, **kwargs)

                    # 尝试获取处理的项目数量
                    if isinstance(result, list):
                        metrics.finish(items_processed=len(result))
                    elif hasattr(result, '__len__'):
                        metrics.finish(items_processed=len(result))
                    else:
                        metrics.finish(items_processed=1)

                    return result
                except Exception as e:
                    metrics.finish(success=False, error_message=str(e))
                    raise

        return wrapper
    return decorator


def cached_operation(cache_type: str = 'parse'):
    """缓存操作装饰器"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(self, file_path: str, *args, **kwargs):
            optimizer = get_global_optimizer()

            if cache_type == 'parse':
                return optimizer.cached_parse(file_path, lambda fp: func(self, fp, *args, **kwargs))
            else:
                # 其他类型的缓存可以在这里扩展
                return func(self, file_path, *args, **kwargs)

        return wrapper
    return decorator


def memory_efficient(file_size_threshold: int = 1024 * 1024):
    """内存高效处理装饰器"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(self, file_path: str, *args, **kwargs):
            # 检查文件大小
            try:
                file_size = Path(file_path).stat().st_size
                if file_size > file_size_threshold:
                    logger.info(f"处理大文件: {file_path} ({file_size / 1024 / 1024:.1f}MB)")
                    # 可以在这里添加特殊的大文件处理逻辑
            except OSError:
                pass

            return func(self, file_path, *args, **kwargs)

        return wrapper
    return decorator


# 性能分析和报告工具
class PerformanceAnalyzer:
    """性能分析器"""

    def __init__(self, optimizer: Optional[PerformanceOptimizer] = None):
        self.optimizer = optimizer or get_global_optimizer()

    def generate_report(self) -> str:
        """生成性能报告"""
        stats = self.optimizer.get_performance_stats()
        slow_ops = self.optimizer.get_slow_operations()

        report = ["=" * 60]
        report.append("性能分析报告")
        report.append("=" * 60)

        # 基本统计
        report.append(f"\n总操作数: {stats['total_operations']}")
        report.append(f"最近操作数: {stats['recent_operations']}")

        if 'avg_duration' in stats:
            report.append(f"\n平均耗时: {stats['avg_duration']:.3f}秒")
            report.append(f"最大耗时: {stats['max_duration']:.3f}秒")
            report.append(f"最小耗时: {stats['min_duration']:.3f}秒")
            report.append(f"平均吞吐量: {stats['avg_throughput']:.1f} 项/秒")
            report.append(f"成功率: {stats['success_rate']:.1%}")

        # 缓存统计
        report.append("\n缓存统计:")
        for cache_name, cache_stats in stats['cache_stats'].items():
            report.append(f"  {cache_name}:")
            report.append(f"    大小: {cache_stats['size']}/{cache_stats['max_size']}")
            report.append(f"    命中率: {cache_stats['hit_rate']:.1%}")

        # 内存统计
        mem_stats = stats['memory_stats']
        report.append(f"\n内存统计:")
        report.append(f"  当前使用: {mem_stats['current_mb']:.1f}MB")
        report.append(f"  峰值使用: {mem_stats['peak_mb']:.1f}MB")
        report.append(f"  进程内存占比: {mem_stats['process_memory_percent']:.1f}%")

        # 慢操作
        if slow_ops:
            report.append(f"\n慢操作 (>1秒):")
            for op in slow_ops[:5]:  # 只显示前5个
                report.append(f"  {op['operation']}: {op['duration']:.3f}秒")

        report.append("\n" + "=" * 60)

        return "\n".join(report)

    def save_report(self, file_path: str):
        """保存性能报告到文件"""
        report = self.generate_report()
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(report)
        logger.info(f"性能报告已保存到: {file_path}")