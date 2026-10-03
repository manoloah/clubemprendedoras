-- El Club de las Emprendedoras · waitlist
-- The browser never touches the table directly. It calls the join_waitlist()
-- function, which:
--   * returns the same empty response whether the email is new or already
--     on the list (no way to probe who signed up),
--   * validates and normalises input on the server,
--   * applies a global throttle so a script can't flood the table.
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

-- One spot per email (case-insensitive).
create unique index if not exists waitlist_email_unique on public.waitlist (lower(email));
create index if not exists waitlist_created_at_idx on public.waitlist (created_at desc);

-- RLS on with no policies: anon/authenticated cannot read or write the table.
alter table public.waitlist enable row level security;
revoke all on public.waitlist from anon, authenticated;

create or replace function public.join_waitlist(
  p_name text,
  p_email text,
  p_source text default 'landing-2027',
  p_utm_source text default null,
  p_utm_medium text default null,
  p_utm_campaign text default null,
  p_utm_content text default null,
  p_referrer text default null
)
returns void
language plpgsql
security definer
set search_path = public
as $$
declare
  v_name text := left(btrim(regexp_replace(coalesce(p_name, ''), '\s+', ' ', 'g')), 120);
  v_email text := lower(btrim(coalesce(p_email, '')));
begin
  if v_name = '' or char_length(v_email) > 254
     or v_email !~* '^[^@\s]+@[^@\s]+\.[^@\s]{2,}$' then
    raise exception 'invalid_input' using errcode = '22023';
  end if;

  -- Global throttle: a real launch spike is well under this; a script is not.
  if (select count(*) from public.waitlist
      where created_at > now() - interval '1 minute') >= 60 then
    raise exception 'rate_limited' using errcode = 'P0001';
  end if;

  insert into public.waitlist
    (name, email, source, utm_source, utm_medium, utm_campaign, utm_content, referrer)
  values (
    v_name, v_email,
    left(coalesce(nullif(btrim(p_source), ''), 'landing-2027'), 60),
    left(p_utm_source, 200), left(p_utm_medium, 200),
    left(p_utm_campaign, 200), left(p_utm_content, 200),
    left(p_referrer, 500)
  )
  on conflict ((lower(email))) do nothing;
end;
$$;

revoke all on function public.join_waitlist(text, text, text, text, text, text, text, text) from public;
grant execute on function public.join_waitlist(text, text, text, text, text, text, text, text)
  to anon, authenticated;
