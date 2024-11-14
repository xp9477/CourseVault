# CourseVault - 课程资源管理系统

CourseVault 是一个简单的课程资源管理系统，帮助用户管理和组织在线学习资源。

## 功能特点

- 用户认证系统（注册/登录）
- 课程资源管理（添加/编辑/删除）
- 课程分类管理（仅管理员）
- 学习笔记功能
- 支持多个网盘平台（百度网盘/阿里云盘/夸克网盘）
- 响应式界面设计

## 快速开始

1. 运行容器

``` bash
docker run -d \
--name coursevault \
-p 5000:5000 \
-v $(pwd)/data:/app/data \
xp9477/coursevault:latest
```

2. 创建管理员账户

``` bash
docker exec -it coursevault flask create-admin admin password123
```

3. 访问 http://localhost:5000 即可使用系统
