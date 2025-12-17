using Microsoft.AspNetCore.Mvc;

namespace WebAppSample.Controllers;

/// <summary>
/// 天气预报API控制器
/// 提供天气预报信息的RESTful API端点
/// </summary>
[ApiController]
[Route("api/[controller]")]
public class WeatherForecastController : ControllerBase
{
    private static readonly string[] Summaries = new[]
    {
        "Freezing", "Bracing", "Chilly", "Cool", "Mild", "Warm", "Balmy", "Hot", "Sweltering", "Scorching"
    };

    private readonly ILogger<WeatherForecastController> _logger;

    /// <summary>
    /// 天气预报控制器构造函数
    /// </summary>
    /// <param name="logger">日志记录器</param>
    public WeatherForecastController(ILogger<WeatherForecastController> logger)
    {
        _logger = logger;
    }

    /// <summary>
    /// 获取天气预报信息
    /// </summary>
    /// <returns>未来5天的天气预报</returns>
    [HttpGet(Name = "GetWeatherForecast")]
    public IEnumerable<WeatherForecast> Get()
    {
        _logger.LogInformation("获取天气预报请求");

        return Enumerable.Range(1, 5).Select(index => new WeatherForecast
        {
            Date = DateOnly.FromDateTime(DateTime.Now.AddDays(index)),
            TemperatureC = Random.Shared.Next(-20, 55),
            Summary = Summaries[Random.Shared.Next(Summaries.Length)]
        })
        .ToArray();
    }

    /// <summary>
    /// 根据日期获取天气预报
    /// </summary>
    /// <param name="date">目标日期（格式：YYYY-MM-DD）</param>
    /// <returns>指定日期的天气预报</returns>
    [HttpGet("by-date/{date}")]
    public ActionResult<WeatherForecast> GetByDate(string date)
    {
        if (!DateOnly.TryParse(date, out var targetDate))
        {
            return BadRequest("日期格式无效，请使用 YYYY-MM-DD 格式");
        }

        _logger.LogInformation($"获取 {date} 的天气预报");

        var forecast = new WeatherForecast
        {
            Date = targetDate,
            TemperatureC = Random.Shared.Next(-20, 55),
            Summary = Summaries[Random.Shared.Next(Summaries.Length)]
        };

        return Ok(forecast);
    }
}

/// <summary>
/// 天气预报数据模型
/// </summary>
public class WeatherForecast
{
    /// <summary>
    /// 预报日期
    /// </summary>
    public DateOnly Date { get; set; }

    /// <summary>
    /// 温度（摄氏度）
    /// </summary>
    public int TemperatureC { get; set; }

    /// <summary>
    /// 温度（华氏度）
    /// </summary>
    public int TemperatureF => 32 + (int)(TemperatureC / 0.5556);

    /// <summary>
    /// 天气描述
    /// </summary>
    public string? Summary { get; set; }
}