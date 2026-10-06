// Waitlist backend: the Google Apps Script web app in sheets/Code.gs.
// Paste its /exec URL below (setup steps in sheets/README.md).
// The URL is public by design: it can only add or complete sign-ups,
// never read the Sheet or overwrite existing answers.
window.CLUB_WAITLIST = {
  endpoint: "", // e.g. "https://script.google.com/macros/s/AKfy.../exec"
  source: "landing-2027",
};
