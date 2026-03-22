# AGENTS.md — Cali Fund Allocation Model Explainer

## What this repository contains

This folder holds two output artefacts and the code that generates them, for the **Cali Fund Allocation Model (Inverted UN Scale of Assessment Option)** explainer.

| File | Description |
|------|-------------|
| `cali_fund_explainer.html` | Standalone interactive explainer. Works in any browser. No server needed. |
| `generate_pptx.js` | Node.js script that generates the 11-slide PowerPoint presentation. |

---

## Conceptual overview

The explainer covers five concepts in a fixed narrative sequence. All content decisions were made deliberately — do not reorder or rename sections without understanding the policy context.

| # | Tab / Slide title | Panel heading | Purpose |
|---|-------------------|---------------|---------|
| 1 | Purpose | Purpose | What the model is for and what it is not |
| 2 | The Formula | The Formula | IUSAF as foundation; TSAC and SOSAC as adjustments |
| 3 | Equity | Establishing Equity (IUSAF) | How the UN Scale inversion works |
| 4 | Stewardship | Recognising Stewardship (TSAC & SOSAC) | Why and how the two adjustments work |
| 5 | IPLCs | Recognising IPLCs | Decision 16/2 requirement; separation of formula and disbursement pathways |

### Key terminology

| Term | Full name | Role |
|------|-----------|------|
| IUSAF | Inverted UN Scale of Assessment Foundation | Base allocation — the equity foundation |
| TSAC  | Terrestrial Stewardship Allocation Component | Adjustment for large countries with biodiversity stewardship responsibilities |
| SOSAC | SIDS Ocean Stewardship Allocation Component | Adjustment for Small Island Developing States' ocean stewardship and structural constraints |
| IPLC  | Indigenous Peoples and Local Communities | At least 50% of each allocation per Decision 16/2 |

### Formula

```
Final Share = (1 − β − γ) × IUSAF  +  β × TSAC  +  γ × SOSAC
Allocation  = Fund Size × Final Share
```

Default weights: IUSAF 75% (β=0.15, γ=0.10). Weights always sum to 100%.

### Colour coding

Every component has a consistent colour used across both the HTML and PPTX:

| Component | Background | Border | Text |
|-----------|-----------|--------|------|
| IUSAF | `#E6F1FB` (blue) | `#378ADD` | `#0C447C` |
| TSAC  | `#E1F5EE` (green) | `#1D9E75` | `#085041` |
| SOSAC | `#FAEEDA` (amber) | `#EF9F27` | `#633806` |
| IPLC  | `#EEEDFE` (purple) | `#7F77DD` | `#3C3489` |

Teal callouts (`#028090`) are used for key takeaways. Amber callouts (`#BA7517`) are used for important caveats — currently only the IPLC pathways-to-disbursement note.

---

## HTML file — `cali_fund_explainer.html`

### What it is

A fully self-contained single-file interactive explainer. All CSS and JavaScript are inline. No external dependencies, no server required.

### How to use it

Open directly in any modern browser:
```
open cali_fund_explainer.html          # macOS
start cali_fund_explainer.html         # Windows
xdg-open cali_fund_explainer.html      # Linux
```

Or host it on any static file server, embed it in a webpage, or distribute as a file attachment.

### Structure

```
<head>          CSS — layout, colours, component styles
<body>
  <header>      Title + option subtitle + introductory description
  <nav>         Five tab buttons (.step-btn), one per concept
  <panels>      Five .panel divs — only the active one is visible
    #p-purpose
    #p-formula
    #p-equity      interactive slider (UN share → fund share)
    #p-stewardship interactive sliders (TSAC β, SOSAC γ)
    #p-iplc        interactive slider (IPLC % split)
  <footer>      Attribution and disclaimer
<script>        show(), updateInversion(), updateBlend(), updateSplit()
```

### Editing guidance

**Changing text content:** Edit directly inside the relevant `<div class="panel" id="p-...">` block.

**Changing the title:** Update both:
- `<title>` in `<head>`
- `<h1>` and the italic subtitle `<p>` in `<header>`

**Changing callout style:**
- Teal callout: `border-left:3px solid #3266ad` + `background:#f1efe8`
- Amber callout: `border-left:3px solid #ba7517` + `background:#fef9ee`

**Adding a new panel:** Add a `.step-btn` to the nav and a matching `<div class="panel" id="p-newname">` to the body. Update the `show()` function if the panel needs interactive initialisation.

**Slider ranges:** The IPLC slider is fixed at 50–80% per Decision 16/2. Do not lower the minimum below 50 without policy justification.

---

## PowerPoint script — `generate_pptx.js`

### What it produces

An 11-slide `.pptx` file in 16:9 format (10" × 5.625"). Each concept gets:
- A **section divider slide** (dark forest background, large section number)
- A **content slide** (cream background, dark header bar)

Plus one opening title slide.

### Dependencies

```bash
npm install -g pptxgenjs
# or locally:
npm install pptxgenjs
```

### Running it

```bash
# Default output (cali_fund_explainer.pptx in current directory)
node generate_pptx.js

# Custom output path
node generate_pptx.js --out ./output/my_deck.pptx
```

### Key design rules (do not break these)

1. **Never use `#` prefix on hex colours.** PptxGenJS will silently corrupt the file.
2. **Never share option objects between two `addShape`/`addText` calls.** PptxGenJS mutates them in-place. Always pass fresh object literals, or use a factory function. The `amberCallout()` helper already does this correctly.
3. **Never use `ROUNDED_RECTANGLE` with accent border overlays.** Rectangular accent bars will not cover rounded corners. Use `RECTANGLE` throughout.
4. **All coordinates are in inches.** Slide is 10" wide × 5.625" tall. Safe content area: x 0.5–9.5, y 0.7–5.4 (leaving margin for header bar and bottom edge).

### Helper functions

| Function | Purpose |
|----------|---------|
| `titleSlide(slide)` | Renders the opening title slide |
| `sectionSlide(slide, num, title, sub)` | Dark divider slide between sections |
| `contentHeader(slide, title)` | Header bar for content slides |
| `colorCard(slide, x, y, w, h, bg, bd, label, labelColor, body, bodyColor)` | Coloured info card |
| `callout(slide, x, y, w, h, text)` | Teal left-border callout box |
| `amberCallout(slide, x, y, w, h, richText)` | Amber left-border callout (rich text array) |

### Adding a new slide

```javascript
// Section divider
s = pres.addSlide();
sectionSlide(s, "6", "New Section Title", "Optional subtitle");

// Content slide
s = pres.addSlide();
contentHeader(s, "6 · New Section Title");
// ... add content using helpers or direct addText/addShape calls
```

### QA process

After any edit, always run the full visual QA cycle:

```bash
node generate_pptx.js

# Convert to images (requires LibreOffice and poppler)
python /path/to/soffice.py --headless --convert-to pdf cali_fund_explainer.pptx
rm -f slide-*.jpg
pdftoppm -jpeg -r 150 cali_fund_explainer.pdf slide
ls -1 "$PWD"/slide-*.jpg
```

Then inspect every slide image for:
- Overlapping text or shapes
- Text cut off at box boundaries
- Elements too close to slide edges (< 0.5")
- Low contrast text
- Incorrect colour coding (IUSAF should always be blue, TSAC green, SOSAC amber, IPLC purple)

---

## What to keep consistent across both files

If you change wording in one file, change it in the other. The key passages that appear in both are:

| Location | Content |
|----------|---------|
| IPLC panel intro | "For simplicity the model is organised around countries as Parties. In accordance with Decision 16/2..." |
| Amber callout | "It is important to recognise that **the amount allocated to IPLCs by the formula** and **appropriate pathways to disbursement** are separate considerations..." (full text includes Article 8J reference) |
| Formula display | IUSAF = foundation, TSAC = adjustment for large countries, SOSAC = adjustment for island states |
| Callout — equity | EU entity note (0% assessment = zero allocation) |
| Callout — formula | "IUSAF is the foundation. TSAC and SOSAC are adjustments..." |

---

## Disclaimer

All content in both outputs carries the standard disclaimer:

> All figures are illustrative modelling outputs for exploratory purposes. They do not represent entitlements or predetermined disbursements.

This must appear on the title slide of the PPTX and in the footer of the HTML. Do not remove it.

---

## Attribution

Prepared by Paul Oldham, [TierraViva AI](https://www.tierraviva.ai/).  
Source code available on [GitHub](https://github.com/tierravivaai/cali-allocation-model-v2).
