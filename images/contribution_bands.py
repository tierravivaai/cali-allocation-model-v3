import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

bands = [
    {"label": "Band 1", "range": "≤ 0.001%",   "weight": 1.50, "parties": "31 parties\n(LDCs & SIDS)", "amount": 4_262_575, "ratio": "1.00×"},
    {"label": "Band 2", "range": "0.001–0.01%", "weight": 1.30, "parties": "59 parties",               "amount": 3_693_965, "ratio": "0.87×"},
    {"label": "Band 3", "range": "0.01–0.1%",   "weight": 1.10, "parties": "30 parties",               "amount": 3_125_355, "ratio": "0.73×"},
    {"label": "Band 4", "range": "0.1–1.0%",    "weight": 0.95, "parties": "18 parties",               "amount": 2_700_612, "ratio": "0.63×"},
    {"label": "Band 5", "range": "1.0–10.0%",   "weight": 0.75, "parties": "3 parties\n(BR, IN, MX)", "amount": 2_131_733, "ratio": "0.50×"},
    {"label": "Band 6", "range": "> 10.0%",     "weight": 0.40, "parties": "1 party\n(China)",        "amount": 1_137_190, "ratio": "0.27×"},
]

colors = ["#1D9E75", "#1D9E75", "#378ADD", "#378ADD", "#BA7517", "#D85A30"]
x = np.arange(len(bands))
bar_width = 0.6
amounts = [b["amount"] for b in bands]

fig, ax = plt.subplots(figsize=(11, 6.5))
fig.patch.set_facecolor("#ffffff")
ax.set_facecolor("#ffffff")

bars = ax.bar(x, amounts, width=bar_width, color=colors, linewidth=0.6,
              edgecolor=[c + "aa" for c in colors], zorder=3)

# Step connector lines between bars
for i in range(len(bands) - 1):
    ax.plot([x[i] + bar_width / 2, x[i + 1] - bar_width / 2],
            [amounts[i + 1], amounts[i + 1]],
            color="#aaaaaa", linewidth=0.8, linestyle="--", zorder=4)

# Ratio labels above each bar
for i, b in enumerate(bands):
    ax.text(x[i], amounts[i] + 60_000, b["ratio"],
            ha="center", va="bottom", fontsize=9.5, color="#555555", fontweight="bold")

# Inside-bar annotations
for i, b in enumerate(bands):
    mid_y = amounts[i] / 2
    ax.text(x[i], amounts[i] - 80_000,
            f"{b['label']}\n{b['range']}\nw = {b['weight']:.2f}",
            ha="center", va="top", fontsize=8, color="white", linespacing=1.5)
    ax.text(x[i], mid_y - 280_000,
            b["parties"],
            ha="center", va="center", fontsize=7.5, color="white", linespacing=1.4, alpha=0.9)

# Axes formatting
ax.set_xticks(x)
ax.set_xticklabels([b["label"] for b in bands], fontsize=10)
ax.set_ylabel("Per-party contribution ($1 bn fund)", fontsize=10, color="#444444")
ax.set_xlabel("Band  (UN assessed share →)", fontsize=10, color="#444444")
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"${v/1e6:.1f}M"))
ax.set_ylim(0, 5_000_000)
ax.tick_params(axis="both", colors="#666666", labelsize=9)
for spine in ["top", "right"]:
    ax.spines[spine].set_visible(False)
for spine in ["left", "bottom"]:
    ax.spines[spine].set_color("#dddddd")
ax.yaxis.grid(True, color="#eeeeee", linewidth=0.6, zorder=0)
ax.set_axisbelow(True)

# Legend patches for color groups
legend_handles = [
    mpatches.Patch(color="#1D9E75", label="Bands 1–2  (highest weight, LDCs / SIDS)"),
    mpatches.Patch(color="#378ADD", label="Bands 3–4  (mid weight)"),
    mpatches.Patch(color="#BA7517", label="Band 5  (Brazil, India, Mexico)"),
    mpatches.Patch(color="#D85A30", label="Band 6  (China only)"),
]
ax.legend(handles=legend_handles, loc="upper right", fontsize=8,
          framealpha=0.7, edgecolor="#dddddd")

ax.set_title("Contribution bands — per-party allocation from a $1 bn fund",
             fontsize=12, color="#222222", pad=14)

plt.tight_layout()
plt.savefig("contribution_bands.png", dpi=150, bbox_inches="tight")
plt.show()
