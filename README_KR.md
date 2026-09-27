# WRRA Cross Domain 1 0

## 게임 전력망 스케줄링의 비교 전수검증

WRRA는 **Wonsik Reality Renderer Architecture**입니다. 우주를 설명하기 위해 만든 toy model의 실행 구조가 게임에만 맞는 표현인지, 서로 다른 계산 문제에서도 같은 검증조건을 견디는지를 확인했습니다.

저장소: <https://github.com/Wonsik-Choi-janefather/wrra-cross-domain-1.0>

이번 연구는 다음 구조를 세 분야에서 고정했습니다.

`Source -> Law -> State and Residue -> Boundary and Common Carrier -> Update -> Renderer -> Search or Action -> Phenotype -> Ledger`

분야별 법칙과 변수는 달라지지만 구조와 판정기준은 바꾸지 않았습니다.

## 핵심 결과

| 분야 | 전수검증 범위 | residue 민감 가시상태 | Renderer 값 불일치 | 계산 축약 |
|---|---|---:|---:|---:|
| 게임 | 4 곱하기 4 Connect K 도달상태 6,036,001개 | 별도 3 곱하기 3 Go에서 752개 | 0 | 루트 245,560 노드에서 32 노드 |
| 전력망 | 3버스 6단계 도달상태 4,409개 | 1개 | 0 | 행동평가 28,517회에서 15,242회 |
| 스케줄링 | 2기계 6작업 도달상태 1,103개 | 37개 | 0 | 행동평가 4,188회에서 3,090회 |

세 분야의 계산 단위가 다르므로 축약률끼리 우열을 비교할 수는 없습니다. 그러나 **인증된 축약 뒤 정확값 불일치가 세 분야 모두 0개**라는 판정은 공통입니다.

residue가 단순한 비유가 아니라는 반례도 확보했습니다.

- 전력망에서는 시점과 수요가 같아도 선로 열 residue가 다르면 안전행동이 달라지고 정확 잔여비용이 10과 12로 갈렸습니다.
- 스케줄링에서는 남은 작업 종류와 기계 가용시간이 같아도 직전 작업군 residue가 다르면 정확 makespan이 10과 11로 갈렸습니다.
- 기존 Go 전수검증에서는 같은 판과 차례라도 직전 판 residue에 따라 패 되따내기의 합법성이 달라지는 가시상태 동치류가 752개였습니다.

## 이번 연구가 새로 확정한 것

이 결과의 가치는 세 문제를 WRRA 용어로 다시 설명했다는 데 있지 않습니다. 같은 실행 문법에 같은 반증조건을 적용했고, 상태 충돌 반례와 전 상태 값 대조를 통과했다는 데 있습니다.

1. **구조의 이식성**  
   게임의 수, 전력망의 조류, 스케줄링의 작업배정은 서로 다르지만 Law, residue, Renderer, phenotype, Ledger의 역할은 바꾸지 않고 실행됐습니다.

2. **residue의 구성적 필요성**  
   겉으로 같은 현재가 서로 다른 합법성, 안전성 또는 정확값을 요구하는 실제 도달상태 쌍을 제시했습니다.

3. **Renderer의 정확성 기준**  
   새 두 분야에서는 완전한 다음 상태와 비용이 같은 행동만 묶었습니다. 추측이나 미래예측이 아니라 Law가 만든 동치 전이를 하나로 줄인 것입니다.

4. **정확성과 효율성의 분리**  
   먼저 전 상태 값 불일치가 0인지 검사했고, 그 뒤에만 계산절감률을 보고했습니다.

5. **부정적 결과의 보존**  
   기존 전력망 기억 절제실험에서 실패흔적 기억은 자기 비용을 회수하지 못했습니다. WRRA가 복잡성이나 기억을 무조건 추가하는 틀이 아니라, 필요한 residue와 불필요한 기억을 구분하는 틀임을 그대로 반영했습니다.

## 정확한 주장 범위

이번 결과는 세 유한 문제에서 WRRA 실행 구조의 이식성을 지지합니다. 모든 복잡계에 보편적으로 적용된다는 증명은 아닙니다. 전력망은 손실 없는 DC 조류와 단순 열기억을 사용했고, 스케줄링은 작은 결정론적 문제이며, 게임의 완전검증도 명시된 소형 보드 범위입니다.

## 재현

새 전력망과 스케줄링 실험은 Python 표준 라이브러리만으로 수초 안에 재현됩니다.

```bash
python src/wrra_cross_domain_1_0.py \
  --game-json baselines/wrra_game_0_2_results_published.json \
  --game-reproduced-json results/reproduced_game_0_2_results.json \
  --grid-scarcity-json baselines/wrra_grid_scarcity_stress_summary_published.json \
  --output-dir results/reproduced_cross_domain

python -m unittest discover -s tests -v
```

603만 상태 게임 전수검증을 처음부터 다시 실행하려면 다음 명령을 사용합니다.

```bash
python vendor/wrra_game_0_2.py \
  --output results/reproduced_game_0_2_results.json
```

이 저장소는 기존 Game 1.0을 대체하지 않는 교차영역 확장 연구입니다: <https://github.com/Wonsik-Choi-janefather/wrra-game-1.0>.

## 저자

최원식 Wonsik Choi  
janefather@gmail.com
