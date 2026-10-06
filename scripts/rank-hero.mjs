// Ranks hero headline + subtitle options by how engaging they are for our ICP,
// using TypeSafe's Jev model.  Run:  node scripts/rank-hero.mjs
// Needs TYPESAFE_API_KEY in the environment or in .env.local (gitignored).
import { readFileSync, existsSync } from "node:fs";

if (!process.env.TYPESAFE_API_KEY && existsSync(".env.local")) {
  for (const line of readFileSync(".env.local", "utf8").split("\n")) {
    const m = line.match(/^\s*([A-Z_]+)\s*=\s*"?([^"\n]*)"?\s*$/);
    if (m) process.env[m[1]] ??= m[2];
  }
}
const KEY = process.env.TYPESAFE_API_KEY;
if (!KEY) throw new Error("Set TYPESAFE_API_KEY (env or .env.local)");

const ICP = {
  who: "Spanish-speaking woman in Mexico/LATAM, 28-42, employee (marketing, sales, design, ops) or small-business owner, university educated, middle class.",
  situation: "Has had a business or app idea for months or years. Not technical. Got quotes of $10-25k USD for an MVP or was told to find a technical co-founder.",
  pains: [
    "Feels AI is moving fast and she is falling behind",
    "Believes she can't start a business because she isn't technical",
    "Afraid her idea won't work; doesn't know where to start",
    "Wants something of her own without quitting her job",
  ],
  wants: "A clear, guided path to launch and sell her idea, with other women like her, in Spanish.",
  turned_off_by: "Bro-culture hype, get-rich-quick promises, heavy tech jargon.",
  where_she_sees_this: "Landing page opened from Instagram on her phone; she reads the headline and subtitle in a few seconds and decides whether to leave her name and email.",
};

const OPTIONS = {
  A_actual: ["De 0 a emprendedora en 8 semanas con IA.", "Pierde el miedo a emprender y convierte tu idea de negocio en una app que sí vende, con ayuda de la inteligencia artificial."],
  B: ["Tu idea lleva años esperando. Lánzala en 8 semanas.", "Con IA y sin saber programar: de la idea a una app que vende, junto a otras emprendedoras."],
  C: ["No necesitas un socio técnico. Necesitas 8 semanas.", "Aprende a usar la IA como experta y convierte tu idea en una app que vende."],
  D: ["Deja de guardar tu idea. Véndela.", "8 semanas para convertirla en una app con IA, aunque nunca hayas programado."],
  E: ["La IA es tu socia técnica. Tú pones la idea.", "En 8 semanas pasas de idea a una app que vende, sin saber programar."],
  F: ["Tu primera app, en 8 semanas y sin programar.", "Pierde el miedo a emprender y usa la IA como experta, en un club de mujeres que van a tu ritmo."],
  G: ["De idea guardada a app que vende, en 8 semanas.", "Pierde el miedo a emprender con IA, acompañada de mujeres como tú."],
  H: ["Emprende sin miedo. Con IA. En 8 semanas.", "Encuentra tu idea, conviértela en una app y consigue tus primeras clientas, sin ser técnica."],
};

const SCORES = {
  engagement: {
    type: "score",
    instructions: "How likely is the person described in `icp` to keep reading and leave her name and email after seeing `hero` (headline + subtitle) on her phone?",
    criteria: [
      "She scrolls past: it feels generic, confusing or not for her",
      "Mild interest, but nothing makes her act now",
      "Interested: she recognizes her situation and considers signing up",
      "Hooked: it names exactly what she feels and she wants in right away",
    ],
  },
  resonance: {
    type: "score",
    instructions: "How directly does `hero` speak to the fears and desires listed in `icp` (fear of starting, not being technical, falling behind on AI, an idea stuck for years)?",
    criteria: [
      "Does not touch her fears or desires",
      "Touches them only vaguely",
      "Clearly speaks to one of them",
      "Speaks to her core fear and her desire in her own words",
    ],
  },
  clarity: {
    type: "score",
    instructions: "How quickly would someone understand from `hero` alone what is offered (a guided 8-week program to turn an idea into a selling app with AI, no coding)?",
    criteria: [
      "Unclear what this is",
      "Gets the vibe but not the offer",
      "Understands the offer after reading both lines",
      "Understands the offer instantly from the headline",
    ],
  },
};
const WEIGHTS = { engagement: 0.5, resonance: 0.3, clarity: 0.2 };

async function ask(state, questions) {
  const res = await fetch("https://api.typesafe.ai/v1/systemone", {
    method: "POST",
    headers: { Authorization: `Bearer ${KEY}`, "Content-Type": "application/json" },
    body: JSON.stringify({ model: "jev-latest", state, questions }),
  });
  if (!res.ok) throw new Error(`${res.status} ${await res.text()}`);
  return res.json();
}

// 1) Comparable per-option scores (same questions, one request per option).
const rows = await Promise.all(
  Object.entries(OPTIONS).map(async ([id, [headline, subtitle]]) => {
    const { answers } = await ask({ icp: ICP, hero: { headline, subtitle } }, SCORES);
    const norm = (k) => answers[k].score / (SCORES[k].criteria.length - 1);
    const total = Object.entries(WEIGHTS).reduce((s, [k, w]) => s + w * norm(k), 0);
    return { id, headline, subtitle, total, ...Object.fromEntries(Object.keys(SCORES).map((k) => [k, +norm(k).toFixed(2)])) };
  })
);

// 2) Head-to-head: which single option would she most likely sign up from?
const { answers } = await ask(
  { icp: ICP, options: Object.fromEntries(Object.entries(OPTIONS).map(([k, [h, s]]) => [k, `${h} — ${s}`])) },
  {
    pick: {
      type: "choice",
      instructions: "Shown one of `options` as the hero of the landing page, which one would most likely make the person in `icp` leave her name and email?",
      criteria: Object.fromEntries(Object.keys(OPTIONS).map((k) => [k, null])),
    },
  }
);
const pick = answers.pick.probabilities;

rows.sort((a, b) => b.total - a.total);
console.table(rows.map((r) => ({ id: r.id, total: +r.total.toFixed(3), engagement: r.engagement, resonance: r.resonance, clarity: r.clarity, head_to_head: +(pick[r.id] ?? 0).toFixed(2), headline: r.headline })));
console.log("Head-to-head winner:", answers.pick.choice, "confidence", answers.pick.confidence);
