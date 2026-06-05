-- =====================================================================
-- 二等ドローン学科クイズ — 学習進捗＆認定テスト用テーブル（追加分）
-- ※ db/schema.sql を実行済みの環境に、あとから追加で実行してください。
-- Supabase ダッシュボード → SQL Editor に貼り付けて Run（冪等）。
-- =====================================================================

create table if not exists public.user_progress (
  user_id          uuid primary key references auth.users(id) on delete cascade,
  -- 通常学習の科目別状況： { "規則": {"learned":n,"ok":n,"ng":n}, ... }
  stats            jsonb not null default '{}'::jsonb,
  -- 認定テスト（4科目×10問＝40問）
  test_attempts    int  not null default 0,     -- 受験回数
  test_last_score  int,                          -- 直近の得点(0-40)
  test_best_score  int,                          -- 最高得点
  test_passed      boolean not null default false,
  test_passed_at   timestamptz,
  test_last_detail jsonb,                         -- 直近テストの科目別 { "規則":{"correct":n,"total":10}, ... }
  updated_at       timestamptz not null default now()
);

alter table public.user_progress enable row level security;

-- 本人のみ読み書き、管理者は全員分を閲覧可
drop policy if exists "up_select" on public.user_progress;
create policy "up_select" on public.user_progress
  for select using (auth.uid() = user_id or public.is_admin());

drop policy if exists "up_insert_self" on public.user_progress;
create policy "up_insert_self" on public.user_progress
  for insert with check (auth.uid() = user_id);

drop policy if exists "up_update_self" on public.user_progress;
create policy "up_update_self" on public.user_progress
  for update using (auth.uid() = user_id);

-- 管理画面用：全受講者の進捗＋アカウント情報（管理者のみ）
create or replace function public.admin_list_progress()
returns table (
  user_id uuid,
  email text,
  full_name text,
  role text,
  stats jsonb,
  test_attempts int,
  test_last_score int,
  test_best_score int,
  test_passed boolean,
  test_passed_at timestamptz,
  progress_updated_at timestamptz,
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
    select p.id, p.email, p.full_name, p.role,
           coalesce(up.stats, '{}'::jsonb),
           coalesce(up.test_attempts, 0),
           up.test_last_score, up.test_best_score,
           coalesce(up.test_passed, false), up.test_passed_at,
           up.updated_at,
           p.created_at, u.email_confirmed_at, u.last_sign_in_at
    from public.profiles p
    join auth.users u on u.id = p.id
    left join public.user_progress up on up.user_id = p.id
    order by p.created_at desc;
end;
$$;
