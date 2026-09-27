#!/usr/bin/env python3
"""Build the scientific figures for WRRA Cross Domain 1.0."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch


NAVY = "#17365D"
BLUE = "#5B9BD5"
PALE = "#DCE6F1"
DARK = "#202020"
GRID = "#D9D9D9"


def architecture_figure(output: Path) -> None:
    fig, ax = plt.subplots(figsize=(12, 3.6))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 4)
    ax.axis("off")
    boxes = [
        (0.25, "Source and\nBoundary"),
        (2.65, "Law State\nResidue Carrier"),
        (5.05, "Renderer\nCertified quotient"),
        (7.45, "Bounded\nSearch or Action"),
        (9.85, "Phenotype\nand Ledger"),
    ]
    for index, (x, label) in enumerate(boxes):
        box = FancyBboxPatch(
            (x, 1.25),
            1.9,
            1.35,
            boxstyle="round,pad=0.06,rounding_size=0.08",
            facecolor=PALE if index not in (2, 4) else "#E2F0D9",
            edgecolor=NAVY,
            linewidth=1.4,
        )
        ax.add_patch(box)
        ax.text(
            x + 0.95,
            1.92,
            label,
            ha="center",
            va="center",
            fontsize=10.5,
            color=DARK,
            weight="semibold" if index in (2, 4) else "normal",
        )
        if index < len(boxes) - 1:
            arrow = FancyArrowPatch(
                (x + 1.92, 1.92),
                (boxes[index + 1][0] - 0.04, 1.92),
                arrowstyle="-|>",
                mutation_scale=13,
                linewidth=1.2,
                color=NAVY,
            )
            ax.add_patch(arrow)
    ax.text(
        6,
        3.25,
        "Fixed execution grammar across three domains",
        ha="center",
        fontsize=14,
        weight="bold",
        color=DARK,
    )
    ax.text(
        6,
        0.55,
        "Domain specific laws and variables change while the structural roles and falsification tests remain fixed",
        ha="center",
        fontsize=9.5,
        color="#555555",
    )
    fig.tight_layout()
    fig.savefig(output, dpi=240, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def evidence_figure(results_path: Path, output: Path) -> None:
    payload = json.loads(results_path.read_text(encoding="utf-8"))
    domains = payload["domains"]
    labels = ["Game", "Power grid", "Scheduling"]
    retained = [
        100 * item["renderer_work_units"] / item["full_work_units"]
        for item in domains
    ]
    residue = [item["residue_sensitive_visible_classes"] for item in domains]
    colors = [NAVY, BLUE, "#70AD47"]

    fig, axes = plt.subplots(1, 2, figsize=(11.5, 4.8))
    ax = axes[0]
    bars = ax.bar(labels, retained, color=colors, width=0.62)
    ax.set_yscale("log")
    ax.set_ylabel("Renderer work remaining percent log scale")
    ax.set_title("Within domain work after certified reduction", weight="bold")
    ax.grid(axis="y", color=GRID, linewidth=0.8, which="both")
    ax.set_axisbelow(True)
    for bar, value in zip(bars, retained):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            value * 1.25,
            f"{value:.4f}%" if value < 0.1 else f"{value:.2f}%",
            ha="center",
            va="bottom",
            fontsize=9,
        )

    ax = axes[1]
    bars = ax.bar(labels, residue, color=colors, width=0.62)
    ax.set_yscale("log")
    ax.set_ylabel("Visible state classes log scale")
    ax.set_title("Classes that require residue", weight="bold")
    ax.grid(axis="y", color=GRID, linewidth=0.8, which="both")
    ax.set_axisbelow(True)
    for bar, value in zip(bars, residue):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            value * 1.25,
            f"{value:,}",
            ha="center",
            va="bottom",
            fontsize=9,
        )

    fig.text(
        0.5,
        0.015,
        "Counts and work units have different domain scopes and are not cross domain performance scores",
        ha="center",
        fontsize=9,
        color="#555555",
    )
    fig.tight_layout(rect=(0, 0.05, 1, 1))
    fig.savefig(output, dpi=240, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def equation_figure(output: Path, lines: list[str], width: float = 10.5) -> None:
    height = 0.82 + 0.56 * (len(lines) - 1)
    fig, ax = plt.subplots(figsize=(width, height))
    ax.axis("off")
    if len(lines) == 1:
        positions = [0.5]
    else:
        positions = [0.72 - 0.44 * index for index in range(len(lines))]
    for y, line in zip(positions, lines):
        ax.text(
            0.5,
            y,
            line,
            ha="center",
            va="center",
            fontsize=18,
            color="#000000",
            transform=ax.transAxes,
        )
    fig.savefig(output, dpi=300, bbox_inches="tight", pad_inches=0.08, facecolor="white")
    plt.close(fig)


def equation_figures(output_dir: Path) -> None:
    equation_figure(
        output_dir / "equation_common_state.png",
        [
            r"$S_t=(X_t,R_t),\qquad (S_{t+1},c_t)=L_D(S_t,a_t),\quad a_t\in A_D(S_t)$"
        ],
    )
    equation_figure(
        output_dir / "equation_renderer.png",
        [
            r"$a\sim_S a'\Longleftrightarrow C_D(T_D(S,a))=C_D(T_D(S,a'))$",
            r"$\mathrm{and}\qquad c(S,a)=c(S,a')$",
        ],
    )
    equation_figure(
        output_dir / "equation_grid.png",
        [
            r"$B_{\mathrm{red}}\theta=P,\qquad f_{ij}=b_{ij}(\theta_i-\theta_j)$",
            r"$h'_{ij}=\frac{1}{2}h_{ij}+\max\left(0,|f_{ij}|-\bar f_{ij}\right)$",
        ],
    )
    equation_figure(
        output_dir / "equation_scheduling.png",
        [
            r"$s(\ell,f)=0\ \mathrm{if}\ \ell=\varnothing\ \mathrm{or}\ \ell=f,\qquad s(\ell,f)=2\ \mathrm{otherwise}$",
            r"$u'_m=u_m+s(\ell_m,f_j)+p_j$",
        ],
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--results", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    architecture_figure(args.output_dir / "wrra_execution_grammar.png")
    evidence_figure(args.results, args.output_dir / "cross_domain_evidence.png")
    equation_figures(args.output_dir)


if __name__ == "__main__":
    main()
