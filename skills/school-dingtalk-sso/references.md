# 钉钉官方文档

## 工作台免登

- 在工作台网页中获取授权码。授权码五分钟内有效且只能使用一次。[requestAuthCode](https://open.dingtalk.com/document/orgapp/jsapi-request-auth-code)
- 在服务端用应用凭证获取访问令牌并按应用缓存。[获取企业内部应用的 accessToken](https://open.dingtalk.com/document/orgapp/obtain-the-access_token-of-an-internal-app)
- 用应用访问令牌和授权码换取身份，从成功响应读取 `result.userid` 和 `result.unionid`。[通过免登码获取用户信息](https://open.dingtalk.com/document/orgapp-server/obtain-the-userid-of-a-user-by-using-the-log-free)
- `unionid` 在同一个开发者企业账号内唯一且稳定。核对目标应用的开发者归属后再使用 `unionid` 查找组织成员。[根据 unionid 获取用户 userid](https://open.dingtalk.com/document/orgapp-server/query-a-user-by-the-union-id)

## 通讯录与权限映射

- 按组织内的 `userid` 查询成员详情。使用角色 ID 和部门 ID 做映射，职位 `title` 用于展示。[查询用户详情](https://open.dingtalk.com/document/orgapp-server/query-user-details.md)
- 核对成员读取权限、应用通讯录授权范围和字段权限。工作台发布可见范围和通讯录授权范围需要分别确认。[通讯录权限](https://open.dingtalk.com/document/app/address-book-permissions.md)
