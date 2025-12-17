using System;
using System.Collections.Generic;

namespace MathLibrary;

/// <summary>
/// 计算历史管理器
/// 负责记录和检索计算历史记录
/// </summary>
public class HistoryManager
{
    private readonly List<string> _records;
    private const int MaxRecords = 100;

    /// <summary>
    /// 历史管理器构造函数
    /// </summary>
    public HistoryManager()
    {
        _records = new List<string>();
    }

    /// <summary>
    /// 添加计算记录
    /// </summary>
    /// <param name="record">计算记录字符串</param>
    /// <exception cref="ArgumentNullException">当记录为null时抛出</exception>
    public void AddRecord(string record)
    {
        if (record == null)
        {
            throw new ArgumentNullException(nameof(record));
        }

        _records.Add($"[{DateTime.Now:HH:mm:ss}] {record}");

        // 限制记录数量
        if (_records.Count > MaxRecords)
        {
            _records.RemoveAt(0);
        }
    }

    /// <summary>
    /// 获取所有历史记录
    /// </summary>
    /// <returns>历史记录的只读列表</returns>
    public IReadOnlyList<string> GetRecords()
    {
        return _records.AsReadOnly();
    }

    /// <summary>
    /// 清空所有历史记录
    /// </summary>
    public void Clear()
    {
        _records.Clear();
    }

    /// <summary>
    /// 获取历史记录数量
    /// </summary>
    public int Count => _records.Count;

    /// <summary>
    /// 获取最近的记录
    /// </summary>
    /// <param name="count">要获取的记录数量</param>
    /// <returns>最近的记录列表</returns>
    public IReadOnlyList<string> GetRecentRecords(int count = 10)
    {
        if (count <= 0)
        {
            return new List<string>().AsReadOnly();
        }

        var startIndex = Math.Max(0, _records.Count - count);
        var recentRecords = _records.GetRange(startIndex, Math.Min(count, _records.Count));
        return recentRecords.AsReadOnly();
    }
}