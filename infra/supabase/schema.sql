create extension if not exists "pgcrypto";

create table integrations (
  id uuid primary key default gen_random_uuid(),
  provider text not null,
  account_email text,
  access_token_encrypted text,
  refresh_token_encrypted text,
  scopes text[],
  metadata jsonb,
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);

create table agent_runs (
  id uuid primary key default gen_random_uuid(),
  run_type text not null,
  status text not null,
  input jsonb,
  output jsonb,
  error text,
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);

create table tool_calls (
  id uuid primary key default gen_random_uuid(),
  run_id uuid references agent_runs(id),
  tool_name text not null,
  risk_level text not null,
  input_summary text,
  output_summary text,
  status text not null,
  error text,
  created_at timestamptz default now()
);

create table daily_briefs (
  id uuid primary key default gen_random_uuid(),
  brief_date date not null,
  summary text not null,
  payload jsonb,
  created_at timestamptz default now()
);

create table tasks (
  id uuid primary key default gen_random_uuid(),
  title text not null,
  description text,
  source text,
  status text default 'open',
  priority text,
  due_at timestamptz,
  metadata jsonb,
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);

create table memories (
  id uuid primary key default gen_random_uuid(),
  type text not null,
  content text not null,
  metadata jsonb,
  created_at timestamptz default now()
);

create table approvals (
  id uuid primary key default gen_random_uuid(),
  action_type text not null,
  risk_level text not null,
  preview text not null,
  payload jsonb,
  status text default 'pending',
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);
