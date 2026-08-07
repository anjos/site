---
title: "Automatic Grading of Vasculitis Inflammation in Fluorescein Angiography Images"
author: "Victor Amiot"
level: "Master"
university: "EPFL, School of Life Sciences"
date: 2023-01-27
slug: "victor-amiot"
cover: "images/covers/victor-amiot.jpg"
summary: >-
  Vasculitis inflames the blood vessels at the back of the eye and can cost a
  patient their sight. This thesis built an automatic pipeline that detects and
  grades the dye leakage from angiography, tested on 543 patients at Jules-Gonin.
projects:
  - "uveitis"
report: "https://www.idiap.ch/~aanjos/pdfs/theses/victor-amiot-vasculitis.pdf"
research_outputs:
  - "10.1109/cbms58004.2023.00301"
  - "10.1016/j.compbiomed.2025.110327"
  - "10.2139/ssrn.4960069"
datasets:
  - name: "Fluorescein angiography study set, 543 patients (Jules-Gonin); clinical, not public"
partners:
  - name: "Hôpital ophtalmique Jules-Gonin (HOJG), Lausanne"
    country: "Switzerland"
  - name: "Luzerner Kantonsspital"
    country: "Switzerland"
  - name: "University Hospital of Grenoble Alpes"
    country: "France"
  - name: "Idiap Research Institute"
    country: "Switzerland"
---

Vasculitis is an inflammatory disease that attacks the retinal blood vessels and
can lead to loss of vision. It is best revealed by fluorescein angiography (FA),
in which a fluorescent dye is injected into the bloodstream: vessels damaged by
the disease leak part of the dye, and the resulting stain becomes visible in the
images a few minutes after injection. At the Jules-Gonin Eye Hospital the severity
is scored with the standard Tugal-Tuktun scale, on which retinal vascular leakage
is rated focal, multifocal, or diffuse. That judgement rests on an expert eye and
years of ophthalmology training, which raises the question at the heart of this
thesis: can the vascular leakage that drives the grade be detected and quantified
automatically from an FA exam?

Until then, automated analysis of retinal inflammation had mostly targeted
diabetic retinopathy, or the global detection of hyper-fluorescence across an
exam, rather than the vasculitis-specific leakage that clinicians actually grade.
The difficulty, and the hypothesis this thesis set out to test, is that
pathological leakage can be told apart from the vessels themselves and from the
fluorescence of other retinal structures by first anchoring the analysis on the
vasculature. Because the vessels are the only bright structures in the early
frames of the FA time-lapse, segmenting them there and then aligning those masks
onto the late frames should isolate the perivascular region where staining is
expected, so that leakage appears simply as retinal background that has become
abnormally bright.

The work was carried out inside the multi-centre CAD4IED project, bringing
together the Jules-Gonin Eye Hospital, Idiap, the Luzern Kantonsspital, and the
CHU Grenoble. A full pipeline was built, from raw clinical FA data to a leakage
grade. Several image-registration strategies were compared against standard SIFT,
and alignment was validated with a purpose-built parallel-view criterion, lifting
overall frame-registration success from 46.5 to 66.8 percent. The gain landed
where it matters: the late frames on which leakage is visible nearly doubled per
study, from 1.44 to 2.86 registered frames on average, and the share of studies
left with no usable late frame fell from 22.2 to 9.5 percent. Computer-vision
methods then produced vessel and background masks that segmented the
hyper-fluorescence on the late frames, and grading strategies mapped the outcome
onto the Tugal-Tuktun categories. A study set of 543 patients was prepared for
expert annotation; on an initial 60-image subset annotated by a single grader, the
pipeline detected diffuse staining well enough to grade cases correctly.

The thesis showed that vasculitis-specific vascular leakage can be localised and
graded automatically when the analysis is anchored to the retinal vasculature,
and that careful, task-specific frame registration is what makes the downstream
segmentation trustworthy. The results are preliminary and are expected to improve
once the parameters are tuned against the fully annotated dataset. Beyond its own
numbers, the project laid the methodological groundwork that the group's later,
clinic-ready uveitis scoring system, UveAI, was built upon.
