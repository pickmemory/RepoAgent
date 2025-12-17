using Microsoft.Extensions.Logging;
using WebAppSample.Models;

namespace WebAppSample.Services;

/// <summary>
/// 用户服务实现类
/// 提供用户相关的业务逻辑操作
/// </summary>
public class UserService : IUserService
{
    private readonly ILogger<UserService> _logger;
    private readonly List<User> _users; // 模拟内存数据存储

    /// <summary>
    /// 用户服务构造函数
    /// </summary>
    /// <param name="logger">日志记录器</param>
    public UserService(ILogger<UserService> logger)
    {
        _logger = logger;
        _users = new List<User>();
        InitializeSampleData();
    }

    /// <inheritdoc />
    public async Task<IEnumerable<User>> GetAllUsersAsync(bool includeInactive = false)
    {
        _logger.LogInformation($"获取所有用户，包含非活跃: {includeInactive}");

        var query = _users.AsEnumerable();
        if (!includeInactive)
        {
            query = query.Where(u => u.IsActive);
        }

        return await Task.FromResult(query.OrderByDescending(u => u.CreatedAt));
    }

    /// <inheritdoc />
    public async Task<User?> GetUserByIdAsync(int id)
    {
        _logger.LogInformation($"根据ID获取用户: {id}");

        var user = _users.FirstOrDefault(u => u.Id == id);
        return await Task.FromResult(user);
    }

    /// <inheritdoc />
    public async Task<User?> GetUserByUsernameAsync(string username)
    {
        _logger.LogInformation($"根据用户名获取用户: {username}");

        var user = _users.FirstOrDefault(u =>
            u.Username.Equals(username, StringComparison.OrdinalIgnoreCase));
        return await Task.FromResult(user);
    }

    /// <inheritdoc />
    public async Task<User> CreateUserAsync(User user)
    {
        _logger.LogInformation($"创建新用户: {user.Username}");

        // 验证用户名唯一性
        if (_users.Any(u => u.Username.Equals(user.Username, StringComparison.OrdinalIgnoreCase)))
        {
            throw new InvalidOperationException($"用户名 '{user.Username}' 已存在");
        }

        // 验证邮箱唯一性
        if (_users.Any(u => u.Email.Equals(user.Email, StringComparison.OrdinalIgnoreCase)))
        {
            throw new InvalidOperationException($"邮箱 '{user.Email}' 已被使用");
        }

        // 生成新ID
        user.Id = _users.Any() ? _users.Max(u => u.Id) + 1 : 1;
        user.CreatedAt = DateTime.UtcNow;
        user.IsActive = true;

        _users.Add(user);

        _logger.LogInformation($"用户创建成功，ID: {user.Id}");
        return await Task.FromResult(user);
    }

    /// <inheritdoc />
    public async Task<User?> UpdateUserAsync(int id, User user)
    {
        _logger.LogInformation($"更新用户信息，ID: {id}");

        var existingUser = _users.FirstOrDefault(u => u.Id == id);
        if (existingUser == null)
        {
            return await Task.FromResult<User?>(null);
        }

        // 验证用户名唯一性（排除自己）
        if (_users.Any(u => u.Id != id &&
            u.Username.Equals(user.Username, StringComparison.OrdinalIgnoreCase)))
        {
            throw new InvalidOperationException($"用户名 '{user.Username}' 已被其他用户使用");
        }

        // 验证邮箱唯一性（排除自己）
        if (_users.Any(u => u.Id != id &&
            u.Email.Equals(user.Email, StringComparison.OrdinalIgnoreCase)))
        {
            throw new InvalidOperationException($"邮箱 '{user.Email}' 已被其他用户使用");
        }

        // 更新用户信息
        existingUser.Username = user.Username;
        existingUser.Email = user.Email;
        existingUser.FullName = user.FullName;
        existingUser.Role = user.Role;
        existingUser.Settings = user.Settings;
        existingUser.Department = user.Department;

        _logger.LogInformation($"用户信息更新成功，ID: {id}");
        return await Task.FromResult(existingUser);
    }

    /// <inheritdoc />
    public async Task<bool> DeleteUserAsync(int id)
    {
        _logger.LogInformation($"删除用户，ID: {id}");

        var user = _users.FirstOrDefault(u => u.Id == id);
        if (user == null)
        {
            return await Task.FromResult(false);
        }

        _users.Remove(user);
        _logger.LogInformation($"用户删除成功，ID: {id}");
        return await Task.FromResult(true);
    }

    /// <inheritdoc />
    public async Task<bool> SetUserActiveStatusAsync(int id, bool isActive)
    {
        _logger.LogInformation($"设置用户状态，ID: {id}, 激活: {isActive}");

        var user = _users.FirstOrDefault(u => u.Id == id);
        if (user == null)
        {
            return await Task.FromResult(false);
        }

        user.IsActive = isActive;
        _logger.LogInformation($"用户状态设置成功，ID: {id}");
        return await Task.FromResult(true);
    }

    /// <inheritdoc />
    public async Task<IEnumerable<User>> GetUsersByRoleAsync(UserRole role)
    {
        _logger.LogInformation($"根据角色获取用户，角色: {role}");

        var users = _users.Where(u => u.Role == role && u.IsActive);
        return await Task.FromResult(users);
    }

    /// <summary>
    /// 初始化示例数据
    /// </summary>
    private void InitializeSampleData()
    {
        _logger.LogInformation("初始化示例用户数据");

        var sampleUsers = new List<User>
        {
            new User
            {
                Id = 1,
                Username = "admin",
                Email = "admin@example.com",
                FullName = "系统管理员",
                Role = UserRole.Administrator,
                Settings = new UserSettings
                {
                    Theme = "Dark",
                    Language = "zh-CN",
                    EnableNotifications = true
                }
            },
            new User
            {
                Id = 2,
                Username = "developer",
                Email = "dev@example.com",
                FullName = "开发者",
                Role = UserRole.Developer,
                Settings = new UserSettings
                {
                    Theme = "Light",
                    Language = "en-US",
                    EnableNotifications = true
                }
            },
            new User
            {
                Id = 3,
                Username = "john_doe",
                Email = "john@example.com",
                FullName = "John Doe",
                Role = UserRole.User,
                IsActive = false,
                Department = new Department
                {
                    Id = 1,
                    Name = "IT部门",
                    Description = "信息技术部门",
                    Manager = "Alice Smith"
                }
            }
        };

        _users.AddRange(sampleUsers);
        _logger.LogInformation($"已初始化 {sampleUsers.Count} 个示例用户");
    }
}