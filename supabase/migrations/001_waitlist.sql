-- El Club de las Emprendedoras · waitlist
-- Anyone with the publishable/anon key can INSERT. Nobody can read rows with it.
-- Read signups from the Supabase dashboard or with the service role key.

create table if not exists public.waitlist (
  id uuid primary key default gen_random_uuid(),
  created_at timestamptz not null default now(),
  name text not null check (char_length(name) between 1 and 120),
  email text not null check (
    char_length(email) <= 254 and email ~* '^[^@\s]+@[^@\s]+\.[^@\s]{2,}$'
  ),
  source text not null default 'landing-2027' check (char_length(source) <= 60),
  utm_source text check (char_length(utm_source) <= 200),
  utm_medium text check (char_length(utm_medium) <= 200),
  utm_campaign text check (char_length(utm_campaign) <= 200),
  utm_content text check (char_length(utm_content) <= 200),
  referrer text check (char_length(referrer) <= 500)
);

-- One spot per email (case-insensitive). Duplicates return HTTP 409,
-- which the landing treats as success.
create unique index if not exists waitlist_email_unique on public.waitlist (lower(email));

alter table public.waitlist enable row level security;

drop policy if exists "Anyone can join the waitlist" on public.waitlist;
create policy "Anyone can join the waitlist"
  on public.waitlist
  for insert
  to anon, authenticated
  with check (true);

-- Column-level grant so the browser can only write these fields.
revoke all on public.waitlist from anon, authenticated;
grant insert (name, email, source, utm_source, utm_medium, utm_campaign, utm_content, referrer)
  on public.waitlist to anon, authenticated;
