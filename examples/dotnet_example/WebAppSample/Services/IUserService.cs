using WebAppSample.Models;

namespace WebAppSample.Services;

/// <summary>
/// 用户服务接口
/// 定义用户相关业务操作的契约
/// </summary>
public interface IUserService
{
    /// <summary>
    /// 获取所有用户
    /// </summary>
    /// <param name="includeInactive">是否包含非活跃用户</param>
    /// <returns>用户列表</returns>
    Task<IEnumerable<User>> GetAllUsersAsync(bool includeInactive = false);

    /// <summary>
    /// 根据ID获取用户
    /// </summary>
    /// <param name="id">用户ID</param>
    /// <returns>用户信息，如果不存在返回null</returns>
    Task<User?> GetUserByIdAsync(int id);

    /// <summary>
    /// 根据用户名获取用户
    /// </summary>
    /// <param name="username">用户名</param>
    /// <returns>用户信息，如果不存在返回null</returns>
    Task<User?> GetUserByUsernameAsync(string username);

    /// <summary>
    /// 创建新用户
    /// </summary>
    /// <param name="user">用户信息</param>
    /// <returns>创建的用户信息</returns>
    Task<User> CreateUserAsync(User user);

    /// <summary>
    /// 更新用户信息
    /// </summary>
    /// <param name="id">用户ID</param>
    /// <param name="user">更新的用户信息</param>
    /// <returns>更新后的用户信息，如果用户不存在返回null</returns>
    Task<User?> UpdateUserAsync(int id, User user);

    /// <summary>
    /// 删除用户
    /// </summary>
    /// <param name="id">用户ID</param>
    /// <returns>删除操作是否成功</returns>
    Task<bool> DeleteUserAsync(int id);

    /// <summary>
    /// 激活/停用用户
    /// </summary>
    /// <param name="id">用户ID</param>
    /// <param name="isActive">是否激活</param>
    /// <returns>操作是否成功</returns>
    Task<bool> SetUserActiveStatusAsync(int id, bool isActive);

    /// <summary>
    /// 根据角色获取用户
    /// </summary>
    /// <param name="role">用户角色</param>
    /// <returns>指定角色的用户列表</returns>
    Task<IEnumerable<User>> GetUsersByRoleAsync(UserRole role);
}