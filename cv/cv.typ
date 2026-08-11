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

#let site = toml("/hugo.toml")
#let cvdata = json("/data/cv.json")
#let funding = json("/data/funding.json").entries
#let bio = yaml("/data/bio.yaml")
#let gen = yaml("generated.yaml")
#let personal = cvdata.personal

// neat-cv builds social URLs from bare handles, so the handles are recovered
// from the site's own link list rather than written down a second time.
#let handle(name, prefix) = {
  let hit = site.params.social.find(s => s.name == name)
  if hit == none { none } else {
    hit.url.trim(prefix, at: start).trim("/", at: end)
  }
}

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
      url: site.params.social.find(s => s.name == "gitlab").url,
    ),),
  ),
  profile-picture: image("portrait.jpg"),
  // The website's one accent knob, --accent in assets/css/main.css. Changing it
  // there and here keeps page and PDF the same colour.
  accent-color: rgb("#1240c0"),
  header-color: rgb("#35414d"),
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

// A grant, in ORCID's own words: title, funder, and the years it runs.
#let grant(g) = {
  let year(d) = if d == none { "" } else { str(d).split("-").at(0) }
  let span = if g.end == none { year(g.start) } else {
    year(g.start) + " – " + year(g.end)
  }
  record((
    title: g.title,
    date: span,
    institution: g.funder,
    location: if g.instrument == none { "" } else { g.instrument },
    url: if g.url == none { "" } else { g.url },
  ))
}

// ---------------------------------------------------------------------------
// Pages 1–2 — the sidebar CV
// ---------------------------------------------------------------------------
#cv-with-side[
  = About me
  #bio.one_liner

  = Interests
  #for i in site.params.interests [- #i]

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

  = Computing
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

  = Teaching
  #records(gen.teaching)

  = Supervision
  // The website only knows the theses it has pages for; the earlier students
  // are the hand-written half of data/cv.json. Both are already newest-first.
  #records(gen.supervision)
  #records(cvdata.supervision)

  = Community Service
  == Programme Committees
  #records(cvdata.service.committees)

  == Journal Reviewing
  #records(cvdata.service.reviewing)

  == Memberships
  #records(cvdata.service.memberships)
]

// ---------------------------------------------------------------------------
// Remaining pages — the bibliography
// ---------------------------------------------------------------------------
#pagebreak()

#cv-thin-side[
  #thin-label("Bibliography")
  #v(1em)
  #thin-metrics((
    (label: "h-index", value: cvdata.metrics.h_index),
    (label: "Citations", value: cvdata.metrics.citations),
  ))
][
  = Open-Source Software
  #records(gen.software)

  = Open Datasets
  #records(gen.datasets)

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
