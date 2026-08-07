---
title: "Reproducible Research and Open Science"
weight: 80
cover: "images/covers/reproducible-research.png"
summary: >-
  Software suites and open platforms that make computational research repeatable,
  shareable, extensible, and stable, including the BEAT open-science platform.
research_outputs:
  - "anjos_bob_2015"
  - "anjos_beat_2016"
  - "anjos_mednet_2024"
  - "anjos_sleepless_2017"
  - "guler_refining_2024"
  - "10.1109/isbi61048.2026.11515636"
---

All of my work runs on a fully reproducible framework, and I care about this more than almost
anything else in how we do research. Too many computational studies ship with vague method
descriptions, unavailable data, and undocumented code, which makes them impossible to
reproduce. A workflow that genuinely works has to be repeatable, shareable, extensible, and
stable. It helps to remember that the person who most often has to reproduce your analysis is
your future self.

## Major achievements

It began with tooling. `Bob`, first described in 2012, gave researchers a Python environment
backed by fast C++ where experiments carry their own database protocols, and that philosophy
now runs through the suites we build and maintain, such as `mednet` and `sleepless`, across
tasks as different as medical image analysis, biometrics, presentation-attack detection, and
remote photoplethysmography. Recognising that raw data
sometimes genuinely cannot be shared, we then built the **BEAT** platform, an open computing
environment where experiments can be run and shared even when the underlying data stays
private, closing the gap between "the software is available" and "the results are
reproducible".

Reproducibility is not only about code; it is also about what a number means. We worked on
evaluation methodology itself, including probabilistic performance measures and credible
regions for the small datasets typical of medical work, so that a reported improvement can be
told apart from noise. Beyond our own projects, I stay active in reviewing the reproducibility
of published research and in lowering the barrier for others to contribute reproducibly, on
the conviction that a result no one can rerun is not yet a result.
