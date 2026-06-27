# Proxy Rules

Personal rule-set collection for proxy clients.

## Shadowrocket

### Personal Module

Raw URL:

```text
https://raw.githubusercontent.com/StevenG3/proxy-rules/main/shadowrocket/personal-rules.module
```

Use this as a Shadowrocket module to keep personal rules outside externally maintained config files such as `sr_top500_banlist_ad.conf`.

The module includes Apple services as `DIRECT` by default, plus selected services that should use your proxy policy group.

### Claude / Anthropic

Raw URL:

```text
https://raw.githubusercontent.com/StevenG3/proxy-rules/main/shadowrocket/claude.list
```

Shadowrocket rule:

```text
RULE-SET,https://raw.githubusercontent.com/StevenG3/proxy-rules/main/shadowrocket/claude.list,PROXY
```

Replace `PROXY` with the policy or proxy group name used in your Shadowrocket configuration.

### Telegram

Raw URL:

```text
https://raw.githubusercontent.com/StevenG3/proxy-rules/main/shadowrocket/telegram.list
```

Shadowrocket rule:

```text
RULE-SET,https://raw.githubusercontent.com/StevenG3/proxy-rules/main/shadowrocket/telegram.list,PROXY
```

Replace `PROXY` with the policy or proxy group name used in your Shadowrocket configuration.
