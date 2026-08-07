---
title: "Biometrics and Presentation-Attack Detection"
weight: 100
archived: true
period: "2010–2018"
cover: "images/covers/biometrics.jpg"
summary: >-
  Earlier work with the Idiap Biometrics group on robust recognition and
  presentation-attack detection that generalises to unseen attacks.
partners:
  - "Biometrics Security & Privacy Group, Idiap"
publications_heading: "Select publications"
research_outputs:
  - "10.1109/tifs.2015.2400392"
  - "10.1109/tifs.2019.2916652"
  - "10.1109/tifs.2018.2885284"
  - "10.1109/tifs.2014.2349158"
  - "10.1109/ijcb.2011.6117509"
  - "chingovska_effectiveness_2012"
  - "10.1109/ijcb.2011.6117503"
  - "10.1109/cvprw.2013.22"
  - "10.1049/iet-bmt.2012.0071"
  - "10.1007/978-3-642-37410-4_11"
  - "10.1007/978-3-319-28501-6_8"
  - "10.34777/cwcg-7r82"
  - "10.34777/8zdh-v182"
  - "10.34777/payf-vb10"
  - "anjos_printattack_2011"
  - "anjos_bob_2015"
---

*Earlier-career work in the Idiap Biometrics Security & Privacy Group (2010 to 2018).*

Biometric systems are exposed to presentation attacks, and most detectors of the
time worked discriminatively, which meant they struggled the moment they met an
attack they had not seen in training. Much of my work in this period looked for
ways to make that generalisation better.

## Major achievements

The work began by giving the field what it lacked: public data and honest baselines. We
released the **PRINT-ATTACK** database, 200 genuine and 200 attack videos over 50 identities,
with a motion-based baseline that correlates a person's head movement against the scene
background, and then organised the **first international Competition on Counter-Measures to
2-D Facial Spoofing Attacks**, where six teams established that motion, texture, and liveness
cues could separate simple printed-photo attacks but called for harder ones. Texture proved
powerful on the richer **REPLAY-ATTACK** data that followed: a Local Binary Pattern baseline
and its spatio-temporal extension **LBP-TOP** cut the half-total error rate from 15.16% to
7.60%, while a counter-measure based purely on foreground/background optical-flow correlation
reached a 1.52% equal-error rate on the PHOTO-ATTACK set, near-perfect on that data.

The harder problems were generalisation and fair evaluation. We argued that an anti-spoofing
module should never be judged alone: fused with the verification system it protects, as a
ternary decision over genuine clients, impostors, and attacks, is where it acquires meaning,
and we built an open framework to study that joint operation. To score such systems honestly
we proposed the **Expected Performance and Spoofability Curve**, which reports recognition
accuracy and vulnerability to spoofing together. For robustness to *unseen* attacks we exploited
the identity the recogniser already knows: generative and discriminative client-specific
detectors improved on client-independent ones by up to 50% relative and generalised better to
attack types absent from training. The final phase moved to deep learning and beyond the
visible spectrum, where **Domain-Specific Units** adapted the low-level layers of a
visual-spectra CNN to match faces across domains, visible-to-near-infrared, thermal, and
sketch, surpassing the state of the art, and a **multi-channel CNN** fusing colour, depth,
near-infrared, and thermal detected sophisticated 2D and 3D attacks, including silicone masks,
at a 0.3% average classification error.

Much of this work's lasting value lies in the public datasets it produced, still standard
benchmarks in face anti-spoofing. **PRINT-ATTACK** (2011) and **REPLAY-ATTACK** (2012) fixed
printed-photo and video-replay attacks together with reproducible evaluation protocols;
**MSSpoof** (2015) carried the threat model into the near-infrared, showing that even
multispectral capture can be spoofed; and **WMCA** (2019) brought colour, depth, near-infrared,
and thermal channels together with a wide range of 2D and 3D presentation-attack instruments.
Shipped with open-source implementations through the `bob` framework, these databases let
others reproduce our results and compete against them on an equal footing.
