-- 自动同步 auth.users 到 public.users 的触发器
-- 在 Supabase SQL Editor 中执行此脚本

-- 创建触发器函数
CREATE OR REPLACE FUNCTION sync_user_to_public_users()
RETURNS TRIGGER AS $$
BEGIN
  -- 当 auth.users 中有新用户时，自动在 public.users 中创建对应记录
  INSERT INTO public.users (
    id,
    email,
    username,
    password_hash,
    created_at,
    updated_at
  ) VALUES (
    NEW.id,
    NEW.email,
    COALESCE(NEW.raw_user_meta_data->>'username', '用户_' || extract(epoch from now())),
    'managed_by_supabase_auth',
    NEW.created_at,
    NEW.updated_at
  )
  ON CONFLICT (id) DO UPDATE SET
    email = EXCLUDED.email,
    updated_at = EXCLUDED.updated_at;
  
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 创建触发器
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
  AFTER INSERT OR UPDATE ON auth.users
  FOR EACH ROW
  EXECUTE FUNCTION sync_user_to_public_users();

-- 为现有的 auth.users 补充 public.users 记录
INSERT INTO public.users (
  id,
  email,
  username,
  password_hash,
  created_at,
  updated_at
)
SELECT 
  au.id,
  au.email,
  COALESCE(au.raw_user_meta_data->>'username', '用户_' || extract(epoch from au.created_at)),
  'managed_by_supabase_auth',
  au.created_at,
  au.updated_at
FROM auth.users au
LEFT JOIN public.users pu ON au.id = pu.id
WHERE pu.id IS NULL;

-- 验证同步结果
SELECT 
  'auth.users' as table_name,
  count(*) as user_count
FROM auth.users
UNION ALL
SELECT 
  'public.users' as table_name,
  count(*) as user_count  
FROM public.users; 