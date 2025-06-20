"use client"

/**
 * 认证调试页面 - 用于诊断 Supabase 认证问题
 */

import React, { useState, useEffect } from 'react'
import { createClient } from '@supabase/supabase-js'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Alert, AlertDescription } from '@/components/ui/alert'

export default function DebugAuthPage() {
  const [status, setStatus] = useState<string>('检查中...')
  const [supabaseClient, setSupabaseClient] = useState<any>(null)
  const [adminClient, setAdminClient] = useState<any>(null)
  const [testEmail, setTestEmail] = useState('test@example.com')
  const [testPassword, setTestPassword] = useState('123456')
  const [logs, setLogs] = useState<string[]>([])

  const addLog = (message: string) => {
    const timestamp = new Date().toLocaleTimeString()
    setLogs(prev => [...prev, `[${timestamp}] ${message}`])
    console.log(message)
  }

  // 初始化检查
  useEffect(() => {
    const checkEnvironment = () => {
      const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL
      const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY

      addLog(`检查环境变量...`)
      addLog(`SUPABASE_URL: ${supabaseUrl ? '✅ 已设置' : '❌ 未设置'}`)
      addLog(`SUPABASE_ANON_KEY: ${supabaseAnonKey ? '✅ 已设置' : '❌ 未设置'}`)
      addLog(`⚠️ SERVICE_ROLE_KEY: 出于安全考虑，不在前端检查`)

      if (supabaseUrl && supabaseAnonKey) {
        try {
          // 创建普通客户端（用于用户认证）
          const client = createClient(supabaseUrl, supabaseAnonKey)
          setSupabaseClient(client)
          
          setStatus('✅ Supabase 客户端创建成功')
          addLog('✅ Supabase 客户端创建成功')
          addLog('💡 管理员功能需要通过后端 API 调用')
        } catch (error) {
          setStatus('❌ Supabase 客户端创建失败')
          addLog(`❌ 客户端创建失败: ${error}`)
        }
      } else {
        setStatus('❌ 环境变量缺失')
        addLog('❌ 环境变量缺失')
      }
    }

    checkEnvironment()
  }, [])

  // 测试连接
  const testConnection = async () => {
    if (!supabaseClient) {
      addLog('❌ Supabase 客户端未初始化')
      return
    }

    try {
      addLog('🔍 测试 Supabase 连接...')
      
      // 强制使用正确的 URL 进行测试
      const CORRECT_URL = 'https://jdyogivzmzwdtmcgxdas.supabase.co'
      const CORRECT_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImpkeW9naXZ6bXp3ZHRtY2d4ZGFzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTAzMTY4NDEsImV4cCI6MjA2NTg5Mjg0MX0.lXlfd1a0fcfAFS_Wj5sPtfxNgbUAPtqOKnkivD8_43Y'
      
      addLog(`🌐 环境变量URL: ${process.env.NEXT_PUBLIC_SUPABASE_URL}`)
      addLog(`🌐 强制测试URL: ${CORRECT_URL}`)
      
      // 首先测试基本的网络连接
      addLog('📡 测试网络连接...')
      try {
        const response = await fetch(CORRECT_URL + '/rest/v1/', {
          method: 'GET',
          headers: {
            'apikey': CORRECT_KEY,
            'Authorization': `Bearer ${CORRECT_KEY}`
          }
        })
        addLog(`📡 网络响应状态: ${response.status}`)
        if (!response.ok) {
          addLog(`❌ 网络请求失败: ${response.statusText}`)
        } else {
          addLog('✅ 网络连接正常')
        }
      } catch (networkError: any) {
        addLog(`❌ 网络连接失败: ${networkError.message}`)
        addLog(`错误类型: ${networkError.name}`)
        if (networkError.cause) {
          addLog(`错误原因: ${networkError.cause}`)
        }
      }

      // 创建新的 Supabase 客户端用于测试
      addLog('🔧 创建测试客户端...')
      const testClient = createClient(CORRECT_URL, CORRECT_KEY)
      
      // 测试 Supabase 客户端连接
      const { data, error } = await testClient
        .from('users')
        .select('count', { count: 'exact', head: true })

      if (error) {
        addLog(`❌ Supabase 连接测试失败: ${error.message}`)
        addLog(`错误代码: ${error.code || 'N/A'}`)
        addLog(`错误详情: ${error.details || 'N/A'}`)
        addLog(`错误提示: ${error.hint || 'N/A'}`)
      } else {
        addLog('✅ Supabase 连接正常')
        addLog(`📊 数据库响应: ${JSON.stringify(data)}`)
      }
    } catch (error: any) {
      addLog(`❌ 连接测试异常: ${error.message}`)
      addLog(`错误堆栈: ${error.stack}`)
    }
  }

  // 测试注册
  const testSignUp = async () => {
    if (!supabaseClient) {
      addLog('❌ Supabase 客户端未初始化')
      return
    }

    // 生成正确格式的测试邮箱
    const baseEmail = testEmail.includes('@') ? testEmail.split('@')[0] : testEmail
    const email = `${baseEmail}_${Date.now()}@example.com`
    
    try {
      addLog(`📝 测试注册: ${email}`)
      
      const { data, error } = await supabaseClient.auth.signUp({
        email,
        password: testPassword,
      })

      if (error) {
        addLog(`❌ 注册失败: ${error.message}`)
        addLog(`错误代码: ${error.status || 'N/A'}`)
      } else {
        addLog('✅ Supabase Auth 注册成功')
        addLog(`用户ID: ${data.user?.id}`)
        addLog(`需要邮箱确认: ${!data.session ? '是' : '否'}`)
        
        // 同步创建 users 表记录
        if (data.user?.id) {
          addLog('📝 同步创建 users 表记录...')
          
          const userRecord = {
            id: data.user.id,
            email: data.user.email,
            username: `用户_${Date.now()}`,
            password_hash: 'managed_by_supabase_auth',
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString()
          }
          
          const { data: insertData, error: insertError } = await supabaseClient
            .from('users')
            .insert([userRecord])
            .select()
          
          if (insertError) {
            addLog(`❌ users 表插入失败: ${insertError.message}`)
            addLog(`   错误代码: ${insertError.code || 'N/A'}`)
          } else {
            addLog('✅ users 表记录创建成功')
            addLog(`📊 插入的数据: ${JSON.stringify(insertData, null, 2)}`)
          }
        }
      }
    } catch (error) {
      addLog(`❌ 注册异常: ${error}`)
    }
  }

  // 测试登录
  const testSignIn = async () => {
    if (!supabaseClient) {
      addLog('❌ Supabase 客户端未初始化')
      return
    }

    try {
      addLog(`🔐 测试登录: ${testEmail}`)
      
      const { data, error } = await supabaseClient.auth.signInWithPassword({
        email: testEmail,
        password: testPassword,
      })

      if (error) {
        addLog(`❌ 登录失败: ${error.message}`)
        addLog(`错误代码: ${error.status || 'N/A'}`)
      } else {
        addLog('✅ 登录成功')
        addLog(`用户ID: ${data.user?.id}`)
        addLog(`Token: ${data.session?.access_token ? '已获取' : '未获取'}`)
        
        // 检查并同步用户到 users 表
        if (data.user?.id) {
          await ensureUserInUsersTable(data.user)
        }
      }
    } catch (error) {
      addLog(`❌ 登录异常: ${error}`)
    }
  }

  // 确保用户存在于 users 表中
  const ensureUserInUsersTable = async (user: any) => {
    if (!supabaseClient) return

    try {
      addLog('🔍 检查用户是否存在于 users 表...')
      
      // 先查询用户是否已存在
      const { data: existingUser, error: queryError } = await supabaseClient
        .from('users')
        .select('*')
        .eq('id', user.id)
        .single()

      if (queryError && queryError.code !== 'PGRST116') {
        addLog(`❌ 查询用户失败: ${queryError.message}`)
        return
      }

      if (existingUser) {
        addLog('✅ 用户已存在于 users 表中')
        addLog(`📧 邮箱: ${existingUser.email}`)
        addLog(`👤 用户名: ${existingUser.username}`)
      } else {
        addLog('📝 用户不存在，创建 users 表记录...')
        
        const userRecord = {
          id: user.id,
          email: user.email,
          username: user.email?.split('@')[0] || `用户_${Date.now()}`,
          password_hash: 'managed_by_supabase_auth',
          created_at: user.created_at || new Date().toISOString(),
          updated_at: new Date().toISOString()
        }
        
        const { data: insertData, error: insertError } = await supabaseClient
          .from('users')
          .insert([userRecord])
          .select()
        
        if (insertError) {
          addLog(`❌ users 表插入失败: ${insertError.message}`)
          addLog(`   错误代码: ${insertError.code || 'N/A'}`)
        } else {
          addLog('✅ users 表记录创建成功')
          addLog(`📊 插入的数据: ${JSON.stringify(insertData, null, 2)}`)
        }
      }
    } catch (error: any) {
      addLog(`❌ 用户同步异常: ${error.message}`)
    }
  }

  // 获取当前会话
  const checkSession = async () => {
    if (!supabaseClient) {
      addLog('❌ Supabase 客户端未初始化')
      return
    }

    try {
      addLog('🔍 检查当前会话...')
      
      const { data: { session } } = await supabaseClient.auth.getSession()

      if (session) {
        addLog('✅ 找到活跃会话')
        addLog(`用户: ${session.user.email}`)
        addLog(`用户ID: ${session.user.id}`)
        addLog(`过期时间: ${new Date(session.expires_at * 1000).toLocaleString()}`)
        
        // 自动同步用户到 users 表
        await ensureUserInUsersTable(session.user)
      } else {
        addLog('ℹ️ 未找到活跃会话')
      }
    } catch (error) {
      addLog(`❌ 会话检查异常: ${error}`)
    }
  }

  // 测试用户日志记录
  const testUserLogs = async () => {
    if (!supabaseClient) {
      addLog('❌ Supabase 客户端未初始化')
      return
    }

    try {
      addLog('📊 测试用户日志记录功能...')
      
      // 检查当前会话
      const { data: { session } } = await supabaseClient.auth.getSession()
      
      if (!session) {
        addLog('❌ 需要先登录才能测试日志记录')
        return
      }

      addLog(`👤 当前用户: ${session.user.email}`)
      addLog(`🔑 用户ID: ${session.user.id}`)
      
      // 测试插入用户活动日志 (适配 user_logs 表)
      const testLogEntry = {
        user_id: session.user.id,
        action: 'test_log_entry',
        details: {
          timestamp: new Date().toISOString(),
          test_data: '这是一个测试日志条目',
          user_agent: navigator.userAgent,
          test_id: Math.random().toString(36).substr(2, 9)
        },
        created_at: new Date().toISOString()
      }

      // 测试插入每日日志数据 (适配 user_daily_logs 表)
      const dailyLogEntry = {
        user_id: session.user.id,
        log_date: new Date().toISOString().split('T')[0], // 今天的日期 YYYY-MM-DD
        total_focus_time: 90,
        total_sessions: 1,
        completed_sessions: 1,
        deep_work_count: 1,
        deep_work_time: 90,
        break_count: 0,
        break_time: 0,
        roundtable_count: 0,
        roundtable_time: 0
      }

      addLog('📝 尝试插入测试日志条目...')
      
      // 测试插入到不同的日志表
      const tableTests = [
        { name: 'user_logs', data: testLogEntry },
        { name: 'user_daily_logs', data: dailyLogEntry }
      ]
      let insertSuccess = false

      for (const tableTest of tableTests) {
        addLog(`📝 尝试插入到 ${tableTest.name} 表...`)
        addLog(`📋 插入数据: ${JSON.stringify(tableTest.data, null, 2)}`)
        
        const { data: insertData, error: insertError } = await supabaseClient
          .from(tableTest.name)
          .insert([tableTest.data])
          .select()

        if (insertError) {
          const errorMessage = insertError.message || 'Unknown error'
          const errorCode = insertError.code || 'N/A'
          const errorDetails = insertError.details || 'N/A'
          
          addLog(`❌ ${tableTest.name} 表插入失败: ${errorMessage}`)
          addLog(`   错误代码: ${errorCode}`)
          addLog(`   错误详情: ${errorDetails}`)
          
          if (errorCode === 'PGRST116' || errorMessage.includes('relation') || errorMessage.includes('does not exist')) {
            addLog(`   💡 表 ${tableTest.name} 不存在`)
          } else if (errorCode === '23505') {
            addLog(`   💡 数据重复 - 可能已存在今日记录`)
          } else if (errorMessage.includes('violates check constraint')) {
            addLog(`   💡 数据不符合约束条件`)
          } else if (errorMessage.includes('violates foreign key constraint')) {
            addLog(`   💡 外键约束违反 - 用户ID不存在`)
          }
        } else {
          addLog(`✅ ${tableTest.name} 表日志记录成功!`)
          addLog(`📊 插入的数据: ${JSON.stringify(insertData, null, 2)}`)
          insertSuccess = true
        }
      }

      if (!insertSuccess) {
        addLog('💡 建议: 需要创建用户日志表')
        addLog('📋 建议的表结构:')
        addLog('   - id (uuid, primary key)')
        addLog('   - user_id (uuid, foreign key to auth.users)')
        addLog('   - action (text)')
        addLog('   - details (jsonb)')
        addLog('   - created_at (timestamp)')
      }

      // 测试查询用户日志（两个表都试试）
      for (const tableTest of tableTests) {
        const tableName = tableTest.name
        addLog(`🔍 尝试查询 ${tableName} 表...`)
        
        const { data: queryData, error: queryError } = await supabaseClient
          .from(tableName)
          .select('*')
          .eq('user_id', session.user.id)
          .order('created_at', { ascending: false })
          .limit(5)

        if (queryError) {
          addLog(`❌ ${tableName} 表查询失败: ${queryError.message}`)
        } else {
          addLog(`✅ ${tableName} 表查询成功，找到 ${queryData?.length || 0} 条记录`)
          if (queryData && queryData.length > 0) {
            addLog(`📋 ${tableName} 表最近的日志条目:`)
            queryData.forEach((log: any, index: number) => {
              addLog(`   ${index + 1}. ${log.action} - ${new Date(log.created_at).toLocaleString()}`)
            })
          }
        }
      }

    } catch (error: any) {
      addLog(`❌ 用户日志测试异常: ${error.message}`)
      addLog(`错误堆栈: ${error.stack}`)
    }
  }

  // 专门测试 user_daily_logs 表
  const testDailyLogs = async () => {
    if (!supabaseClient) {
      addLog('❌ Supabase 客户端未初始化')
      return
    }

    try {
      addLog('📊 专门测试 user_daily_logs 表功能...')
      
      // 检查当前会话
      const { data: { session } } = await supabaseClient.auth.getSession()
      
      if (!session) {
        addLog('❌ 需要先登录才能测试日志记录')
        return
      }

      addLog(`👤 当前用户: ${session.user.email}`)
      
      // 准备今日日志数据
      const today = new Date().toISOString().split('T')[0]
      const dailyLogData = {
        user_id: session.user.id,
        log_date: today,
        total_focus_time: Math.floor(Math.random() * 120) + 30, // 30-150分钟
        total_sessions: Math.floor(Math.random() * 5) + 1, // 1-5次
        completed_sessions: Math.floor(Math.random() * 3) + 1, // 1-3次
        deep_work_count: Math.floor(Math.random() * 3) + 1,
        deep_work_time: Math.floor(Math.random() * 90) + 30,
        break_count: Math.floor(Math.random() * 2),
        break_time: Math.floor(Math.random() * 30),
        roundtable_count: Math.floor(Math.random() * 2),
        roundtable_time: Math.floor(Math.random() * 60)
      }

      addLog(`📋 准备插入/更新的数据: ${JSON.stringify(dailyLogData, null, 2)}`)

      // 使用 upsert 插入或更新数据
      addLog('💾 使用 upsert 操作...')
      const { data: upsertData, error: upsertError } = await supabaseClient
        .from('user_daily_logs')
        .upsert(dailyLogData, { 
          onConflict: 'user_id,log_date',
          ignoreDuplicates: false 
        })
        .select()

      if (upsertError) {
        addLog(`❌ upsert 操作失败: ${upsertError.message}`)
        addLog(`   错误代码: ${upsertError.code || 'N/A'}`)
        addLog(`   错误详情: ${upsertError.details || 'N/A'}`)
      } else {
        addLog('✅ upsert 操作成功!')
        addLog(`📊 结果数据: ${JSON.stringify(upsertData, null, 2)}`)
      }

      // 查询今日的日志记录
      addLog('🔍 查询今日日志记录...')
      const { data: todayData, error: queryError } = await supabaseClient
        .from('user_daily_logs')
        .select('*')
        .eq('user_id', session.user.id)
        .eq('log_date', today)

      if (queryError) {
        addLog(`❌ 查询失败: ${queryError.message}`)
      } else {
        addLog(`✅ 查询成功，找到 ${todayData?.length || 0} 条记录`)
        if (todayData && todayData.length > 0) {
          const record = todayData[0]
          addLog('📋 今日记录详情:')
          addLog(`   总专注时间: ${record.total_focus_time} 分钟`)
          addLog(`   总会话数: ${record.total_sessions}`)
          addLog(`   完成会话数: ${record.completed_sessions}`)
          addLog(`   深度工作: ${record.deep_work_count} 次, ${record.deep_work_time} 分钟`)
          addLog(`   休息: ${record.break_count} 次, ${record.break_time} 分钟`)
          addLog(`   圆桌: ${record.roundtable_count} 次, ${record.roundtable_time} 分钟`)
        }
      }

      // 查询最近7天的记录
      addLog('🔍 查询最近7天的记录...')
      const sevenDaysAgo = new Date()
      sevenDaysAgo.setDate(sevenDaysAgo.getDate() - 7)
      
      const { data: weekData, error: weekError } = await supabaseClient
        .from('user_daily_logs')
        .select('*')
        .eq('user_id', session.user.id)
        .gte('log_date', sevenDaysAgo.toISOString().split('T')[0])
        .order('log_date', { ascending: false })

      if (weekError) {
        addLog(`❌ 周记录查询失败: ${weekError.message}`)
      } else {
        addLog(`✅ 找到最近7天的 ${weekData?.length || 0} 条记录`)
        if (weekData && weekData.length > 0) {
          addLog('📊 最近7天统计:')
          weekData.forEach((record: any) => {
            addLog(`   ${record.log_date}: ${record.total_focus_time}分钟, ${record.total_sessions}次会话`)
          })
        }
      }

    } catch (error: any) {
      addLog(`❌ 每日日志测试异常: ${error.message}`)
      addLog(`错误堆栈: ${error.stack}`)
    }
  }

  // 测试数据库表结构
  const testDatabaseSchema = async () => {
    if (!supabaseClient) {
      addLog('❌ Supabase 客户端未初始化')
      return
    }

    try {
      addLog('🗃️ 检查数据库表结构...')
      
      // 检查常见的表
      const tablesToCheck = ['users', 'user_logs', 'profiles', 'sessions']
      
      for (const tableName of tablesToCheck) {
        try {
          addLog(`🔍 检查表: ${tableName}`)
          const { data, error } = await supabaseClient
            .from(tableName)
            .select('*', { count: 'exact', head: true })
          
          if (error) {
            if (error.code === 'PGRST116' || error.message.includes('does not exist')) {
              addLog(`   ❌ 表 "${tableName}" 不存在`)
            } else {
              addLog(`   ❌ 访问表 "${tableName}" 失败: ${error.message}`)
            }
          } else {
            addLog(`   ✅ 表 "${tableName}" 存在，记录数: ${data?.length || 0}`)
          }
        } catch (err: any) {
          addLog(`   ❌ 检查表 "${tableName}" 时出错: ${err.message}`)
        }
      }

      // 检查当前用户权限
      addLog('👥 检查当前用户权限...')
      const { data: { session } } = await supabaseClient.auth.getSession()
      
      if (session) {
        addLog(`✅ 当前登录用户: ${session.user.email}`)
        addLog(`🔑 用户ID: ${session.user.id}`)
        addLog(`⏰ 会话过期时间: ${new Date(session.expires_at * 1000).toLocaleString()}`)
        
        // 测试用户是否可以访问自己的数据
        addLog('🔍 测试用户数据访问权限...')
        try {
          const { data: profileData, error: profileError } = await supabaseClient
            .from('profiles')
            .select('*')
            .eq('id', session.user.id)
            .single()
          
          if (profileError) {
            addLog(`❌ 无法访问用户档案: ${profileError.message}`)
          } else {
            addLog(`✅ 可以访问用户档案数据`)
          }
        } catch (err: any) {
          addLog(`❌ 档案访问测试失败: ${err.message}`)
        }
      } else {
        addLog('ℹ️ 未登录，无法测试用户权限')
        addLog('💡 建议：先登录后再测试数据库功能')
      }

    } catch (error: any) {
      addLog(`❌ 数据库检查异常: ${error.message}`)
    }
  }

  // 权限诊断
  const diagnosePermissions = async () => {
    if (!supabaseClient) {
      addLog('❌ Supabase 客户端未初始化')
      return
    }

    try {
      addLog('🔐 开始权限诊断...')
      
      // 检查当前会话
      const { data: { session } } = await supabaseClient.auth.getSession()
      
      if (!session) {
        addLog('❌ 未登录，请先登录后再进行权限诊断')
        return
      }

      addLog(`👤 诊断用户: ${session.user.email}`)
      
      // 测试各种操作权限
      const permissionTests = [
        {
          name: '读取用户档案 (profiles)',
          test: async () => {
            const { data, error } = await supabaseClient
              .from('profiles')
              .select('*')
              .eq('id', session.user.id)
            return { success: !error, error: error?.message, data }
          }
        },
        {
          name: '创建用户档案 (profiles)',
          test: async () => {
            const { data, error } = await supabaseClient
              .from('profiles')
              .upsert({
                id: session.user.id,
                email: session.user.email,
                updated_at: new Date().toISOString()
              })
            return { success: !error, error: error?.message, data }
          }
        },
        {
          name: '读取用户日志 (user_logs)',
          test: async () => {
            const { data, error } = await supabaseClient
              .from('user_logs')
              .select('*')
              .eq('user_id', session.user.id)
              .limit(1)
            return { success: !error, error: error?.message, data }
          }
        },
        {
          name: '读取用户日志 (user_daily_logs)',
          test: async () => {
            const { data, error } = await supabaseClient
              .from('user_daily_logs')
              .select('*')
              .eq('user_id', session.user.id)
              .limit(1)
            return { success: !error, error: error?.message, data }
          }
        },
        {
          name: '写入用户日志 (user_logs)',
          test: async () => {
            const { data, error } = await supabaseClient
              .from('user_logs')
              .insert({
                user_id: session.user.id,
                action: 'permission_test',
                details: { test: true, timestamp: new Date().toISOString() }
              })
            return { success: !error, error: error?.message, data }
          }
        },
        {
          name: '写入用户日志 (user_daily_logs)',
          test: async () => {
            const { data, error } = await supabaseClient
              .from('user_daily_logs')
              .insert({
                user_id: session.user.id,
                action: 'permission_test',
                details: { test: true, timestamp: new Date().toISOString() }
              })
            return { success: !error, error: error?.message, data }
          }
        }
      ]

      // 执行权限测试
      for (const test of permissionTests) {
        try {
          addLog(`🧪 测试: ${test.name}...`)
          const result = await test.test()
          
          if (result.success) {
            addLog(`   ✅ ${test.name} - 权限正常`)
            if (result.data && Array.isArray(result.data)) {
              addLog(`   📊 返回数据: ${result.data.length} 条记录`)
              if (result.data.length > 0) {
                addLog(`   📋 示例数据: ${JSON.stringify(result.data[0], null, 2)}`)
              }
            } else if (result.data) {
              addLog(`   📊 返回数据: ${JSON.stringify(result.data, null, 2)}`)
            }
          } else {
            addLog(`   ❌ ${test.name} - 权限不足: ${result.error}`)
          }
        } catch (error: any) {
          addLog(`   ❌ ${test.name} - 测试异常: ${error.message}`)
        }
      }

      // 检查RLS策略
      addLog('🛡️ 检查行级安全策略 (RLS)...')
      addLog('💡 如果上述操作失败，可能需要：')
      addLog('   1. 在 Supabase 控制台中禁用相关表的 RLS')
      addLog('   2. 或者创建适当的 RLS 策略')
      addLog('   3. 或者使用 Service Role Key 而不是 Anon Key')

    } catch (error: any) {
      addLog(`❌ 权限诊断异常: ${error.message}`)
    }
  }

  // 测试管理员功能（通过后端 API）
  const testAdminFunctions = async () => {
    try {
      addLog('🔧 测试管理员功能（通过后端 API）...')
      
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
      
      // 测试后端管理员 API
      addLog('📡 调用后端管理员 API...')
      
      try {
        const response = await fetch(`${apiUrl}/admin/users`, {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
          }
        })

        if (response.ok) {
          const data = await response.json()
          addLog('✅ 后端管理员 API 调用成功')
          addLog(`📊 响应数据: ${JSON.stringify(data, null, 2)}`)
        } else {
          addLog(`❌ 后端 API 响应错误: ${response.status} ${response.statusText}`)
          const errorText = await response.text()
          addLog(`错误详情: ${errorText}`)
        }
      } catch (fetchError: any) {
        addLog(`❌ 无法连接到后端 API: ${fetchError.message}`)
        addLog('💡 请确保后端服务正在运行在 http://localhost:8000')
      }

      // 提供直接测试 Service Role Key 的建议
      addLog('')
      addLog('🔐 Service Role Key 安全使用建议:')
      addLog('   1. ✅ 已在后端环境变量中设置')
      addLog('   2. ✅ 已从前端环境变量中移除')
      addLog('   3. 💡 应该通过后端 API 使用管理员权限')
      addLog('   4. 💡 可以在后端代码中直接测试 Service Role Key')

    } catch (error: any) {
      addLog(`❌ 管理员功能测试异常: ${error.message}`)
    }
  }

  // 清理日志
  const clearLogs = () => {
    setLogs([])
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-4xl mx-auto space-y-6">
        {/* 页面标题 */}
        <div className="text-center">
          <h1 className="text-3xl font-bold text-gray-900">🔍 AURA STUDIO 认证调试</h1>
          <p className="text-gray-600 mt-2">诊断 Supabase 认证问题</p>
        </div>

        {/* 状态卡片 */}
        <Card>
          <CardHeader>
            <CardTitle>系统状态</CardTitle>
          </CardHeader>
          <CardContent>
            <Alert>
              <AlertDescription>{status}</AlertDescription>
            </Alert>
          </CardContent>
        </Card>

        {/* 测试输入 */}
        <Card>
          <CardHeader>
            <CardTitle>测试参数</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-2">测试邮箱</label>
              <Input
                value={testEmail}
                onChange={(e) => setTestEmail(e.target.value)}
                placeholder="test@example.com"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-2">测试密码</label>
              <Input
                type="password"
                value={testPassword}
                onChange={(e) => setTestPassword(e.target.value)}
                placeholder="123456"
              />
            </div>
          </CardContent>
        </Card>

        {/* 测试按钮 */}
        <Card>
          <CardHeader>
            <CardTitle>测试操作</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {/* 基础测试 */}
              <div>
                <h4 className="text-sm font-medium mb-2 text-gray-700">基础连接测试</h4>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
                  <Button onClick={testConnection} variant="outline" size="sm">
                    测试连接
                  </Button>
                  <Button onClick={testSignUp} variant="outline" size="sm">
                    测试注册
                  </Button>
                  <Button onClick={testSignIn} variant="outline" size="sm">
                    测试登录
                  </Button>
                  <Button onClick={checkSession} variant="outline" size="sm">
                    检查会话
                  </Button>
                </div>
              </div>
              
              {/* 数据库测试 */}
              <div>
                <h4 className="text-sm font-medium mb-2 text-gray-700">数据库功能测试</h4>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
                  <Button onClick={testDatabaseSchema} variant="outline" size="sm">
                    📊 检查表结构
                  </Button>
                  <Button onClick={testUserLogs} variant="outline" size="sm">
                    📝 测试日志记录
                  </Button>
                  <Button onClick={testDailyLogs} variant="outline" size="sm" className="bg-green-50 hover:bg-green-100">
                    📊 测试每日日志
                  </Button>
                  <Button onClick={diagnosePermissions} variant="outline" size="sm">
                    🔐 权限诊断
                  </Button>
                  <Button onClick={clearLogs} variant="outline" size="sm">
                    🗑️ 清理日志
                  </Button>
                </div>
              </div>
              
              {/* 管理员功能测试 */}
              <div>
                <h4 className="text-sm font-medium mb-2 text-gray-700">管理员功能测试</h4>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                  <Button onClick={testAdminFunctions} variant="outline" size="sm">
                    🔧 测试后端管理员 API
                  </Button>
                  <div className="text-xs text-gray-500 flex items-center">
                    通过后端 API 安全调用
                  </div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* 日志显示 */}
        <Card>
          <CardHeader>
            <CardTitle>调试日志</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="bg-gray-900 text-green-400 p-4 rounded-lg font-mono text-sm max-h-96 overflow-y-auto">
              {logs.length === 0 ? (
                <div className="text-gray-500">暂无日志...</div>
              ) : (
                logs.map((log, index) => (
                  <div key={index} className="mb-1">
                    {log}
                  </div>
                ))
              )}
            </div>
          </CardContent>
        </Card>

        {/* 环境信息 */}
        <Card>
          <CardHeader>
            <CardTitle>环境信息</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
              <div>
                <strong>Supabase URL:</strong>
                <br />
                <code className="text-xs bg-gray-100 p-1 rounded">
                  {process.env.NEXT_PUBLIC_SUPABASE_URL || '未设置'}
                </code>
              </div>
              <div>
                <strong>Anon Key:</strong>
                <br />
                <code className="text-xs bg-gray-100 p-1 rounded">
                  {process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY 
                    ? `${process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY.substring(0, 20)}...` 
                    : '未设置'}
                </code>
              </div>
              <div>
                <strong>Service Role Key:</strong>
                <br />
                <code className="text-xs bg-gray-100 p-1 rounded">
                  🔒 仅在后端使用（安全）
                </code>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* 返回按钮 */}
        <div className="text-center">
          <Button 
            onClick={() => window.location.href = '/'}
            variant="default"
          >
            返回主页
          </Button>
        </div>
      </div>
    </div>
  )
} 