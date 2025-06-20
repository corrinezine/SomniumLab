#!/usr/bin/env node

/**
 * AURA STUDIO - 前端 Supabase 连接诊断工具
 * 
 * 这个脚本帮助诊断前端与 Supabase 的连接问题
 * 使用方法：node frontend-diagnosis.js
 */

const fs = require('fs');
const path = require('path');

console.log('🔍 AURA STUDIO 前端 Supabase 连接诊断');
console.log('=' .repeat(50));

// 1. 检查环境变量文件
console.log('\n📋 步骤 1: 检查环境变量文件...');

const envLocalPath = path.join(__dirname, '.env.local');
const envExists = fs.existsSync(envLocalPath);

console.log(`✅ .env.local 文件: ${envExists ? '存在' : '❌ 不存在'}`);

if (envExists) {
    try {
        const envContent = fs.readFileSync(envLocalPath, 'utf8');
        const lines = envContent.split('\n').filter(line => line.trim() && !line.startsWith('#'));
        
        console.log(`📝 环境变量数量: ${lines.length}`);
        
        // 检查必需的环境变量
        const requiredVars = [
            'NEXT_PUBLIC_SUPABASE_URL',
            'NEXT_PUBLIC_SUPABASE_ANON_KEY',
            'NEXT_PUBLIC_API_URL'
        ];
        
        const envVars = {};
        lines.forEach(line => {
            const [key, value] = line.split('=');
            if (key && value) {
                envVars[key.trim()] = value.trim();
            }
        });
        
        requiredVars.forEach(varName => {
            const exists = envVars[varName];
            const status = exists ? '✅' : '❌';
            const preview = exists ? `${exists.substring(0, 20)}...` : '未设置';
            console.log(`   ${status} ${varName}: ${preview}`);
        });
        
    } catch (error) {
        console.log(`❌ 读取 .env.local 失败: ${error.message}`);
    }
} else {
    console.log('❌ 请先创建 .env.local 文件');
}

// 2. 检查 package.json 依赖
console.log('\n📋 步骤 2: 检查依赖包...');

const packageJsonPath = path.join(__dirname, 'package.json');
if (fs.existsSync(packageJsonPath)) {
    try {
        const packageJson = JSON.parse(fs.readFileSync(packageJsonPath, 'utf8'));
        const dependencies = { ...packageJson.dependencies, ...packageJson.devDependencies };
        
        const requiredPackages = [
            '@supabase/supabase-js',
            'next',
            'react'
        ];
        
        requiredPackages.forEach(pkg => {
            const version = dependencies[pkg];
            const status = version ? '✅' : '❌';
            console.log(`   ${status} ${pkg}: ${version || '未安装'}`);
        });
        
    } catch (error) {
        console.log(`❌ 读取 package.json 失败: ${error.message}`);
    }
} else {
    console.log('❌ package.json 文件不存在');
}

// 3. 检查关键文件
console.log('\n📋 步骤 3: 检查关键文件...');

const keyFiles = [
    'components/auth/AuthProvider.tsx',
    'components/auth/LoginForm.tsx', 
    'app/auth-test/page.tsx',
    'app/debug-auth/page.tsx'
];

keyFiles.forEach(file => {
    const exists = fs.existsSync(path.join(__dirname, file));
    const status = exists ? '✅' : '❌';
    console.log(`   ${status} ${file}`);
});

// 4. 生成测试建议
console.log('\n📋 步骤 4: 测试建议...');

console.log('🚀 接下来请按以下步骤测试:');
console.log('   1. 重启 Next.js 开发服务器: npm run dev 或 pnpm dev');
console.log('   2. 访问调试页面: http://localhost:3000/debug-auth');
console.log('   3. 检查浏览器控制台是否有错误');
console.log('   4. 测试注册和登录功能');

console.log('\n🔧 如果仍有问题，请检查:');
console.log('   - Supabase 项目状态是否正常');
console.log('   - 网络连接是否稳定');
console.log('   - API Key 是否有效');
console.log('   - 后端服务是否运行在 http://localhost:8000');

console.log('\n✨ 诊断完成！'); 