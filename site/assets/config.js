// Waitlist backend. Fill in ONE of the two options before publishing.
//
// Option A: Supabase (recommended). Run supabase/migrations/001_waitlist.sql
// in your project, then paste the project URL and the *publishable/anon* key.
// The anon key is safe in the browser: it can only call join_waitlist(),
// never read or write the table directly.
//
// Option B: any endpoint that accepts a JSON POST
// ({ name, email, utm_*, referrer, source }), e.g. a Zapier/Make webhook.
window.CLUB_WAITLIST = {
  supabaseUrl: "",      // e.g. "https://abcd1234.supabase.co"
  supabaseAnonKey: "",  // e.g. "sb_publishable_..." or the legacy anon JWT
  endpoint: "",         // Option B, used only when Supabase is empty
  source: "landing-2027",
};
