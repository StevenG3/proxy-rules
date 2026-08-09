# Proxy Rules

Personal rule-set collection for proxy clients.

## Shadowrocket

### Personal Module

Raw URL:

```text
https://raw.githubusercontent.com/StevenG3/proxy-rules/main/shadowrocket/personal-rules.module
```

Use this as a Shadowrocket module to keep personal rules outside externally maintained config files such as `sr_top500_banlist_ad.conf`.

The module routes Apple services, Claude and Telegram through your proxy policy
group, sends China domains and `GEOIP,CN` to `DIRECT`, and pins call-related
traffic (IMS/VoWiFi, APNs, FaceTime) to `DIRECT` ahead of everything else — see
[Incoming Call Fix](#incoming-call-fix) below.

### Incoming Call Fix

症状：开着 Shadowrocket 时部分电话打不进来，且事后**连未接来电记录都没有**。

没有通话记录是关键线索——它说明呼叫根本没有到达设备，而不是到了没响。可能
的成因按通路分三类：

| 来电通路 | 是否受 Shadowrocket 影响 | 机制 |
| --- | --- | --- |
| 蜂窝网络下的 VoLTE / CS 通话 | **否** | 走运营商 IMS 专用 APN，不经过隧道。若这类电话也打不进来，问题在运营商侧（呼叫转移、防骚扰拦截、漫游），与本仓库无关。 |
| Wi-Fi 通话 / VoWiFi / IMS | **是，且最可能** | 通过 IKEv2 与运营商 ePDG 建链（UDP 500/4500），语音由 ESP（IP 协议号 50）承载。Shadowrocket 的 TUN 接口**只处理 TCP**，ESP 无法转发，IMS 注册直接失败，网络侧判定设备不可达。 |
| App 内 VoIP（微信 / WhatsApp / FaceTime） | **是** | 依赖 APNs 长连接唤醒响铃。APNs 经代理转发时容易延迟或静默掉线，来电不响且不留记录。 |

#### 必须手动关闭的开关

这一步优先于任何规则。以下开关会把流量在**规则匹配之前**整体捕获进隧道，
模块无法覆盖：

**设置 > 隧道 > 包括所有网络**

* **包括蜂窝服务** → **关**（这一项直接对应 VoLTE、Wi-Fi 通话、IMS、MMS、可视语音信箱）
* **包括APNs** → **关**
* **包括本地网络** → **关**

最省事的做法是直接关闭「包括所有网络」总开关。

#### 模块

Shadowrocket module URL:

```text
https://raw.githubusercontent.com/StevenG3/proxy-rules/main/shadowrocket/call-fix.sgmodule
```

已在使用 `personal-rules.module` 的话无需重复导入——该模块已在规则最前面
引用了同一份规则集。单独导入 `call-fix.sgmodule` 时，请在「配置 > 模块 >
右上角 `···` > 重新排序」中把它排到其他模块之前。

模块做了三件事：

1. 把运营商 IMS/VoWiFi（`3gppnetwork.org`、`epdg` 关键字、UDP 500/4500）、
   APNs、iMessage/FaceTime 注册与媒体端口（UDP 16384–16403）全部置顶为 `DIRECT`。
2. 设置 `udp-policy-not-supported-behaviour = DIRECT`。默认值 `REJECT` 会在节点
   不支持 UDP 转发时直接掐断 VoIP 媒体流。代价是命中代理策略的 UDP（如 QUIC）
   会以真实 IP 直连，介意者可删掉该行。
3. 预留了 `tun-excluded-routes` 与 `[Host]` 两段配置（默认注释）。若关掉隧道
   开关后 VoWiFi 仍不可用，再按模块内注释启用——ePDG 的 IP 段因运营商而异，
   需要自行填入。

规则集单独引用：

```text
RULE-SET,https://raw.githubusercontent.com/StevenG3/proxy-rules/main/shadowrocket/call-direct.list,DIRECT
```

#### 验证方法

规则和开关都是猜测性修复，先用下面的步骤确认根因，避免白改：

1. 关闭 Shadowrocket，让对方重拨同一个号码。若能打进来，才说明确实是代理的问题。
2. 若确认相关，先只关「包括所有网络」，不改规则，再测一次——这一步能区分是隧道
   捕获问题还是规则策略问题。
3. 若第 2 步已恢复，规则模块作为长期保险保留即可；若仍不通，再启用模块里的
   `tun-excluded-routes`。

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

### NOL Ticket Direct

Shadowrocket module URL:

```text
https://raw.githubusercontent.com/StevenG3/proxy-rules/main/shadowrocket/nol-ticket-direct.sgmodule
```

Import this URL from Shadowrocket's Modules screen. The module routes the
confirmed NOL ticketing and payment domains through `DIRECT`.
