using System.ComponentModel.DataAnnotations;

namespace WebAppSample.Models;

/// <summary>
/// 用户实体模型
/// 演示复杂的数据模型定义
/// </summary>
public class User
{
    /// <summary>
    /// 用户唯一标识符
    /// </summary>
    public int Id { get; set; }

    /// <summary>
    /// 用户名
    /// </summary>
    [Required]
    [StringLength(50, MinimumLength = 3)]
    public string Username { get; set; } = string.Empty;

    /// <summary>
    /// 邮箱地址
    /// </summary>
    [Required]
    [EmailAddress]
    public string Email { get; set; } = string.Empty;

    /// <summary>
    /// 用户全名
    /// </summary>
    [StringLength(100)]
    public string? FullName { get; set; }

    /// <summary>
    /// 用户创建时间
    /// </summary>
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;

    /// <summary>
    /// 用户是否激活
    /// </summary>
    public bool IsActive { get; set; } = true;

    /// <summary>
    /// 用户角色
    /// </summary>
    public UserRole Role { get; set; } = UserRole.User;

    /// <summary>
    /// 用户配置信息
    /// </summary>
    public UserSettings? Settings { get; set; }

    /// <summary>
    /// 用户所属部门
    /// </summary>
    public Department? Department { get; set; }
}

/// <summary>
/// 用户角色枚举
/// </summary>
public enum UserRole
{
    /// <summary>
    /// 普通用户
    /// </summary>
    User = 0,

    /// <summary>
    /// 管理员
    /// </summary>
    Administrator = 1,

    /// <summary>
    /// 访客
    /// </summary>
    Guest = 2,

    /// <summary>
    /// 开发者
    /// </summary>
    Developer = 3
}

/// <summary>
/// 用户设置类
/// </summary>
public class UserSettings
{
    /// <summary>
    /// 主题设置
    /// </summary>
    public string Theme { get; set; } = "Light";

    /// <summary>
    /// 语言设置
    /// </summary>
    public string Language { get; set; } = "en-US";

    /// <summary>
    /// 是否启用通知
    /// </summary>
    public bool EnableNotifications { get; set; } = true;

    /// <summary>
    /// 时区设置
    /// </summary>
    public string Timezone { get; set; } = "UTC";
}

/// <summary>
/// 部门类
/// </summary>
public class Department
{
    /// <summary>
    /// 部门ID
    /// </summary>
    public int Id { get; set; }

    /// <summary>
    /// 部门名称
    /// </summary>
    [Required]
    [StringLength(100)]
    public string Name { get; set; } = string.Empty;

    /// <summary>
    /// 部门描述
    /// </summary>
    public string? Description { get; set; }

    /// <summary>
    /// 部门经理
    /// </summary>
    public string? Manager { get; set; }

    /// <summary>
    /// 创建时间
    /// </summary>
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
}