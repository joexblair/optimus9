# 1008 — DEFINITION 2: JOE'S DELEGATION GATE INSIDE THE CHAIN, 15 ARMS

Joe 1008: *"does it improve if we sweep 6/9/12/16/20 minutes? 'improve' carries two
definitions: 1) likelihoodd of a correctly gated delegation, and 2) impact on our maemfe
baseline"*.

Driver `docs/octo-freedom/1005_scoring/_gatearm.py`, gate in `_chain10.run_leg` behind
`W_DGATE`, default `off`. 95 days, banked knob key ws12_baton_config.v1.

| the gate | width | handovers | refusals | legs | stops | fit NET | hold NET | all-95 NET | MFE/MAE | x-cross exits | >ws12 div exits |
|---|---|---|---|---|---|---|---|---|---|---|---|
| off | 6 min / 72 bars | 130 | 0 | 1623 | 201 | +0.7511 | +4.0801 | **+4.8312** | 0.9527 | 979 | 117 |
| once | 6 min / 72 bars | 83 | 57 | 1669 | 209 | -27.6265 | +9.3097 | **-18.3168** | 0.9394 | 1042 | 77 |
| retest | 6 min / 72 bars | 128 | 0 | 1623 | 201 | +1.1502 | +3.6017 | **+4.7519** | 0.9531 | 981 | 115 |
| off | 9 min / 108 bars | 112 | 0 | 1625 | 206 | +4.3283 | -22.8099 | **-18.4816** | 0.9339 | 990 | 102 |
| once | 9 min / 108 bars | 74 | 45 | 1666 | 206 | -13.7011 | -11.4158 | **-25.1169** | 0.9317 | 1046 | 67 |
| retest | 9 min / 108 bars | 109 | 0 | 1627 | 205 | +4.3283 | -23.8314 | **-19.5031** | 0.9316 | 993 | 100 |
| off | 12 min / 144 bars | 90 | 0 | 1651 | 204 | +5.5107 | -5.5844 | **-0.0737** | 0.9449 | 1024 | 86 |
| once | 12 min / 144 bars | 57 | 39 | 1683 | 210 | -12.3276 | -21.3115 | **-33.6391** | 0.9233 | 1069 | 54 |
| retest | 12 min / 144 bars | 87 | 0 | 1651 | 204 | +6.2942 | -5.6010 | **+0.6932** | 0.9429 | 1027 | 83 |
| off | 16 min / 192 bars | 76 | 0 | 1669 | 202 | +9.4051 | +10.2727 | **+19.6778** | 0.9552 | 1046 | 74 |
| once | 16 min / 192 bars | 53 | 27 | 1695 | 206 | -2.5372 | -2.2448 | **-4.7820** | 0.9354 | 1082 | 53 |
| retest | 16 min / 192 bars | 75 | 0 | 1671 | 203 | +9.4051 | +3.8654 | **+13.2705** | 0.9501 | 1048 | 73 |
| off | 20 min / 240 bars | 65 | 0 | 1683 | 204 | +6.7503 | +8.3587 | **+15.1090** | 0.9544 | 1069 | 63 |
| once | 20 min / 240 bars | 48 | 18 | 1705 | 209 | -4.8269 | -11.4743 | **-16.3012** | 0.9369 | 1097 | 46 |
| retest | 20 min / 240 bars | 65 | 0 | 1683 | 204 | +6.7503 | +8.3587 | **+15.1090** | 0.9544 | 1069 | 63 |

| width | gate | fit delta | hold delta | all delta | MFE/MAE delta | positive on both halves |
|---|---|---|---|---|---|---|
| 6 min | once | -28.3776 | +5.2296 | -23.1480 | -0.0133 | no |
| 6 min | retest | +0.3991 | -0.4784 | -0.0793 | +0.0004 | YES |
| 9 min | once | -18.0294 | +11.3941 | -6.6353 | -0.0022 | no |
| 9 min | retest | +0.0000 | -1.0215 | -1.0215 | -0.0024 | no |
| 12 min | once | -17.8383 | -15.7271 | -33.5654 | -0.0216 | no |
| 12 min | retest | +0.7835 | -0.0166 | +0.7669 | -0.0019 | no |
| 16 min | once | -11.9423 | -12.5175 | -24.4598 | -0.0198 | no |
| 16 min | retest | +0.0000 | -6.4073 | -6.4073 | -0.0051 | YES |
| 20 min | once | -11.5772 | -19.8330 | -31.4102 | -0.0175 | no |
| 20 min | retest | +0.0000 | +0.0000 | +0.0000 | +0.0000 | YES |
