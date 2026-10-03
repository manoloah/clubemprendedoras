// Waitlist backend. Fill in ONE of the two options before publishing.
//
// Option A: Supabase (recommended). Run supabase/migrations/001_waitlist.sql
// in your project, then paste the project URL and the *publishable/anon* key.
// The anon key is safe in the browser: RLS only allows inserts, never reads.
//
// Option B: any endpoint that accepts a JSON POST
// ({ name, email, utm_*, referrer, source }), e.g. a Zapier/Make webhook.
window.CLUB_WAITLIST = {
  supabaseUrl: "",      // e.g. "https://abcd1234.supabase.co"
  supabaseAnonKey: "",  // e.g. "sb_publishable_..." or the legacy anon JWT
  endpoint: "",         // Option B, used only when Supabase is empty
  table: "waitlist",
  source: "landing-2027",
};
