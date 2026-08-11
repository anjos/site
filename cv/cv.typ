// Curriculum Vitae of André Anjos — built with Typst and @preview/neat-cv.
//
// Presentation only. Every fact on this page comes from a source of truth the
// website already maintains:
//
//   generated.yaml   publications, software, datasets, supervised theses,
//                    courses and projects — written by tools/build-cv.py from
//                    data/outputs.json and content/**/*.md
//   /data/funding.json   grants, from the ORCID record
//   /data/cv.json        the parts no web page holds: employment, education,
//                        community service, skills, bibliometrics
//   /data/bio.yaml, /hugo.toml   biography, contact details and social links
//
// Nothing is typed twice: add a grant on ORCID, a paper in Zotero, a thesis in
// content/theses/, and it appears here on the next `pixi run cv`.
//
// Paths starting with `/` resolve against the repository root, which is why the
// build passes `--root .`.

#import "@preview/neat-cv:1.2.0": (
  contact-info, cv, cv-thin-side, cv-with-side, entry, item-pills,
  item-with-level, publications, social-links, thin-label, thin-metrics,
)
#import "@preview/cetz:0.5.2": canvas, draw
#import "@preview/cetz-plot:0.1.4": chart

// The website's two accent stops, --accent and --accent-2 in assets/css/main.css.
// Everything coloured here derives from them, as it does there.
#let accent = rgb("#1240c0")
#let accent-2 = rgb("#0b6b63")

// neat-cv sets sidebar text at 0.72em — 6.8pt here, and three sizes ended up
// living in that column. One size for all of it, the chart legend's.
#let SIDEBAR_TEXT = 8.4pt

#let site = toml("/hugo.toml")
#let cvdata = json("/data/cv.json")
#let funding = json("/data/funding.json").entries
#let contributions = json("/data/contributions.json").entries
#let bio = yaml("/data/bio.yaml")
#let interests = json("/data/interests.json").entries
#let output-types = json("/data/outputtypes.json").slices
#let gen = yaml("generated.yaml")
#let personal = cvdata.personal

// Every profile link comes from the website's own list, never written twice.
// neat-cv wants bare handles and builds the URLs itself, so `handle` peels the
// prefix back off; `social-url` is for the places that want the whole thing.
#let social-url(name) = site.params.social.find(s => s.name == name).url
#let handle(name, prefix) = social-url(name).trim(prefix, at: start).trim(
  "/",
  at: end,
)

#let birth = {
  let parts = personal.birth.split("-").map(int)
  datetime(year: parts.at(0), month: parts.at(1), day: parts.at(2))
}
#let age = {
  let today = datetime.today()
  let years = today.year() - birth.year()
  if (
    today.month() < birth.month()
      or (today.month() == birth.month() and today.day() < birth.day())
  ) { years - 1 } else { years }
}

#show: cv.with(
  author: (
    firstname: "André",
    lastname: "Anjos",
    email: site.params.email,
    phone: personal.phone,
    address: personal.address,
    position: personal.positions,
    website: site.baseURL.trim("/", at: end),
    github: handle("github", "https://github.com/"),
    linkedin: handle("linkedin", "https://www.linkedin.com/in/"),
    scholar: handle("google-scholar", "https://scholar.google.ch/citations?user="),
    orcid: site.params.orcid,
    // neat-cv's `gitlab` key hardcodes a gitlab.com prefix, and the group that
    // matters is self-hosted at Idiap.
    custom-links: ((
      icon-name: "gitlab",
      label: "medai",
      url: social-url("gitlab"),
    ),),
  ),
  // Deliberately no `profile-picture:` — neat-cv draws it at the top of *every*
  // `cv-with-side` sidebar, and the outputs page opens a second one. The portrait
  // is placed by hand below instead, so it appears exactly once.
  accent-color: accent,
  // The header band is the site's own gradient: `linear-gradient(135deg,
  // var(--accent), var(--accent-2))`, which anjos.ai uses for the CV button and,
  // washed out, for the page field behind everything. A hue shift at constant
  // lightness, never a ramp toward white — see AGENTS.md, "The theme".
  // CSS 135deg (to bottom-right) is Typst 45deg: CSS measures from "to top"
  // clockwise, Typst from "to right". Both stops are darkened equally, which
  // keeps the hue shift intact and buys contrast for neat-cv's white label.
  header-color: gradient.linear(
    accent.darken(30%),
    accent-2.darken(30%),
    angle: 45deg,
  ),
  // Fira Sans, neat-cv's default heading face, is not on conda-forge; Roboto and
  // Open Sans are, and are what the previous CV used. See pixi.toml.
  heading-font: "Roboto",
  body-font: ("Open Sans", "Roboto"),
  body-font-size: 9.5pt,
  paper-size: "a4",
)

// ---------------------------------------------------------------------------
// One renderer for every entry-shaped section, whether it was generated from
// the website or hand-written in data/cv.json. `description` may be a string or
// a list of bullets; `url`, which neat-cv's `entry()` has no field for, is
// printed as a trailing link.
// ---------------------------------------------------------------------------
#let record(r) = {
  let field(name) = r.at(name, default: "")
  let described = field("description")
  entry(
    title: field("title"),
    date: field("date"),
    institution: field("institution"),
    location: field("location"),
    {
      let bulleted = type(described) == array
      if bulleted { list(..described) } else if described != "" { described }
      let url = field("url")
      if url != "" {
        // A bulleted description already ends its own block; prose does not.
        if described != "" and not bulleted { linebreak() }
        text(size: 0.9em, link(url)[#url.trim("https://", at: start).trim("/", at: end)])
      }
    },
  )
}

#let records(rs) = for r in rs { record(r) }

// A grant, in ORCID's own words: title, funder, and the years it runs. The
// funding instrument rides in the funder's parenthesis rather than off in the
// location column, and is dropped when ORCID repeats the funder's name there.
//
// A grant from data/contributions.json also carries a `role`, which is the only
// thing it has to say beyond the ORCID shape and so becomes the description.
#let grant(g) = {
  let year(d) = if d == none { "" } else { str(d).split("-").at(0) }
  let span = if g.end == none { year(g.start) } else {
    year(g.start) + " – " + year(g.end)
  }
  let funder = if g.instrument in (none, g.funder) { g.funder } else {
    g.funder + " (Instrument: " + g.instrument + ")"
  }
  record((
    title: g.title,
    date: span,
    institution: funder,
    description: if "role" in g { "Roles: " + g.role } else { "" },
    url: if g.url == none { "" } else { g.url },
  ))
}

// ---------------------------------------------------------------------------
// The two donut charts. Slice order, grouping and colour all come from
// data/outputtypes.json via generated.yaml — the same file the website's
// /outputs/ page reads, so a slice is the same colour in both places.
//
// The charts live in the 4 cm sidebar, which is far too narrow for rim labels —
// hence the bare donut, the total in its hole, and the legend below carrying
// every name and count. That legend is also the "table view" the palette's two
// low-contrast steps rely on, so it is not optional.
// ---------------------------------------------------------------------------
#let output-pie(slices, caption) = align(center)[
  #let total = slices.map(s => s.count).sum()
  #canvas({
    chart.piechart(
      slices,
      value-key: "count",
      label-key: "label",
      slice-style: slices.map(s => rgb(s.color)),
      radius: 1.72,
      inner-radius: 0.99,
      stroke: white + 0.7pt,
      gap: 1deg,
      outer-label: (content: none),
      legend: (label: none),
    )
    draw.content((0, 0), text(size: 12pt, weight: "bold", fill: accent)[#total])
  })
  #v(-0.2em)
  #text(fill: luma(110), caption)
]

// A squircle, big enough to read its hue at a glance — a 4 pt dot was not.
#let swatch(color) = box(
  baseline: 1.5pt,
  rect(width: 8pt, height: 8pt, radius: 2.5pt, fill: rgb(color), stroke: none),
)

// One legend for the pair: the charts share a colour table, so naming it twice
// would be twice the ink for the same information. Two counts per row — all
// time, then the recent window — because the second chart has no labels either.
#let output-legend(stats) = {
  let recent = stats.recent.map(s => (s.label, s.count)).to-dict()
  set text(fill: luma(90))
  grid(
    columns: (1fr, auto, auto),
    align: (left, right, right),
    column-gutter: 0.5em,
    row-gutter: 0.45em,
    [], text(fill: luma(150))[all], text(fill: luma(150))[5y],
    ..stats
      .all
      .map(s => (
        [#swatch(s.color) #s.label],
        [#s.count],
        text(fill: luma(150))[#recent.at(s.label, default: 0)],
      ))
      .flatten(),
  )
  // Name what the neutral wedge holds; the sections below list them in full.
  let other = output-types.find(s => s.label == "Other")
  if other != none {
    v(0.35em)
    let listed = other.at("cvTypes", default: other.types)
    text(size: 0.85em, fill: luma(150))[Other: #listed.join(", ").]
  }
}

// ---------------------------------------------------------------------------
// Pages 1–2 — the sidebar CV
// ---------------------------------------------------------------------------
#cv-with-side[
  #set text(size: SIDEBAR_TEXT)
  // What `profile-picture:` would have drawn, minus the repeat on later sidebars.
  #block(
    clip: true,
    stroke: accent + 0.5pt,
    radius: 50%,
    width: 100%,
    image("portrait.jpg"),
  )

  = About me
  #bio.one_liner

  // The ORCID record's Keywords, in ORCID's own order. The website's hero pills
  // read the same generated file.
  = Interests
  #for i in interests [- #i]

  = Contact
  #contact-info()

  = Personal
  Date of birth: #birth.display("[day].[month].[year]") (#age years old)

  Nationality: #personal.nationality

  Family: #personal.family

  #v(1fr)
  #social-links()

  #colbreak()

  = Languages
  #for l in cvdata.skills.languages {
    item-with-level(l.title, l.level, subtitle: l.subtitle)
  }

  = Computer Skills
  #item-pills(cvdata.skills.computing)
][
  = Professional Experience
  #records(cvdata.employment)

  = Education
  #records(cvdata.education)

  = Research Areas
  #records(gen.projects)

  = Grants and Funding
  #for g in funding { grant(g) }

  // Grants worked on but not led, each stating the role played. Hand-written in
  // data/contributions.json: ORCID has nowhere to record a role.
  = Earlier Career Contributions
  While working at the Biometrics & Security group of
  #link("https://www.idiap.ch/~marcel/")[Sébastien Marcel].
  #for g in contributions { grant(g) }

  = Teaching
  #records(gen.teaching)

  = Supervision
  // The website only knows the theses it has pages for; the earlier students
  // are the hand-written half of data/cv.json. Both are already newest-first.
  #records(gen.supervision)
  #records(cvdata.supervision)

  // Community Service (committees, reviewing, memberships) is written and ready
  // in data/cv.json but deliberately not printed — it is awaiting a review.
]

// ---------------------------------------------------------------------------
// The research outputs open on the wide sidebar, so the charts get the same
// 4 cm column the first pages use. The bibliography that follows then switches
// to the thin sidebar: it runs for pages, and 4 cm of white down each of them
// would be a poor trade for a label.
// ---------------------------------------------------------------------------
#pagebreak()

#let stats = gen.at("output-stats")

#cv-with-side[
  #set text(size: SIDEBAR_TEXT)
  = Bibliometrics
  h-index: #cvdata.metrics.h_index

  Citations: #cvdata.metrics.citations

  #text(fill: luma(130))[
    #link(social-url("google-scholar"))[Google Scholar], #cvdata.metrics.as_of
  ]

  = Research Outputs
  #output-pie(stats.all, "All-time")
  #v(0.4em)
  #output-pie(stats.recent, "Last 5y")
  #v(0.6em)
  #output-legend(stats)
][
  = Open-Source Software
  #records(gen.software)

  = Open Datasets
  #records(gen.datasets)
]

#pagebreak()

#cv-thin-side[
  // The metrics are stated once, in the sidebar of the page before this one.
  #thin-label("Bibliography")
][
  #for group in gen.publications {
    heading(level: 1, group.label)
    // Author lists are printed in full — that is the information a CV is for —
    // except for the collaboration-signed ATLAS papers, one of which lists 2048
    // people and would on its own be longer than the rest of this document.
    publications(
      group.entries,
      highlight-authors: ("Anjos, André",),
      max-authors: 40,
    )
  }
]
