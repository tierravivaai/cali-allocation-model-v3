/**
 * generate_pptx.js
 * ─────────────────────────────────────────────────────────────────────────────
 * Generates the Cali Fund Allocation Model explainer presentation.
 *
 * Produces: cali_fund_explainer.pptx (11 slides, 16:9)
 *
 * Slide structure:
 *   1  — Title
 *   2  — Section: 1 · Purpose
 *   3  — Content: Purpose
 *   4  — Section: 2 · The Formula
 *   5  — Content: The Formula
 *   6  — Section: 3 · Establishing Equity
 *   7  — Content: Establishing Equity (IUSAF)
 *   8  — Section: 4 · Recognising Stewardship
 *   9  — Content: Recognising Stewardship (TSAC & SOSAC)
 *   10 — Section: 5 · Recognising IPLCs
 *   11 — Content: Recognising IPLCs
 *
 * Usage:
 *   node generate_pptx.js
 *   node generate_pptx.js --out ./output/my_deck.pptx
 *
 * Dependencies:
 *   npm install -g pptxgenjs   (or npm install pptxgenjs)
 *
 * ─────────────────────────────────────────────────────────────────────────────
 */

"use strict";

const pptxgen = require("pptxgenjs");
const path    = require("path");

// ── CLI arg: optional output path ─────────────────────────────────────────
const args    = process.argv.slice(2);
const outFlag = args.indexOf("--out");
const outFile = outFlag !== -1 ? args[outFlag + 1] : "cali_fund_explainer.pptx";

// ── Presentation setup ────────────────────────────────────────────────────
const pres = new pptxgen();
pres.layout  = "LAYOUT_16x9";   // 10" × 5.625"
pres.title   = "Cali Fund Allocation Model (Inverted UN Scale of Assessment Option)";
pres.author  = "TierraViva AI";
pres.subject = "Biodiversity Fund Allocation — Illustrative Model";

// ── Colour palette ────────────────────────────────────────────────────────
// Deep forest / teal theme — chosen to reflect biodiversity subject matter.
// NEVER prefix hex values with '#' in PptxGenJS (causes file corruption).
const C = {
  // Structural colours
  dark:     "0D3B2E",   // deep forest green — title & section slide backgrounds
  mid:      "1A5C47",   // forest green — callout text
  teal:     "028090",   // teal — accent bar, highlights
  cream:    "F5F4EF",   // warm off-white — content slide backgrounds
  white:    "FFFFFF",
  muted:    "5C7B72",   // muted green-grey — body text on cream

  // Component colour ramps (background / border / text)
  // IUSAF — blue: foundation/equity
  iusaf_bg: "E6F1FB", iusaf_bd: "378ADD", iusaf_tx: "0C447C",
  // TSAC — green: terrestrial stewardship
  tsac_bg:  "E1F5EE", tsac_bd:  "1D9E75", tsac_tx:  "085041",
  // SOSAC — amber: ocean/SIDS stewardship
  sosac_bg: "FAEEDA", sosac_bd: "EF9F27", sosac_tx: "633806",
  // IPLC — purple: community allocation
  iplc_bg:  "EEEDFE", iplc_bd:  "7F77DD", iplc_tx:  "3C3489",
  // Amber callout (pathways to disbursement warning)
  amber_bar: "BA7517", amber_bg: "FEF9EE", amber_bd: "EFD08A", amber_tx: "5C3D0A",
};

// ── Reusable helper functions ─────────────────────────────────────────────
// These are intentionally pure — they only take a slide and explicit
// parameters, so they are safe to call multiple times without side effects.
// PptxGenJS mutates option objects, so helpers that pass objects inline
// are safe; any shared object must be wrapped in a factory function.

/**
 * titleSlide — renders the opening title slide.
 * Dark forest background with teal accent bar, main title, option subtitle,
 * descriptor line, disclaimer pill, and right-aligned section preview list.
 */
function titleSlide(slide) {
  slide.background = { color: C.dark };

  // Left accent bar
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 0, w: 0.22, h: 5.625,
    fill: { color: C.teal }
  });

  // Main title
  slide.addText("Cali Fund\nAllocation Model", {
    x: 0.55, y: 1.3, w: 6.5, h: 1.8,
    fontSize: 40, fontFace: "Georgia", bold: true,
    color: C.white, valign: "middle"
  });

  // Option subtitle — signals this is one methodological option, not the only one
  slide.addText("Inverted UN Scale of Assessment Option", {
    x: 0.55, y: 3.1, w: 7, h: 0.45,
    fontSize: 18, fontFace: "Georgia", color: "9ecfc8", italic: true
  });

  // Descriptor
  slide.addText("An interactive guide to the five key concepts", {
    x: 0.55, y: 3.62, w: 7, h: 0.4,
    fontSize: 14, fontFace: "Calibri", color: "7ab8b2", italic: true
  });

  // Disclaimer pill
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0.55, y: 4.6, w: 7.5, h: 0.55,
    fill: { color: C.teal, transparency: 75 },
    line: { color: C.teal, width: 0.5 }
  });
  slide.addText(
    "All figures are illustrative modelling outputs for exploratory purposes. " +
    "They do not represent entitlements or predetermined disbursements.",
    { x: 0.65, y: 4.62, w: 7.3, h: 0.5, fontSize: 10, fontFace: "Calibri", color: C.white, valign: "middle" }
  );

  // Section index — right column
  const steps = [
    "Purpose",
    "The Formula",
    "Establishing Equity",
    "Recognising Stewardship",
    "Recognising IPLCs",
  ];
  steps.forEach((label, i) => {
    slide.addText(`${i + 1}. ${label}`, {
      x: 7.2, y: 1.5 + i * 0.52, w: 2.6, h: 0.45,
      fontSize: 12, fontFace: "Calibri", color: "9ecfc8", align: "right"
    });
  });
}

/**
 * sectionSlide — dark divider slide between content sections.
 * @param {object} slide  - PptxGenJS slide object
 * @param {string} num    - Section number (e.g. "1")
 * @param {string} title  - Section title
 * @param {string} [sub]  - Optional subtitle/framing line
 */
function sectionSlide(slide, num, title, sub) {
  slide.background = { color: C.dark };
  slide.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 0.22, h: 5.625, fill: { color: C.teal } });
  slide.addText(num, {
    x: 0.5, y: 0.6, w: 1.2, h: 1.2,
    fontSize: 72, fontFace: "Georgia", bold: true, color: C.teal, valign: "top"
  });
  slide.addText(title, {
    x: 0.5, y: 1.8, w: 9, h: 1.2,
    fontSize: 36, fontFace: "Georgia", bold: true, color: C.white, valign: "middle"
  });
  if (sub) {
    slide.addText(sub, {
      x: 0.5, y: 3.1, w: 8.5, h: 1.0,
      fontSize: 16, fontFace: "Calibri", color: "9ecfc8", italic: true, valign: "top"
    });
  }
}

/**
 * contentHeader — dark header bar for content slides.
 * @param {object} slide  - PptxGenJS slide object
 * @param {string} title  - Header text (e.g. "1 · Purpose")
 */
function contentHeader(slide, title) {
  slide.background = { color: C.cream };
  slide.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 10, h: 0.7, fill: { color: C.dark } });
  slide.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 0.22, h: 5.625, fill: { color: C.teal } });
  slide.addText(title, {
    x: 0.5, y: 0.1, w: 9, h: 0.5,
    fontSize: 16, fontFace: "Georgia", bold: true,
    color: C.white, valign: "middle", margin: 0
  });
}

/**
 * colorCard — a coloured information card with a bold label and body text.
 * Note: bg/bd/labelColor/bodyColor are hex strings without '#'.
 */
function colorCard(slide, x, y, w, h, bg, bd, label, labelColor, body, bodyColor) {
  slide.addShape(pres.shapes.RECTANGLE, { x, y, w, h, fill: { color: bg }, line: { color: bd, width: 1 } });
  slide.addText(label, {
    x: x + 0.12, y: y + 0.1, w: w - 0.24, h: 0.28,
    fontSize: 10, fontFace: "Calibri", bold: true, color: labelColor, margin: 0
  });
  slide.addText(body, {
    x: x + 0.12, y: y + 0.38, w: w - 0.24, h: h - 0.5,
    fontSize: 11, fontFace: "Calibri", color: bodyColor, valign: "top", margin: 0
  });
}

/**
 * callout — teal left-border callout box (for key takeaways).
 */
function callout(slide, x, y, w, h, text) {
  slide.addShape(pres.shapes.RECTANGLE, { x, y, w: 0.06, h, fill: { color: C.teal } });
  slide.addShape(pres.shapes.RECTANGLE, {
    x: x + 0.06, y, w: w - 0.06, h,
    fill: { color: "EAF6F5" }, line: { color: "C0E4DF", width: 0.5 }
  });
  slide.addText(text, {
    x: x + 0.18, y: y + 0.05, w: w - 0.25, h: h - 0.1,
    fontSize: 11, fontFace: "Calibri", color: C.mid, valign: "top", margin: 0
  });
}

/**
 * amberCallout — amber left-border callout (for important caveats/warnings).
 * Used for the IPLC pathways-to-disbursement note.
 */
function amberCallout(slide, x, y, w, h, richText) {
  slide.addShape(pres.shapes.RECTANGLE, { x, y, w: 0.06, h, fill: { color: C.amber_bar } });
  slide.addShape(pres.shapes.RECTANGLE, {
    x: x + 0.06, y, w: w - 0.06, h,
    fill: { color: C.amber_bg }, line: { color: C.amber_bd, width: 0.5 }
  });
  slide.addText(richText, {
    x: x + 0.2, y: y + 0.05, w: w - 0.28, h: h - 0.1,
    fontSize: 12, fontFace: "Calibri", valign: "middle", margin: 0
  });
}

// ── SLIDE 1 — Title ───────────────────────────────────────────────────────
let s = pres.addSlide();
titleSlide(s);

// ── SLIDES 2–3 — Purpose ─────────────────────────────────────────────────
s = pres.addSlide();
sectionSlide(s, "1", "Purpose", "What is this model for?");

s = pres.addSlide();
contentHeader(s, "1 · Purpose");

s.addText(
  "The Cali Fund distributes biodiversity finance among countries that are Parties to the Convention on " +
  "Biological Diversity (CBD). This model produces indicative, illustrative shares — not binding " +
  "entitlements — to support negotiations.",
  { x: 0.5, y: 0.85, w: 9, h: 0.75, fontSize: 13, fontFace: "Calibri", color: C.muted, valign: "top" }
);

colorCard(s, 0.5, 1.7, 4.3, 1.35, C.white, "CBCAC0",
  "Core principle", "1A5C47",
  "Countries that contribute less to the UN budget receive proportionally more from this fund",
  "2C5F2D"
);
colorCard(s, 5.2, 1.7, 4.3, 1.35, C.white, "CBCAC0",
  "Special protections", "1A5C47",
  "Least Developed Countries, Small Island Developing States, and Indigenous Peoples & Local Communities " +
  "all receive targeted support",
  "2C5F2D"
);

callout(s, 0.5, 3.2, 9.0, 0.65,
  "The model uses the UN Scale of Assessments 2025–2027 as its input — a widely-accepted measure of " +
  "countries' relative economic capacity."
);

// Control chips row (four sidebar controls explained)
const chips = [
  { label: "Fund size",           desc: "Sets the total annual pot in USD",               bg: C.iusaf_bg, tx: C.iusaf_tx },
  { label: "Land area weight",    desc: "Adjusts how much land stewardship matters",       bg: C.tsac_bg,  tx: C.tsac_tx  },
  { label: "Island states weight",desc: "Reserves a pool for small island nations",        bg: C.sosac_bg, tx: C.sosac_tx },
  { label: "IPLC share",          desc: "Splits each allocation between governments and IPLCs", bg: C.iplc_bg, tx: C.iplc_tx },
];
chips.forEach(({ label, desc, bg, tx }, i) => {
  const cx = 0.5 + i * 2.3;
  s.addShape(pres.shapes.RECTANGLE, { x: cx, y: 4.05, w: 2.1, h: 1.1, fill: { color: bg }, line: { color: "CBCAC0", width: 0.5 } });
  s.addText(label, { x: cx + 0.1, y: 4.1, w: 1.9, h: 0.3, fontSize: 11, fontFace: "Calibri", bold: true, color: tx, margin: 0 });
  s.addText(desc,  { x: cx + 0.1, y: 4.42, w: 1.9, h: 0.65, fontSize: 10, fontFace: "Calibri", color: C.muted, valign: "top", margin: 0 });
});

// ── SLIDES 4–5 — The Formula ──────────────────────────────────────────────
s = pres.addSlide();
sectionSlide(s, "2", "The Formula", "One foundation. Two adjustments.");

s = pres.addSlide();
contentHeader(s, "2 · The Formula");

s.addText("The model has one foundation and two adjustments that together determine every country's share.", {
  x: 0.5, y: 0.85, w: 9, h: 0.45, fontSize: 13, fontFace: "Calibri", color: C.muted
});

// Formula box — rich text with colour-coded component names
s.addShape(pres.shapes.RECTANGLE, { x: 0.5, y: 1.4, w: 9, h: 1.35, fill: { color: C.white }, line: { color: "CBCAC0", width: 0.5 } });
s.addText([
  { text: "Each country's share  =  ",                                               options: { color: "3B3B39", fontSize: 13 } },
  { text: "Inverted UN Scale of Assessment Foundation (IUSAF)",                      options: { color: C.iusaf_tx, bold: true, fontSize: 13 } },
  { text: "  — the base",                                                            options: { color: C.muted, fontSize: 12 } },
  { text: "\n" },
  { text: "  +  ",                                                                   options: { color: "3B3B39", fontSize: 13 } },
  { text: "Terrestrial Stewardship Allocation Component (TSAC)",                     options: { color: C.tsac_tx, bold: true, fontSize: 13 } },
  { text: "  — adjustment for large countries",                                      options: { color: C.muted, fontSize: 12 } },
  { text: "\n" },
  { text: "  +  ",                                                                   options: { color: "3B3B39", fontSize: 13 } },
  { text: "SIDS Ocean Stewardship Allocation Component (SOSAC)",                     options: { color: C.sosac_tx, bold: true, fontSize: 13 } },
  { text: "  — adjustment for island states",                                        options: { color: C.muted, fontSize: 12 } },
], { x: 0.65, y: 1.48, w: 8.7, h: 1.2, valign: "middle", margin: 0 });

// Three component cards
colorCard(s, 0.5, 2.9, 2.85, 1.45, C.iusaf_bg, C.iusaf_bd,
  "IUSAF · Foundation", C.iusaf_tx,
  "The core equity engine. Inverts UN budget shares so smaller contributors receive a larger fund share. All allocations start here.",
  "185FA5"
);
colorCard(s, 3.58, 2.9, 2.85, 1.45, C.tsac_bg, C.tsac_bd,
  "TSAC · Adjustment", C.tsac_tx,
  "Recognises the terrestrial biodiversity stewardship responsibilities of countries with large land areas.",
  "0F6E56"
);
colorCard(s, 6.65, 2.9, 2.85, 1.45, C.sosac_bg, C.sosac_bd,
  "SOSAC · Adjustment", C.sosac_tx,
  "Recognises the ocean stewardship responsibilities and structural constraints of Small Island Developing States.",
  "854F0B"
);

callout(s, 0.5, 4.5, 9.0, 0.65,
  "IUSAF is the foundation. TSAC and SOSAC are adjustments — any weight given to them reallocates money " +
  "away from the IUSAF base. It is a matter for Parties to agree the appropriate balance."
);

// ── SLIDES 6–7 — Establishing Equity (IUSAF) ─────────────────────────────
s = pres.addSlide();
sectionSlide(s, "3", "Establishing Equity", "IUSAF — the foundation of the model");

s = pres.addSlide();
contentHeader(s, "3 · Establishing Equity (IUSAF)");

s.addText([
  { text: "The UN Scale says how much each country contributes to the UN budget. The model flips this: " +
          "the smaller your UN share, the larger your fund share. " },
  { text: "This is the foundation of the model.", options: { bold: true, color: C.dark } }
], { x: 0.5, y: 0.85, w: 9, h: 0.65, fontSize: 13, fontFace: "Calibri", color: C.muted });

// Inversion formula
s.addShape(pres.shapes.RECTANGLE, { x: 0.5, y: 1.6, w: 9, h: 0.65, fill: { color: C.white }, line: { color: "CBCAC0", width: 0.5 } });
s.addText("Fund share  =  1 ÷ UN budget share   →   then rescaled so all shares add up to 100%", {
  x: 0.65, y: 1.65, w: 8.7, h: 0.55,
  fontSize: 14, fontFace: "Calibri", color: C.dark, valign: "middle", margin: 0
});

// Illustrative bar chart — 3 countries
const bars = [
  { name: "Country A", label: "Small UN contributor",  pct: 72, color: C.iusaf_bd, bg: C.iusaf_bg },
  { name: "Country B", label: "Mid UN contributor",    pct: 20, color: C.tsac_bd,  bg: C.tsac_bg  },
  { name: "Country C", label: "Large UN contributor",  pct: 8,  color: C.sosac_bd, bg: C.sosac_bg },
];
s.addText("How inversion redistributes fund shares (illustrative):", {
  x: 0.5, y: 2.4, w: 9, h: 0.3, fontSize: 11, fontFace: "Calibri", color: C.muted, italic: true
});
bars.forEach(({ name, label, pct, color, bg }, i) => {
  const y = 2.78 + i * 0.62;
  s.addText(name,  { x: 0.5, y, w: 1.2, h: 0.4, fontSize: 12, fontFace: "Calibri", color: C.dark, valign: "middle", margin: 0 });
  s.addShape(pres.shapes.RECTANGLE, { x: 1.85, y: y + 0.04, w: pct * 0.065, h: 0.35, fill: { color: bg }, line: { color, width: 1 } });
  s.addText(`${pct}% of fund`, { x: 1.95, y: y + 0.04, w: pct * 0.065 - 0.1, h: 0.35, fontSize: 11, fontFace: "Calibri", bold: true, color, valign: "middle", margin: 0 });
  s.addText(label, { x: 6.6, y, w: 3, h: 0.4, fontSize: 11, fontFace: "Calibri", color: C.muted, valign: "middle", italic: true, margin: 0 });
});

callout(s, 0.5, 4.65, 9.0, 0.6,
  "Countries with a 0% UN assessment (such as the EU as an entity) receive a zero allocation and are shown separately in the app."
);

// ── SLIDES 8–9 — Recognising Stewardship (TSAC & SOSAC) ──────────────────
s = pres.addSlide();
sectionSlide(s, "4", "Recognising Stewardship", "TSAC & SOSAC — adjustments for different biodiversity responsibilities");

s = pres.addSlide();
contentHeader(s, "4 · Recognising Stewardship (TSAC & SOSAC)");

// TSAC card
s.addShape(pres.shapes.RECTANGLE, { x: 0.5, y: 0.85, w: 9, h: 1.4, fill: { color: C.tsac_bg }, line: { color: C.tsac_bd, width: 1 } });
s.addText("Large countries: terrestrial biodiversity stewardship (TSAC)", {
  x: 0.65, y: 0.92, w: 8.7, h: 0.3, fontSize: 12, fontFace: "Calibri", bold: true, color: C.tsac_tx, margin: 0
});
s.addText(
  "Some countries are very large and therefore carry greater responsibility for stewarding the world's " +
  "terrestrial biodiversity. A land-area weight recognises this stewardship role and adjusts their share accordingly.",
  { x: 0.65, y: 1.24, w: 8.7, h: 0.9, fontSize: 12, fontFace: "Calibri", color: "0F6E56", valign: "top", margin: 0 }
);

// SOSAC card
s.addShape(pres.shapes.RECTANGLE, { x: 0.5, y: 2.35, w: 9, h: 1.4, fill: { color: C.sosac_bg }, line: { color: C.sosac_bd, width: 1 } });
s.addText("Small Island Developing States: ocean stewardship and structural constraints (SOSAC)", {
  x: 0.65, y: 2.42, w: 8.7, h: 0.3, fontSize: 12, fontFace: "Calibri", bold: true, color: C.sosac_tx, margin: 0
});
s.addText(
  "Small Island Developing States carry significant ocean stewardship responsibilities and face recognised " +
  "structural constraints — geographic isolation, economic vulnerability, and disproportionate exposure to " +
  "environmental risks. An equal share among eligible SIDS balances these realities.",
  { x: 0.65, y: 2.74, w: 8.7, h: 0.9, fontSize: 12, fontFace: "Calibri", color: "854F0B", valign: "top", margin: 0 }
);

s.addText(
  "The three components are weighted so they always add up to 100% of the fund. Giving more weight to TSAC or " +
  "SOSAC reallocates money away from the IUSAF foundation. It would be a matter for Parties to agree the " +
  "appropriate balance points between IUSAF, TSAC and SOSAC.",
  { x: 0.5, y: 3.85, w: 9, h: 0.65, fontSize: 12, fontFace: "Calibri", color: C.muted }
);

// Blend bar — visual showing default 75 / 15 / 10 split
const blendW = 9.0;
// IUSAF segment
s.addShape(pres.shapes.RECTANGLE, { x: 0.5,                         y: 4.6, w: blendW * 0.75,        h: 0.38, fill: { color: C.iusaf_bg }, line: { color: C.iusaf_bd, width: 0.5 } });
s.addText("IUSAF 75%", { x: 0.5,                         y: 4.6, w: blendW * 0.75,        h: 0.38, fontSize: 10, fontFace: "Calibri", bold: true, color: C.iusaf_tx, align: "center", valign: "middle", margin: 0 });
// TSAC segment
s.addShape(pres.shapes.RECTANGLE, { x: 0.5 + blendW * 0.75 + 0.03, y: 4.6, w: blendW * 0.15 - 0.03, h: 0.38, fill: { color: C.tsac_bg  }, line: { color: C.tsac_bd,  width: 0.5 } });
s.addText("TSAC 15%",  { x: 0.5 + blendW * 0.75 + 0.03, y: 4.6, w: blendW * 0.15 - 0.03, h: 0.38, fontSize: 10, fontFace: "Calibri", bold: true, color: C.tsac_tx,  align: "center", valign: "middle", margin: 0 });
// SOSAC segment
s.addShape(pres.shapes.RECTANGLE, { x: 0.5 + blendW * 0.90 + 0.06, y: 4.6, w: blendW * 0.10 - 0.06, h: 0.38, fill: { color: C.sosac_bg }, line: { color: C.sosac_bd, width: 0.5 } });
s.addText("SOSAC 10%", { x: 0.5 + blendW * 0.90 + 0.06, y: 4.6, w: blendW * 0.10 - 0.06, h: 0.38, fontSize: 10, fontFace: "Calibri", bold: true, color: C.sosac_tx, align: "center", valign: "middle", margin: 0 });

// ── SLIDES 10–11 — Recognising IPLCs ─────────────────────────────────────
s = pres.addSlide();
sectionSlide(s, "5", "Recognising IPLCs", "Decision 16/2: at least 50% of Cali Funding allocated to IPLCs");

s = pres.addSlide();
contentHeader(s, "5 · Recognising IPLCs");

s.addText(
  "For simplicity the model is organised around countries as Parties. In accordance with Decision 16/2 " +
  "at least 50% of Cali Funding will be allocated to IPLCs. This is achieved by splitting the allocation in half.",
  { x: 0.5, y: 0.85, w: 9, h: 0.65, fontSize: 13, fontFace: "Calibri", color: C.muted }
);

// Amber callout — pathways to disbursement are a separate question from the formula
amberCallout(s, 0.5, 1.58, 9.5, 1.1, [
  { text: "It is important to recognise that ",                                                                           options: { color: C.amber_tx } },
  { text: "the amount allocated to IPLCs by the formula",                                                                 options: { bold: true, color: C.amber_tx } },
  { text: " and ",                                                                                                        options: { color: C.amber_tx } },
  { text: "appropriate pathways to disbursement",                                                                         options: { bold: true, color: C.amber_tx } },
  { text: " are separate considerations. Different pathways to disbursement may be appropriate at the national, "        +
          "subnational or UN regional/sub-regional level and may be informed by existing experience, guiding principles " +
          "and the programme of work of the Subsidiary Body on Article 8J and Other Provisions of the Convention.",       options: { color: C.amber_tx } },
]);

// Formula box
s.addShape(pres.shapes.RECTANGLE, { x: 0.5, y: 2.78, w: 9, h: 0.75, fill: { color: C.white }, line: { color: "CBCAC0", width: 0.5 } });
s.addText([
  { text: "IPLC share",       options: { bold: true, color: C.iplc_tx } },
  { text: "  =  total allocation  ×  chosen %",   options: { color: C.muted } },
  { text: "\n" },
  { text: "Government share", options: { bold: true, color: C.tsac_tx } },
  { text: "  =  total allocation  ×  the remainder", options: { color: C.muted } },
], { x: 0.65, y: 2.84, w: 8.7, h: 0.62, fontSize: 14, fontFace: "Calibri", valign: "middle", margin: 0 });

// Split bar example (50% IPLC, 50% Government)
s.addText("Example: a country receiving $5m from a $1 billion fund (50% IPLC share):", {
  x: 0.5, y: 3.63, w: 9, h: 0.28, fontSize: 11, fontFace: "Calibri", color: C.muted, italic: true
});
s.addText("IPLC share",       { x: 0.5, y: 3.99, w: 1.8, h: 0.34, fontSize: 11, fontFace: "Calibri", color: C.muted, valign: "middle", margin: 0 });
s.addShape(pres.shapes.RECTANGLE,  { x: 2.45, y: 4.01, w: 3.5, h: 0.32, fill: { color: C.iplc_bg }, line: { color: C.iplc_bd, width: 1 } });
s.addText("$2.50m — 50%",     { x: 2.45, y: 4.01, w: 3.5, h: 0.32, fontSize: 11, fontFace: "Calibri", bold: true, color: C.iplc_tx, align: "center", valign: "middle", margin: 0 });

s.addText("Government share", { x: 0.5, y: 4.42, w: 1.8, h: 0.34, fontSize: 11, fontFace: "Calibri", color: C.muted, valign: "middle", margin: 0 });
s.addShape(pres.shapes.RECTANGLE,  { x: 2.45, y: 4.44, w: 3.5, h: 0.32, fill: { color: C.tsac_bg  }, line: { color: C.tsac_bd,  width: 1 } });
s.addText("$2.50m — 50%",     { x: 2.45, y: 4.44, w: 3.5, h: 0.32, fontSize: 11, fontFace: "Calibri", bold: true, color: C.tsac_tx,  align: "center", valign: "middle", margin: 0 });

s.addText("Total: $5.00m ✓",  { x: 2.45, y: 4.84, w: 3.5, h: 0.26, fontSize: 11, fontFace: "Calibri", color: C.muted, align: "center" });

callout(s, 6.1, 3.99, 3.35, 1.15,
  "Every table shows: Total share, Government component, and IPLC component. A totals row confirms everything sums to the fund size."
);

// ── Write output ──────────────────────────────────────────────────────────
pres.writeFile({ fileName: outFile })
  .then(() => console.log(`✓ Written: ${outFile}`))
  .catch(err => { console.error("✗ Error:", err.message); process.exit(1); });
