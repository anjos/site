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
  - "anjos_credible_2023"
  - "anjos_fairical_2025"
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
backed by fast C++ in which an experiment carries its own dataset protocols, so that "the same
data" means the same partitions rather than the same download. That design now runs through the
suites we build and maintain — `mednet` for medical images and signals, `sleepless` for
polysomnography, `credible` and `fairical` for evaluation — across tasks as different as medical
image analysis, biometrics, presentation-attack detection and remote photoplethysmography, all
released under free licences with documentation and packages rather than as a repository dump.
The harder obstacle was data that genuinely cannot be shared, which no amount of open code
fixes. For that we built the **BEAT** platform, a web-based open computing environment where
experiments are submitted, run and compared against data the experimenter never sees, closing
the gap between "the software is available" and "the result can be checked".

Reproducibility is not only about code; it is also about what a number means. A supervised
master's thesis took up evaluation methodology itself, deriving credible regions for the common
performance measures from their posterior distributions so that a reported improvement can be
told apart from noise on the small datasets typical of medical work. One worked example makes
the case better than any argument: two systems scoring 0.571 and 0.315 by the usual F1 formula
look decisively different, yet under the probabilistic treatment the apparently weaker system
actually outperforms the other in 43% of simulated draws. That work became the open-source
`credible` package, and `fairical` later carried the same instinct into fairness, where a
single score is even less trustworthy because the criteria genuinely conflict and must be
reported as a trade-off rather than collapsed into one number. The habit shows up across the
group's work — the papers that release the code behind their figures, the studies that exist
mainly to establish an honest protocol, the benchmarks deliberately built to be unflattering.
Beyond our own projects I stay active in reviewing the reproducibility of published research and
in lowering the barrier for others to contribute reproducibly, on the conviction that a result
no one can rerun is not yet a result.
