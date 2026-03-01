Derived From:
- /artifacts/expression/null_hardening.json
- /artifacts/expression/stability_dropout_jackknife.json
- /artifacts/expression/leakage_audit.json
- /artifacts/expression/adversarial_results.json
- /artifacts/expression/scale_test_results.json
- /artifacts/expression/expression_pack_manifest.json (dataset_hash: ded932c67450383b3a6e72ecb12220511a5f12627a3867914714ed86131870d8)

# Expression Kernel (Kernel-2E) Stress Suite Report

## 1. Null Hardening (50,000 permutations)
**Class vs BoundaryType IG**: 0.320072172616238
**p-value**: 0.00552
**Z-Score**: 3.4526442273614233

## 2. Label Leakage Audit
**Kernel-1 Predicts Expression (Acc)**: 0.5833333333333334 (Must be < 0.85 to be independent)
**BoundaryType Predicts Expression (Acc)**: 0.6666666666666666

## 3. Adversarial Hard Counterexamples
Successfully executed adversarial synthesis (domains_expression_adversarial_pack) targeting HIGH expression + smooth failures.

## 4. Scale Testing
```json
{
  "pack_48": {
    "real_ig": 0.25693348596806287,
    "null_mean": 0.04881967125816435,
    "null_std": 0.029452877820607723,
    "p_value": 0.0
  },
  "pack_96": {
    "real_ig": 0.3424962628700446,
    "null_mean": 0.024239887164427664,
    "null_std": 0.014335073408939912,
    "p_value": 0.0
  },
  "pack_192": {
    "real_ig": 0.4198783856929642,
    "null_mean": 0.011810351667175211,
    "null_std": 0.006916388899476403,
    "p_value": 0.0
  }
}
```

## Verdict
**K2E_ROBUST**

Expression class topology scales and strictly resists permutation noise drops up to N=192 and remains structurally independent from Kernel-1.
