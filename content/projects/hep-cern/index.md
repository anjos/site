---
title: "High-Energy Physics — ATLAS Trigger (CERN)"
weight: 110
archived: true
period: "2001–2010"
cover: "images/covers/hep-cern.svg"
summary: >-
  Earlier work at CERN's ATLAS experiment on real-time trigger and data-acquisition
  systems, and neural-network methods for particle recognition.
partners:
  - "CERN, ATLAS Experiment"
  - "Federal University of Rio de Janeiro"
research_outputs:
  - "10.1088/1748-0221/3/08/s08003"
  - "10.48550/arxiv.0901.0512"
  - "10.1109/23.710942"
  - "10.1016/s0168-9002(03)00553-9"
  - "10.1016/j.nima.2005.11.132"
  - "10.1016/j.cpc.2010.10.003"
  - "10.21528/lnlm-vol4-no2-art5"
  - "torres_online_2007"
  - "10.1109/tns.2004.828875"
  - "anjos_sistema_2006"
---

*Earlier-career work at CERN (2001 to 2010).*

I spent close to a decade at CERN's ATLAS experiment, working on the Trigger and
Data Acquisition systems that decide, in real time, which of the Large Hadron
Collider's collisions are worth recording. That infrastructure helped make
discoveries like the Higgs boson possible. In parallel, I explored neural-network
and statistical methods for recognising particles as the data streamed in.

## Major achievements

I contributed to the design, commissioning, and operation of the ATLAS
High-Level Trigger, the software stage that decides which collisions are kept.
The scale sets the problem: the collider delivers collisions at 40 MHz and the
detector produces around 1.5 megabytes per event, some 60 terabytes per second
of raw data, of which only a small fraction can ever be written to storage. The
architecture we helped build and validate splits that decision across two
software stages running on processor farms, and keeps it affordable by having
the hardware trigger point at regions of interest, so the second stage reads
under 2% of an event instead of all of it. My work concerned the dataflow and
supervision of that system — how events move through the farms, and how the
farms themselves are configured, controlled, and monitored — and later a
software environment that automated configuring and running the trigger and
dataflow farms, so that a system of this size could be tested and redeployed by
people ranging from casual testers to final deployers. Some of those components
stayed in use well after I left.

In parallel, my doctoral work applied neural networks and statistical methods
to separating electrons from jets in the online filter, from calorimeter data
alone and within a hard real-time budget. The obstacle was dimensionality: a
calorimeter region of interest carries far too many channels to feed a network
directly at these rates. Organising the deposited energy into concentric ring
sums around the shower axis compressed the input while preserving the structure
that distinguishes an electron from a hadronic jet, and so improved
discrimination rather than merely making it cheaper — the resulting network
reached 97% electron efficiency at a 3% false-alarm rate, with the full
discrimination chain executing in under 500 microseconds. More than anything,
this period taught me how large scientific software is really built, and how
much of a physics result rests on infrastructure nobody outside the
collaboration ever sees. That is what drew me toward reproducible,
well-engineered computing in the years that followed.
