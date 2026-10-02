"""win_events — the Windows host's network-relevant event logs, copied into WSL every minute. Reads only.

Joe 1002: *"bake all of your ideas and get them collecting inputs"* - item #8 of the outage list - and
*"did you review the TCPIP windows log?"*. WSL's traffic leaves through the Windows host (NAT on the
`WSL (Hyper-V firewall)` switch), so a Windows network event is part of the collector's path.

ONE JOB: copy new events from the logs below into `windows_events.log`, one JSON line each (utc, log,
provider, id, level, message's first line). It reads with PowerShell through WSL interop, remembers the
last RecordId per log, and changes nothing on Windows.

    System                                              every provider (Tcpip, NDIS, DHCP, power, services)
    Microsoft-Windows-Hyper-V-VmSwitch-Operational      the WSL switch. Id 285 fires ~53 times an hour
                                                        as a baseline (measured 10-01/10-02); copied anyway
    Microsoft-Windows-NCSI/Operational                  Windows' internet-connectivity checks
    Microsoft-Windows-NetworkProfile/Operational        network connect / disconnect
    Microsoft-Windows-Dhcp-Client/Admin                 DHCP lease events
    Microsoft-Windows-Windows Firewall With Advanced Security/Firewall
    Microsoft-Windows-TCPIP/Operational                 DISABLED on this host at 1002; copied once enabled

ALARMS (one errors-log line each, which the /rc alert feed follows): every System event from provider
`Tcpip` (4227 / 4231 / 4266 are port exhaustion: 263 of them since 2025-11-28, 9 since kline_audit began).

    python3 -m optimus9.live.win_events
"""
import json
import os
import subprocess
import sys
import time

PS = '/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe'
OUT = os.environ.get('O9_WIN_EVENTS_LOG', '/home/joe/thecodes/windows_events.log')
STATE = OUT + '.state'
EVERY_S = 60.0
LOGS = ['System', 'Microsoft-Windows-Hyper-V-VmSwitch-Operational', 'Microsoft-Windows-NCSI/Operational',
        'Microsoft-Windows-NetworkProfile/Operational', 'Microsoft-Windows-Dhcp-Client/Admin',
        'Microsoft-Windows-Windows Firewall With Advanced Security/Firewall', 'Microsoft-Windows-TCPIP/Operational']
_SCRIPT = r"""
$ErrorActionPreference = 'SilentlyContinue'
$state = ConvertFrom-Json '%s'
$out = @()
foreach ($ln in %s) {
  $last = 0; if ($state.PSObject.Properties.Name -contains $ln) { $last = [int64]$state.$ln }
  if ($last -eq 0) {
    $ev = Get-WinEvent -LogName $ln -MaxEvents 1
  } else {
    $ev = Get-WinEvent -FilterXPath ("*[System[EventRecordID>" + $last + "]]") -LogName $ln -MaxEvents 5000
  }
  foreach ($e in $ev) {
    $m = ''; if ($e.Message) { $m = ($e.Message -split "`n")[0].Trim() }
    $out += [pscustomobject]@{ log=$ln; rid=$e.RecordId; utc=$e.TimeCreated.ToUniversalTime().ToString('yyyy-MM-dd HH:mm:ss');
                              provider=$e.ProviderName; id=$e.Id; level=$e.LevelDisplayName; msg=$m; first=($last -eq 0) }
  }
}
ConvertTo-Json -InputObject @($out) -Compress -Depth 3
"""


def _load_state():
    try:
        with open(STATE) as fh:
            return json.load(fh)
    except (OSError, ValueError):
        return {}


def poll(state):
    """-> list of new events (oldest first per log); updates `state` with each log's newest RecordId."""
    logs = '@(' + ','.join("'%s'" % x for x in LOGS) + ')'
    script = _SCRIPT % (json.dumps(state).replace("'", "''"), logs)
    p = subprocess.run([PS, '-NoProfile', '-NonInteractive', '-Command', script], capture_output=True,
                       text=True, timeout=120)
    txt = p.stdout.strip()
    rows = json.loads(txt) if txt else []
    if isinstance(rows, dict):
        rows = [rows]
    new = []
    for r in sorted(rows, key=lambda x: (x['log'], x['rid'])):
        state[r['log']] = max(int(state.get(r['log'], 0)), int(r['rid']))
        if not r.get('first'):                       # the first poll only sets the starting RecordId
            new.append(r)
    return new


def main():
    from optimus9.live.feed_errors import write
    state = _load_state()
    print('win_events: %d logs every %.0f s -> %s' % (len(LOGS), EVERY_S, OUT), flush=True)
    while True:
        try:
            new = poll(state)
            with open(OUT, 'a') as fh:
                for r in new:
                    fh.write(json.dumps({k: r[k] for k in ('utc', 'log', 'provider', 'id', 'level', 'msg', 'rid')})
                             + '\n')
            with open(STATE, 'w') as fh:
                json.dump(state, fh)
            for r in new:
                if r['log'] == 'System' and r['provider'] == 'Tcpip':
                    write('windows', 'Tcpip %s' % r['id'], '%s UTC %s' % (r['utc'], r['msg']))
        except Exception as e:                                   # a failed poll is a line, not a dead loop
            write('win_events', 'poll failed', '%s: %s' % (type(e).__name__, str(e)[:300]))
        time.sleep(EVERY_S)


if __name__ == '__main__':
    sys.exit(main())
