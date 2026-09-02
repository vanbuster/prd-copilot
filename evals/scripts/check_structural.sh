#!/usr/bin/env bash
# 结构机判：吃一个 PRD 文件，输出 L1/L2 可机判断言的逐条结果。零依赖（grep/wc/awk）。
# 用法: ./check_structural.sh <prd.md>
set -euo pipefail
[ $# -eq 1 ] && [ -f "$1" ] || { echo "用法: $0 <prd.md>" >&2; exit 2; }
F="$1"; FAILS=0
say() { printf '%-8s %s\n' "$1" "$2"; [ "$1" = "FAIL" ] && FAILS=$((FAILS+1)) || true; }

# --- 红线主表（8 条） ---
REDLINES=("优化用户体验" "提升性能" "简单易用" "安全保障" "合理的价格" "后续优化" "根据实际情况调整" "待定")
HIT=0
for w in "${REDLINES[@]}"; do
  if grep -q "$w" "$F"; then HIT=$((HIT+1)); echo "         红线命中: $w -> $(grep -n "$w" "$F" | head -1)"; fi
done
grep -q "TBD" "$F" && { HIT=$((HIT+1)); echo "         红线命中: TBD"; } || true
[ "$HIT" -eq 0 ] && say PASS "红线主表 8 条零命中" || say FAIL "红线主表命中 $HIT 处"

# --- 空洞形容词扩展表 ---
EXTRAS=("高效" "流畅" "无缝" "极致" "大幅提升" "显著改善" "全面优化" "seamless" "robust" "user-friendly")
XHIT=0
for w in "${EXTRAS[@]}"; do
  if grep -q "$w" "$F"; then XHIT=$((XHIT+1)); echo "         扩展表命中: $w -> $(grep -n "$w" "$F" | head -1)"; fi
done
[ "$XHIT" -eq 0 ] && say PASS "空洞形容词扩展表零命中" || say FAIL "扩展表命中 $XHIT 处（引用语境可人工豁免）"

# --- 模块数 ---
MODS=$(grep -cE '^## [0-9]+\.' "$F" || true)
{ [ "$MODS" -eq 11 ] || [ "$MODS" -eq 12 ]; } && say PASS "一级模块 $MODS 个（11 或 11+1）" || say FAIL "一级模块 $MODS 个（应为 11 或 12）"

# --- 编号连续性 ---
grep -q '\*\*US1\*\*\|US1' "$F" && say PASS "US 编号存在（US1 起）" || say FAIL "未找到 US1"
grep -q 'F1' "$F" && say PASS "F 编号存在（F1 起）" || say FAIL "未找到 F1"

# --- 验收标准 checkbox ---
CB=$(grep -c '^\s*- \[ \]' "$F" || true)
[ "$CB" -ge 10 ] && say PASS "验收 checkbox $CB 处（≥10）" || say FAIL "验收 checkbox 仅 $CB 处（应 ≥10）"

# --- 字数 ---
CHARS=$(wc -m < "$F" | tr -d ' ')
{ [ "$CHARS" -ge 4000 ] && [ "$CHARS" -le 9000 ]; } && say PASS "字符数 $CHARS（正文目标 4000-6000，全文含报告放宽至 9000）" || say FAIL "字符数 $CHARS 超出范围"

# --- frontmatter 关键字段 ---
for k in title date version template ai_product; do
  awk '/^---$/{n++} n==1' "$F" | grep -q "^$k:" && say PASS "frontmatter 含 $k" || say FAIL "frontmatter 缺 $k"
done

# --- 质量门报告持久化 ---
grep -q '^## 附：质量门报告' "$F" && say PASS "文末质量门报告存在" || say FAIL "缺文末质量门报告"
grep -q '质量门' <(head -20 "$F") && say PASS "文首徽章存在" || say FAIL "缺文首徽章"

# --- 北极星唯一性（粗判：出现次数） ---
NS=$(grep -c '北极星' "$F" || true)
[ "$NS" -ge 1 ] && say PASS "北极星指标已提及（唯一性由评审判）" || say FAIL "未提及北极星指标"

echo "----------------------------------------"
if [ "$FAILS" -eq 0 ]; then echo "STRUCTURAL: ALL PASS"; else echo "STRUCTURAL: $FAILS FAIL"; exit 1; fi
