-- =====================================================================
-- 二等ドローン学科クイズ — Supabase スキーマ
-- Supabase ダッシュボード → SQL Editor に貼り付けて実行してください。
-- （何度でも再実行できるよう冪等に書いています）
-- =====================================================================

-- ---- プロフィール表（氏名・役割などを保存）----
create table if not exists public.profiles (
  id          uuid primary key references auth.users(id) on delete cascade,
  email       text,
  full_name   text,
  role        text not null default 'user',   -- 'user' / 'admin'
  created_at  timestamptz not null default now()
);

alter table public.profiles enable row level security;

-- ---- 新規登録時に profiles を自動作成するトリガ ----
create or replace function public.handle_new_user()
returns trigger
language plpgsql
security definer
set search_path = public
as $$
begin
  insert into public.profiles (id, email, full_name)
  values (new.id, new.email, coalesce(new.raw_user_meta_data->>'full_name', ''))
  on conflict (id) do nothing;
  return new;
end;
$$;

drop trigger if exists on_auth_user_created on auth.users;
create trigger on_auth_user_created
  after insert on auth.users
  for each row execute function public.handle_new_user();

-- ---- 管理者判定（RLSの再帰を避けるため security definer）----
create or replace function public.is_admin()
returns boolean
language sql
security definer
set search_path = public
as $$
  select exists (
    select 1 from public.profiles
    where id = auth.uid() and role = 'admin'
  );
$$;

-- ---- RLS ポリシー ----
drop policy if exists "profiles_select" on public.profiles;
create policy "profiles_select" on public.profiles
  for select using (auth.uid() = id or public.is_admin());

drop policy if exists "profiles_update_self" on public.profiles;
create policy "profiles_update_self" on public.profiles
  for update using (auth.uid() = id);

drop policy if exists "profiles_insert_self" on public.profiles;
create policy "profiles_insert_self" on public.profiles
  for insert with check (auth.uid() = id);

-- ---- 管理画面用：全アカウント一覧（管理者のみ実行可）----
create or replace function public.admin_list_users()
returns table (
  id uuid,
  email text,
  full_name text,
  role text,
  created_at timestamptz,
  email_confirmed_at timestamptz,
  last_sign_in_at timestamptz
)
language plpgsql
security definer
set search_path = public
as $$
begin
  if not public.is_admin() then
    raise exception 'forbidden';
  end if;
  return query
    select p.id, p.email, p.full_name, p.role, p.created_at,
           u.email_confirmed_at, u.last_sign_in_at
    from public.profiles p
    join auth.users u on u.id = p.id
    order by p.created_at desc;
end;
$$;

-- =====================================================================
-- 自分を管理者にする（メールアドレスを書き換えて1回だけ実行）：
--   update public.profiles set role = 'admin' where email = 'あなたの登録メール';
-- =====================================================================
