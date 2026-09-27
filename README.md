# WRRA Cross Domain 1.0

## Comparative exact validation in games power grids and scheduling

WRRA means **Wonsik Reality Renderer Architecture**. Wonsik Choi originally built it as a toy model for explaining how a world can execute through a small set of structural roles. This release asks a narrower and falsifiable question: can the same execution grammar be instantiated in three unrelated computational domains without changing the grammar, and can its certified Renderer reduce work without changing the exact answer?

Repository: <https://github.com/Wonsik-Choi-janefather/wrra-cross-domain-1.0>

The fixed grammar is:

`Source -> Law -> State and Residue -> Boundary and Common Carrier -> Update -> Renderer -> Search or Action -> Phenotype -> Ledger`

The domain laws and variables change. The grammar and tests do not.

## Main result

All three declared finite tests passed.

| Domain | Exact scope | Residue sensitive visible classes | Exact value mismatches after Renderer | Full work | Renderer work | Reduction |
|---|---|---:|---:|---:|---:|---:|
| Game | Every reachable state of 4x4 Connect K with k 3 | 752 in the separate 3x3 simple ko Go census | 0 | 245,560 nodes | 32 nodes | 99.9870% |
| Power grid | Every state reachable over a six step three bus DC trace | 1 | 0 | 28,517 action evaluations | 15,242 | 46.5512% |
| Scheduling | Every state reachable from six jobs on two machines | 37 | 0 | 4,188 action evaluations | 3,090 | 26.2178% |

Work units differ by domain and must not be compared as if they were one benchmark. The exactness result is comparable: every certified reduction preserved the exact objective in its stated scope.

The two new residue witnesses are stronger than a verbal analogy.

- In the power grid model, the same time and demand with different line heat residues gives safe action sets that differ and exact remaining costs of 10 and 12.
- In the scheduling model, the same remaining job types and machine availability with different last family residues gives exact makespans of 10 and 11.

The Game 1.0 exhaustive computation was also rerun from the published source. All seven declared invariants matched the published ledger, including 6,036,001 Connect K states, 23,453,344 legal edges, zero all state value mismatches, and 752 Go residue sensitive visible classes.

## What this supports

The result supports **cross domain portability of the WRRA execution architecture** across three finite test systems. It also shows a precise role for residue: present information omitted by the visible state can be necessary to determine the legal transition set or exact value.

The result does not prove that WRRA is universally applicable, that the toy grid represents an operating power system, or that the three reduction percentages are directly comparable. The new grid uses lossless DC flow and a simplified thermal memory. The scheduling problem is small and deterministic. The game result is exact only for the declared small boards.

## Files

```text
WRRA_Cross_Domain_1_0
├── README.md
├── README_KR.md
├── ZENODO_METADATA.md
├── .zenodo.json
├── CITATION.cff
├── MANIFEST.sha256
├── LICENSE
├── LICENSE-CODE
├── LICENSE-CONTENT
├── requirements.txt
├── protocol
│   └── preregistered_analysis_plan.json
├── src
│   └── wrra_cross_domain_1_0.py
├── tests
│   └── test_cross_domain.py
├── baselines
│   ├── wrra_game_0_2_results_published.json
│   ├── wrra_grid_scarcity_stress_summary_published.json
│   └── provenance.json
├── vendor
│   └── wrra_game_0_2.py
├── results
│   ├── cross_domain_results.json
│   ├── cross_domain_summary.csv
│   ├── reproduced_game_0_2_results.json
│   └── verification_summary.json
├── figures
├── paper
└── tools
```

## Fast reproduction

Python 3.11 or newer is recommended. The exact cross domain code uses only the Python standard library.

```bash
python src/wrra_cross_domain_1_0.py \
  --game-json baselines/wrra_game_0_2_results_published.json \
  --game-reproduced-json results/reproduced_game_0_2_results.json \
  --grid-scarcity-json baselines/wrra_grid_scarcity_stress_summary_published.json \
  --output-dir results/reproduced_cross_domain

python -m unittest discover -s tests -v
```

The new finite grid and scheduling tests finish in seconds on a typical computer.

## Full game reproduction

The 6,036,001 state Game 0.2 enumeration can take several minutes and more memory.

```bash
python vendor/wrra_game_0_2.py \
  --output results/reproduced_game_0_2_results.json
```

Then run the fast reproduction command above to compare the seven declared invariants.

## Renderer certification rule

For the new finite domains, the Renderer receives every Law permitted action, computes the complete one step successor and immediate objective contribution, and groups actions only when their future relevant canonical successor and cost are identical. It retains one representative per equivalence class. This is exact quotienting, not heuristic prediction.

Heuristic ranking can be added later, but it must be reported separately and may not be called certified pruning unless exact agreement is demonstrated.

## Prior work preserved

- WRRA Core 1.0 DOI `10.5281/zenodo.22650956`
- WRRA Game 1.0 DOI `10.5281/zenodo.22985378`
- Related WRRA Grid records DOI `10.5281/zenodo.22330256`, `10.5281/zenodo.22331940`, and `10.5281/zenodo.22447864`

The historical Game and Grid studies retain their original scope and status. The analysis plan is prospective only for the new finite grid and scheduling runs and retrospective for the harmonized use of previously published results.

This repository is a cross-domain extension, not a replacement for the historical Game 1.0 repository: <https://github.com/Wonsik-Choi-janefather/wrra-game-1.0>.

## License

- Source code in `src`, `tests`, `tools`, and `vendor` is released under the MIT License.
- Reports, figures, protocol, machine readable results, and documentation are released under Creative Commons Attribution 4.0 International.

See `LICENSE`, `LICENSE-CODE`, and `LICENSE-CONTENT`.

## Author

Wonsik Choi  
Email: janefather@gmail.com
