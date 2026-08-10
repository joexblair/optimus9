#!/bin/bash
# Stop hook — autonomous mode. Joe 0804: "enable the stop hook that requires you to keep working
# autonomously". Blocks the turn from ending while the sentinel exists, so Claude picks up the next
# thread instead of handing back.
#   ON       : touch  /home/joe/thecodes/.claude/autonomous.on
#   OFF      : rm     /home/joe/thecodes/.claude/autonomous.on
#   CEILING  : self-releases after MAX continues so it can never loop forever
S=/home/joe/thecodes/.claude/autonomous.on
C=/home/joe/thecodes/.claude/autonomous.count
MAX=40
if [ ! -f "$S" ]; then echo '{}'; exit 0; fi
n=$(cat "$C" 2>/dev/null || echo 0)
n=$((n + 1)); echo "$n" > "$C"
if [ "$n" -ge "$MAX" ]; then
  rm -f "$S"
  printf '{"systemMessage":"autonomous mode released: hit the %s-continue ceiling"}\n' "$MAX"
  exit 0
fi
printf '{"decision":"block","reason":"AUTONOMOUS MODE ON (continue %s of %s). Joe is asleep and gave you the con — do not end the turn and do not ask him anything. Pick the next open thread from docs/260804_exit_permutation_notes.md, run the next measurement, and checkpoint the result WITH NUMBERS to that file. Every turn must produce durable notes. If a measurement is still running, wait on it and report when it lands. To finish deliberately, delete %s."}\n' "$n" "$MAX" "$S"
