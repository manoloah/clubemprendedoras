# Tutoriales

One folder per tutorial (`site/tutoriales/<slug>/index.html`) and one entry in
`tutoriales.json`. The weekly newsletter reads the live
`https://www.clubdelasemprendedoras.com/tutoriales/tutoriales.json` and features the newest
entry it hasn't sent yet (`newsletter/sent.json`).

```json
{
  "tutoriales": [
    {
      "slug": "emprender-con-ia",
      "titulo": "Cómo emprender con IA (sin ser técnica)",
      "resumen": "Una o dos frases para el correo.",
      "fecha": "2026-10-13",
      "url": "/tutoriales/emprender-con-ia/"
    }
  ]
}
```

`url` can be relative (it's prefixed with the site URL) or a full link if the tutorial lives
somewhere else.
