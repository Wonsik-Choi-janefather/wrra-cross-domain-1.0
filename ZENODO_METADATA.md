# Zenodo Metadata

## Title

WRRA Cross Domain 1.0 Comparative Exact Validation in Games Power Grids and Scheduling

## Subtitle

Minimal Sufficient State Residue and Constraint Preserving Rendering

## Resource type

Software with accompanying technical report

## Creator

Wonsik Choi  
janefather@gmail.com

## Description

WRRA Cross Domain 1.0 tests whether one fixed execution architecture can be instantiated without structural change in three distinct computational domains: games, electric power grids, and machine scheduling. WRRA means Wonsik Reality Renderer Architecture and was originally developed as a toy model for explaining how a world can execute through Source, Law, State and Residue, Boundary, Common Carrier, Update, Renderer, Phenotype, and Ledger.

The release applies four common tests: state sufficiency, constructive residue necessity, exact objective preservation under a certified Renderer, and within-domain computation reduction. It reproduces the published WRRA Game 1.0 exhaustive result of 6,036,001 reachable 4 by 4 Connect K states and 23,453,344 legal edges, with zero all-state minimax mismatches and a root reduction from 245,560 alpha-beta nodes to 32. The separate 3 by 3 simple-ko Go census again finds 752 visible-state classes whose legal action sets depend on previous-board residue.

Two new exact experiments are included. A three-bus six-step DC grid with thermal-memory constraints reaches 4,409 states; certified action quotienting reduces 28,517 labelled action evaluations to 15,242 with zero exact cost-to-go mismatches. A six-job two-machine sequence-dependent scheduling problem reaches 1,103 states; exact job-label and machine-symmetry quotienting reduces 4,188 action evaluations to 3,090 with zero exact makespan mismatches. Both domains include same-visible-state witnesses in which omitted residue changes exact feasibility or value.

The package contains source code, deterministic tests, the frozen analysis plan, published and reproduced Ledgers, JSON and CSV results, figures, an English technical report, a Korean summary, licenses, and SHA-256 hashes. Passing three finite-domain tests supports portability of the WRRA execution kernel; it is not a proof of universal applicability. Work units differ by domain and the reduction percentages are not cross-domain performance scores.

## Keywords

WRRA; Wonsik Reality Renderer Architecture; minimal sufficient state; residue; state sufficiency; exact quotient; certified pruning; state abstraction; exhaustive validation; game search; Go; Connect K; power grid; DC power flow; thermal memory; scheduling; sequence dependent setup; explainable AI; complex systems; reproducible research

## License

MIT for source code and CC BY 4.0 for reports data figures and documentation

## Related identifiers

- 10.5281/zenodo.22650956 WRRA Core 1.0
- 10.5281/zenodo.22985378 WRRA Game 1.0
- 10.5281/zenodo.22330256 related WRRA Grid record
- 10.5281/zenodo.22331940 related WRRA Grid record
- 10.5281/zenodo.22447864 related WRRA Grid record
