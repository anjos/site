---
title: "Trustworthy Biometric Verification under Spoofing Attacks: Application to the Face Mode"
author: "Ivana Chingovska"
level: "PhD"
role: "De facto co-supervisor"
university: "EPFL, Electrical Engineering (doctoral programme, with Idiap)"
date: 2015-11-23
slug: "ivana-chingovska"
cover: "images/covers/ivana-chingovska.png"
summary: >-
  A face-recognition system can be fooled by a photo or video of its target. This
  doctoral thesis built defences against such spoofing and, just as importantly, a
  principled way to measure how trustworthy a system is under attack.
projects:
  - "biometrics-pad"
report: "https://publications.idiap.ch/attachments/papers/2016/Chingovska_THESIS_2015.pdf"
research_outputs:
  - "10.1007/978-3-319-28501-6_8"
  - "10.1109/tifs.2015.2400392"
  - "10.1109/tifs.2014.2349158"
  - "10.1007/978-1-4471-6524-8_10"
  - "10.1007/978-3-642-27733-7_9212-2"
  - "10.1109/cvprw.2013.22"
  - "10.1109/icb.2013.6613026"
  - "chingovska_effectiveness_2012"
  - "10.34777/cwcg-7r82"
  - "anjos_bob_2015"
partners:
  - name: "Idiap Research Institute"
    country: "Switzerland"
---

Biometric verification promises to recognise a person by who they are rather than
by what they remember, and face recognition is among its most convenient forms.
That convenience comes with a weakness: a system can be fooled by a presentation
attack, a printed photograph or a replayed video of the legitimate user. As face
verification spread into everyday devices, this thesis asked how such systems can
be made trustworthy in the presence of spoofing, and how that trustworthiness can
even be measured.

At the time, presentation-attack detection was a young and fragmented field, with
countermeasures evaluated on private data and no agreed way to report how
vulnerable a verification system really was. The thesis took the position that
resistance to spoofing must be treated as a first-class property of verification,
addressed both by designing effective face countermeasures and by building an
evaluation methodology that quantifies a system's behaviour when it is actually
attacked.

The integration was pursued at three distinct points. At the input, the identity
the verification system already knows was made available to the detector,
producing client-specific countermeasures in both generative and discriminative
form that outperformed their client-independent equivalents and, more importantly,
held up better against attacks unseen during training. At the output, the two
systems' scores were fused as a multiple-expert problem, with several fusion rules
compared on verification accuracy and robustness together. At the evaluation stage,
the thesis proposed the Expected Performance and Spoofability framework, which
treats the system as facing three kinds of input — genuine clients, zero-effort
impostors and deliberate attacks — and its accompanying curve, which allows two
systems to be compared without the bias that follows from tuning on the test set.
All of it was released as free software alongside the public Replay-Attack
database and a family of texture and motion countermeasures.

The hypothesis is borne out at every one of the three points, and the answer to the
opening question is that trustworthiness is not a property of the detector at all
but of the pair. A countermeasure evaluated alone can look strong and still leave
the system it protects vulnerable, because the relevant error rates only exist once
attacks are admitted as a third class of input. The database, the software and the
metrics became widely used reference points in presentation-attack detection, and
the framing — evaluate the protected system, not the protection — is the thesis's
most durable contribution to how the community reports biometric trustworthiness.
