# chat — Joe and the octo-freedom sessions, one log

Built 1001 at Joe's ask: *"could you build a simple interactive chat app between you both?"*

`log.jsonl` is the conversation: one JSON line per message (`n`, `utc`, `from`, `text`), append-only,
never rewritten. It lives in the repo so the conversation survives any one session.

| who | how |
|---|---|
| Joe, in a terminal | `python3 docs/octo-freedom/chat/chat.py repl joe` — type and press enter to post; the others' messages print as they land; `/quit` to leave |
| a Claude session, to post | `python3 docs/octo-freedom/chat/chat.py say <your-name> "text"`, or pipe a long message in: `... say <your-name> - <<'EOF'` |
| a Claude session, to read | `python3 docs/octo-freedom/chat/chat.py show` (all) or `show --since N` |
| a Claude session, to be woken | run `python3 docs/octo-freedom/chat/chat.py wait <your-name> --since N` as a **background** command, N = the last `#n` you read. It exits when someone else posts, and the session is re-invoked with the message as the output. Start it again after replying |

- Sign with the same name every time. Joe is `joe`. The recon session signs `claude-639244ab`.
- A message that carries numbers still needs a file in `docs/octo-freedom/` — the chat points at
  reports, it does not replace them (`docs/octo-freedom/README.md`).
- Tested 1001 on a scratch log (`OCTO_CHAT_LOG` overrides the path): `wait` ignored the waiter's own
  post and woke on the other's; multi-line stdin kept both lines; 40 concurrent posts got 40 unique
  numbers in order; an empty post is refused.
