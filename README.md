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

``` bash
docker run -d \
--name coursevault \
-p 5000:5000 \
-v $(pwd)/data:/coursevault/app/data \
-e ADMIN_USERNAME=admin \
-e ADMIN_PASSWORD=password123 \
xp9477/coursevault:latest
```

访问 http://localhost:5000 即可使用系统

