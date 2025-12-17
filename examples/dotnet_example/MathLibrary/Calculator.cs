using System;

namespace MathLibrary;

/// <summary>
/// 高级计算器类
/// 提供基本的数学运算功能和统计计算
/// </summary>
public class Calculator
{
    private double _lastResult;
    private readonly HistoryManager _history;

    /// <summary>
    /// 计算器构造函数
    /// </summary>
    public Calculator()
    {
        _lastResult = 0;
        _history = new HistoryManager();
    }

    /// <summary>
    /// 获取或设置最后一次计算结果
    /// </summary>
    public double LastResult
    {
        get => _lastResult;
        private set => _lastResult = value;
    }

    /// <summary>
    /// 加法运算
    /// </summary>
    /// <param name="a">第一个操作数</param>
    /// <param name="b">第二个操作数</param>
    /// <returns>两数之和</returns>
    /// <example>
    /// <code>
    /// var calculator = new Calculator();
    /// double result = calculator.Add(5, 3); // 结果: 8
    /// </code>
    /// </example>
    public double Add(double a, double b)
    {
        var result = a + b;
        _lastResult = result;
        _history.AddRecord($"{a} + {b} = {result}");
        return result;
    }

    /// <summary>
    /// 减法运算
    /// </summary>
    /// <param name="a">被减数</param>
    /// <param name="b">减数</param>
    /// <returns>两数之差</returns>
    /// <exception cref="CalculatorException">当结果超出允许范围时抛出</exception>
    public double Subtract(double a, double b)
    {
        var result = a - b;
        ValidateResult(result);
        _lastResult = result;
        _history.AddRecord($"{a} - {b} = {result}");
        return result;
    }

    /// <summary>
    /// 乘法运算
    /// </summary>
    /// <param name="a">第一个操作数</param>
    /// <param name="b">第二个操作数</param>
    /// <returns>两数之积</returns>
    public double Multiply(double a, double b)
    {
        var result = a * b;
        _lastResult = result;
        _history.AddRecord($"{a} × {b} = {result}");
        return result;
    }

    /// <summary>
    /// 除法运算
    /// </summary>
    /// <param name="a">被除数</param>
    /// <param name="b">除数</param>
    /// <returns>两数之商</returns>
    /// <exception cref="DivideByZeroException">当除数为零时抛出</exception>
    /// <exception cref="CalculatorException">当结果超出允许范围时抛出</exception>
    public double Divide(double a, double b)
    {
        if (b == 0)
        {
            throw new DivideByZeroException("除数不能为零");
        }

        var result = a / b;
        ValidateResult(result);
        _lastResult = result;
        _history.AddRecord($"{a} ÷ {b} = {result}");
        return result;
    }

    /// <summary>
    /// 幂运算
    /// </summary>
    /// <param name="baseNumber">底数</param>
    /// <param name="exponent">指数</param>
    /// <returns>幂运算结果</returns>
    /// <exception cref="CalculatorException">当结果超出允许范围时抛出</exception>
    public double Power(double baseNumber, double exponent)
    {
        try
        {
            var result = Math.Pow(baseNumber, exponent);
            ValidateResult(result);
            _lastResult = result;
            _history.AddRecord($"{baseNumber}^{exponent} = {result}");
            return result;
        }
        catch (OverflowException)
        {
            throw new CalculatorException("幂运算结果超出有效范围");
        }
    }

    /// <summary>
    /// 计算平方根
    /// </summary>
    /// <param name="number">要开方的数字</param>
    /// <returns>平方根结果</returns>
    /// <exception cref="ArgumentException">当数字为负数时抛出</exception>
    public double SquareRoot(double number)
    {
        if (number < 0)
        {
            throw new ArgumentException("不能计算负数的平方根", nameof(number));
        }

        var result = Math.Sqrt(number);
        _lastResult = result;
        _history.AddRecord($"√{number} = {result}");
        return result;
    }

    /// <summary>
    /// 计算一组数的平均值
    /// </summary>
    /// <param name="numbers">数字数组</param>
    /// <returns>平均值</returns>
    /// <exception cref="ArgumentException">当数组为空时抛出</exception>
    public double Average(params double[] numbers)
    {
        if (numbers.Length == 0)
        {
            throw new ArgumentException("数字数组不能为空", nameof(numbers));
        }

        var sum = 0.0;
        foreach (var num in numbers)
        {
            sum += num;
        }

        var result = sum / numbers.Length;
        _lastResult = result;
        _history.AddRecord($"Average({string.Join(", ", numbers)}) = {result}");
        return result;
    }

    /// <summary>
    /// 计算一组数的最大值
    /// </summary>
    /// <param name="numbers">数字数组</param>
    /// <returns>最大值</returns>
    /// <exception cref="ArgumentException">当数组为空时抛出</exception>
    public double Max(params double[] numbers)
    {
        if (numbers.Length == 0)
        {
            throw new ArgumentException("数字数组不能为空", nameof(numbers));
        }

        var result = numbers[0];
        for (int i = 1; i < numbers.Length; i++)
        {
            if (numbers[i] > result)
            {
                result = numbers[i];
            }
        }

        _lastResult = result;
        _history.AddRecord($"Max({string.Join(", ", numbers)}) = {result}");
        return result;
    }

    /// <summary>
    /// 计算一组数的最小值
    /// </summary>
    /// <param name="numbers">数字数组</param>
    /// <returns>最小值</returns>
    /// <exception cref="ArgumentException">当数组为空时抛出</exception>
    public double Min(params double[] numbers)
    {
        if (numbers.Length == 0)
        {
            throw new ArgumentException("数字数组不能为空", nameof(numbers));
        }

        var result = numbers[0];
        for (int i = 1; i < numbers.Length; i++)
        {
            if (numbers[i] < result)
            {
                result = numbers[i];
            }
        }

        _lastResult = result;
        _history.AddRecord($"Min({string.Join(", ", numbers)}) = {result}");
        return result;
    }

    /// <summary>
    /// 重置计算器状态
    /// </summary>
    public void Reset()
    {
        _lastResult = 0;
        _history.Clear();
    }

    /// <summary>
    /// 获取计算历史记录
    /// </summary>
    /// <returns>历史记录列表</returns>
    public IReadOnlyList<string> GetHistory()
    {
        return _history.GetRecords();
    }

    /// <summary>
    /// 验证计算结果是否在有效范围内
    /// </summary>
    /// <param name="result">计算结果</param>
    /// <exception cref="CalculatorException">当结果超出范围时抛出</exception>
    private void ValidateResult(double result)
    {
        const double MaxValue = 1e100;
        const double MinValue = -1e100;

        if (double.IsNaN(result))
        {
            throw new CalculatorException("计算结果无效（NaN）");
        }

        if (double.IsInfinity(result))
        {
            throw new CalculatorException("计算结果超出范围（无穷大）");
        }

        if (result > MaxValue || result < MinValue)
        {
            throw new CalculatorException($"计算结果超出有效范围 [{MinValue}, {MaxValue}]");
        }
    }
}

/// <summary>
/// 计算器异常类
/// </summary>
public class CalculatorException : Exception
{
    /// <summary>
    /// 计算器异常构造函数
    /// </summary>
    public CalculatorException() : base()
    {
    }

    /// <summary>
    /// 计算器异常构造函数
    /// </summary>
    /// <param name="message">异常消息</param>
    public CalculatorException(string message) : base(message)
    {
    }

    /// <summary>
    /// 计算器异常构造函数
    /// </summary>
    /// <param name="message">异常消息</param>
    /// <param name="innerException">内部异常</param>
    public CalculatorException(string message, Exception innerException) : base(message, innerException)
    {
    }
}