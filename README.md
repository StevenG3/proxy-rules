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
| App 内 VoIP（微信 / WhatsApp / Telegram / FaceTime） | **是，大陆用户的首要成因** | 依赖 APNs 长连接唤醒响铃。APNs 经代理转发时容易延迟或静默掉线，来电不响且不留记录。 |
| 蜂窝网络下的 VoLTE / CS 通话 | **否** | 走运营商 IMS 专用 APN，不经过隧道。若这类电话也打不进来，问题在运营商侧（呼叫转移、防骚扰拦截、漫游），与本仓库无关。 |
| Wi-Fi 通话 / VoWiFi / IMS | **仅港澳台 / 境外卡** | 通过 IKEv2 与运营商 ePDG 建链（UDP 500/4500），语音由 ESP（IP 协议号 50）承载。Shadowrocket 的 TUN 接口**只处理 TCP**，ESP 无法转发。但大陆运营商不提供该服务，见下。 |

#### 大陆卡不必考虑 VoWiFi

ePDG 的域名由 3GPP 规定为 `epdg.epc.mnc<MNC>.mcc<MCC>.pub.3gppnetwork.org`，
其中 `pub` 即 public，可从公网 DNS 查询。实测（2026-08-09）结果：

| 运营商 | ePDG |
| --- | --- |
| 中国移动 / 联通 / 电信 / 广电 | **未发布** |
| CSL、PCCW 香港 | `120.88.224.5/6`、`120.88.240.5/6` |
| SmarTone 香港 | `180.219.134.18` |
| 中国移动香港 | `182.239.86.1`、`182.239.118.1` |
| 中华电信 | `221.120.20.1`、`221.120.23.1/11` |
| 台湾大哥大 | `175.96.62.1`、`175.96.63.1` |
| au KDDI 日本 | `27.86.78.32/34/96/98` + IPv6 |

大陆四家全部未发布，与"大陆运营商不提供 Wi-Fi 通话、大陆卡的 iPhone 里
没有该开关"这一事实一致。**因此用大陆卡时 VoWiFi 不可能是成因**，无需为它
配置 `tun-excluded-routes`。

自行复核：

```bash
python3 tools/lookup-epdg.py            # 内置常见运营商
python3 tools/lookup-epdg.py 460-00 454-12   # 指定 MCC-MNC
```

⚠️ `pub.3gppnetwork.org` 配了通配记录，未发布 ePDG 的运营商会返回
`127.0.0.1` 而非 NXDOMAIN。不要把它当成真实网关地址填进规则。

#### ⚠️ 已知冲突模块：「苹果APNs推送」

```text
https://raw.githubusercontent.com/ttyyss2233/Tool/main/shadowrocket/mokuai/Apns.module
```

若模块列表中启用了这个模块，**必须关闭**——它与 `call-direct.list` 的策略
完全相反，且使用的是同一批 APNs 网段：

| 该模块 | `call-direct.list` |
| --- | --- |
| `DOMAIN-SUFFIX,push.apple.com,PROXY` | 同域名 `DIRECT` |
| `IP-CIDR,17.57.144.0/22,PROXY` | 同网段 `DIRECT` |
| `IP-CIDR,17.188.128.0/18,PROXY` | 同网段 `DIRECT` |
| `IP-CIDR,17.188.20.0/23,PROXY` | 同网段 `DIRECT` |
| `IP-CIDR6,2620:149:a44::/48,PROXY` | 同网段 `DIRECT` |

更麻烦的是它的 `#!desc` 直接指示用户「到设置，隧道，打开包含所有网络，
apns开关」。照做之后，APNs 在**系统层**被强制入隧、在**规则层**又被推去代理，
长连接两头受夹，结果就是推送延迟或静默掉线——即来电不响铃且无未接记录、
Google Voice 收不到通知。

调整模块顺序**不足以**解决：隧道开关属于 iOS 系统层，在规则匹配之前生效，
任何规则都盖不住，必须手动关闭。

此外该模块含 `DOMAIN-SUFFIX,akadns.net,PROXY`。`akadns.net` 是 Akamai 的全球
DNS 基础设施，被大量服务（含众多国内站点）使用，整体推向代理会拖慢本应直连
的流量，粒度过粗。

#### 设置 > 隧道

这一页的每个开关都直接对应一个 iOS `NEVPNProtocol` 属性，在**规则匹配之前**
由系统生效，模块和规则集都无法覆盖。

| 开关 | 对应属性 | Apple 默认 | 说明 |
| --- | --- | --- | --- |
| 强制路由 | `enforceRoutes` | `false` | 开启后隧道路由压过系统路由表**以及 App 自身的接口绑定**。 |
| 包括所有网络 | `includeAllNetworks` | `false` | 总开关。关闭时，下面三项全部失效。 |
| 包括本地网络 | `excludeLocalNetworks` 取反 | iOS 下即"开" | 关掉可修复 AirDrop、AirPlay、CarPlay、NAS、打印机、HomeKit 摄像头。 |
| 包括 APNs | `excludeAPNs` 取反 | **排除**（即"关"） | 打开等于把 Apple 推送塞进隧道，属反默认设置。 |
| 包括蜂窝服务 | `excludeCellularServices` 取反 | **排除**（即"关"） | 对应 Wi-Fi 通话、MMS、SMS、可视语音信箱。 |

**限制（Apple 文档明确列出）：**

1. 后三项**只在「包括所有网络」开启时才有意义**，单独打开无效。
2. 无论开关如何设置，系统**始终**把以下流量排除在隧道外，你控制不了：
   * DHCP 等维持本地网络连接的控制平面流量
   * Captive Portal（Wi-Fi 热点认证）流量
   * **仅使用蜂窝网络的服务，例如 VoLTE**
   * 与 Apple Watch 等配对设备的通信
3. 「包括 APNs」「包括蜂窝服务」需要 **iOS 16.4+**。

**第 2 条是关键**：VoLTE 由系统自动排除，因此**蜂窝语音来电永远不会受
Shadowrocket 影响**。如果只有一部分电话打不进来，那条分界线就在这里——
走 VoLTE 的正常，靠 APNs 唤醒的 App VoIP 来电出问题。

**推荐设置**（最小改动，保留 `includeAllNetworks` 的防泄漏语义）：

* **包括 APNs → 关**（恢复 Apple 默认，这是来电不响的直接成因）
* **强制路由 → 关**（Apple 默认即为关）
* 包括蜂窝服务 → 保持关
* 包括本地网络 → 局域网设备/AirDrop 有问题时再关

若仍不正常，再关闭「包括所有网络」总开关。代价是失去"VPN 断开即断网"的
防泄漏保证，换取系统服务恢复正常。

### 既要 Telegram / X 推送，又要能接电话

结论：**这两者不冲突，而且不需要 TUN 模式。**

关键在于 iOS 的推送机制——所有第三方 App 的远程推送都**只经由 APNs 送达**，
没有例外。Telegram / X 的推送路径是：

```text
Telegram 服务器 ──► Apple APNs ──► 你的设备（一条直连长连接）
```

代理并不参与这一段。真正需要代理的是 **App 自己到自家服务器的连接**——
用来上报 APNs device token、保持账号在线、点开通知后拉取内容。这条链路
被墙时，服务器无从推送给你，于是表现为"不挂代理就收不到推送"。

所以你需要的是"Telegram / X 的流量能走代理"，而不是"所有流量都进 TUN"。
而 Shadowrocket 手册对两种代理类型的定义是：

* **HTTP** —— 系统代理模式，对于不支持的程序**会交给 TUN 接管**网络连接
* **None** —— TUN 模式，**全部**网络请求都将通过 TUN 接口处理

也就是说 **HTTP 模式本身已经带 TUN 兜底**。Telegram 用的 MTProto 是自定义
TCP 协议、不走系统 HTTP 代理，正属于"不支持的程序"，在 HTTP 模式下同样由
TUN 接管、照常走代理，推送不受任何影响。而「None」会把本该绕开的系统服务
也一并吃进隧道，这才是来电出问题的根源。

配合本仓库的规则，三者同时成立：

| 目标 | 手段 |
| --- | --- |
| Telegram / X 走代理、推送正常 | 代理类型 = HTTP（TUN 兜底），`telegram.list` → PROXY |
| APNs 稳定、来电响铃 | `call-direct.list` 置顶 → DIRECT |
| 系统服务不被强制入隧 | 关闭「包括所有网络」 |

注意 `call-direct.list` 让 APNs 走直连**不会**影响 Telegram / X 的推送——
推送走的正是这条直连的 APNs 通道，而 Telegram 自己的 MTProto 连接仍由
`telegram.list` 送去代理，两者互不干扰。

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

0. 检查模块列表是否启用了
   [「苹果APNs推送」](#️-已知冲突模块苹果apns推送)，有则关闭。
1. **设置 > 隧道 > 包括 APNs → 关**，再让对方重拨。绝大多数情况到此为止。
2. 仍不通，**强制路由 → 关**。
3. 仍不通，导入模块让 APNs 直连（同时解决 `apple.list` 把 APNs 送去代理的问题）。
4. 仍不通，关闭「包括所有网络」总开关。
5. 只有在用港澳台 / 境外卡且确认该运营商发布了 ePDG 的前提下，才需要启用模块里的
   `tun-excluded-routes`。

每一步之间留足时间让 APNs 重新建连（切一次飞行模式可加速），并注意
**走 VoLTE 的蜂窝来电本就不受影响**，测试时应当用微信 / Telegram 等
App 内语音来电来验证。

### US-Apps（TikTok / Claude 走美国节点）

用于在不修改 `sr_top500_banlist_ad.conf` 的前提下，把 TikTok 与 Claude 定向到
美国节点。共 44 条规则。

**方式一：内联模块（推荐）**

`shadowrocket/us-apps.module` — 模块页 `新建模块`，整段粘贴后保存。规则内嵌，
导入即生效，无远程依赖。

**方式二：远程规则集**

```text
DOMAIN-SUFFIX,ads-sg.tiktok.com,REJECT
RULE-SET,https://raw.githubusercontent.com/StevenG3/proxy-rules/main/shadowrocket/us-apps.list,LA-REALITY
```

`us-apps.list` 不含策略名，故广告拦截那条必须单独写在 `RULE-SET` 之前。

#### 规则来源

| 仓库 | 采用情况 |
| --- | --- |
| blackmatrix7 `TikTok/TikTok.list` | 32 条，主干 |
| ACL4SSR `Clash/Ruleset/TikTok.list` | 子集，仅 `DOMAIN-KEYWORD,tiktokcdn` 为独有 |
| blackmatrix7 `Claude/Claude.list` | 仅 3 条 |
| ACL4SSR `Clash/Ruleset/AI.list` | 补 `claude.com`、`claudeusercontent.com` 及关键字 |
| Loyalsoldier `surge-rules` | **未发布 TikTok 规则集**（`ruleset/tiktok.txt` 与 `tiktok.txt` 均 404），未采用 |

#### 与原 conf 的冲突

全文扫描 `sr_top500_banlist_ad.conf` 后，仅一处冲突：

```text
第 1747 行  DOMAIN-SUFFIX,ads-sg.tiktok.com,Reject
```

模块规则优先于配置文件，`DOMAIN-SUFFIX,tiktok.com,LA-REALITY` 会把该广告
域名一并接管，使拦截失效。模块已在最顶部重申 `REJECT` 抢回——规则自上而下
匹配，置顶即生效。Claude / Anthropic 在原 conf 中无任何规则，零冲突。

优先级判定：模块 > 配置文件；上 > 下；域名类 > IP 类；`GEOIP` 属推断类，
排在显式规则之后；`FINAL` 恒在末尾。

#### TikTok 的 IP 一致性

1. **关闭 IPv6**：`点击配置文件的 ⓘ 图标 > 通用 > 启用IPv6 > 关闭`，
   避免 IPv4 走美国节点而 IPv6 走直连的双栈泄漏。
2. **DNS 无需额外设置**：命中代理策略的域名默认由代理服务器解析（「DNS 覆写
   仅针对直连类域名进行解析，代理类域名将经由代理服务器进行解析」），本地既
   拿不到也污染不了。规则没命中时才会泄漏，因此规则命中率才是关键。
3. **固定节点**：`LA-REALITY` 不要放进 `url-test` / `fallback` 等自动测速
   分组，会话中途更换出口 IP 极易触发美区风控。

节点名必须与首页显示完全一致，否则规则静默失效（不报错，直接落回默认策略）。
导入后在 `数据 > 请求` 中筛 `tiktok` 核对策略列。

### Google Voice

Raw URL:

```text
https://raw.githubusercontent.com/StevenG3/proxy-rules/main/shadowrocket/google-voice.list
```

```text
RULE-SET,https://raw.githubusercontent.com/StevenG3/proxy-rules/main/shadowrocket/google-voice.list,PROXY
```

**必须放在 `GEOIP,CN` 之前**，`personal-rules.module` 中已如此排列。

#### 收不到 Google Voice 通知的两层原因

GV 的通知需要两条独立的链路同时成立，缺一不可：

```text
① GV 连上 Google 服务器（注册/刷新 APNs token、维持信令）—— 必须走代理
② Google → Apple APNs → 你的设备 —— 必须直连且稳定
```

**第 ① 层：GEOIP 误判。** 若规则里没有显式的 Google 域名规则，
`voice.google.com` 会一路落到 `GEOIP,CN`。而 GEOIP 必须先把域名解析成 IP
才能判断归属地，国内 DNS 对 `google.com` 的解析结果是被污染的——判成 CN
就走 DIRECT，直接撞墙。GV 连不上服务器，Google 根本不会发出那条推送。
域名规则不依赖解析结果，是唯一可靠的解法。

**第 ② 层：APNs 被塞进隧道。** 见上文 [Incoming Call Fix](#incoming-call-fix)，
`设置 > 隧道 > 包括 APNs` 必须关闭。GV 的通知与微信、Telegram 的来电走的是
同一条 APNs 通道，同一个开关同时影响它们。

#### 其他注意事项

* **节点建议固定在美国。** GV 对账号 IP 的地理位置敏感，落地国家频繁跳变
  可能触发风控使会话失效。
* 先排除非网络因素：iOS `设置 > 通知 > Google Voice` 是否允许通知、是否被
  专注模式拦截、GV App 内 `设置 > 请勿打扰` 是否开启、以及 GV 内消息与来电的
  通知开关是否分别打开。

### 通用诊断：某个服务「主体能用、某块功能空白」

本仓库中 Google Voice、Bybit、Kraken 三次故障是同一个模式，先记在这里，
下次遇到直接照做。

**症状**：App 能登录、主要数据正常，但某一块内容始终加载不出来或转圈。

**成因**：该功能依赖的域名没有任何显式规则，落到 `GEOIP,CN` 上。GEOIP 要先
把域名本地解析成 IP 再判定归属地，而结果取决于 DNS 与 CDN 的地理调度：

* 判为海外 → `FINAL,PROXY` → 通
* 判为 CN → `DIRECT` → 撞墙

同一个 App 的不同域名落在不同 IP 段，判定结果就可能不一致——于是出现「一半
能用一半不能用」。Kraken 是最典型的例子：账户接口在 Cloudflare 的
`104.17.185.205`，行情数据源 DXfeed 在 `162.159.134.42`，同为 Cloudflare
却分属不同 anycast 段。

**关键点**：出问题的往往是**第三方服务，域名与主站完全无关**。

| 服务 | 主站 | 实际掉链子的域名 |
| --- | --- | --- |
| Kraken | `kraken.com` | `dxfeed.com`（图表数据源）|
| Bybit | `bybit.com` | `challenges.cloudflare.com`（人机验证）|
| Google Voice | `voice.google.com` | `googleapis.com`（信令与 token）|
| 哔哩哔哩 | `bilibili.com` | `bilivideo.com`、`hdslb.com`（视频流）|

**排查步骤**：

1. 看 App 界面上的署名，例如「图表数据由 DXfeed 提供」——第三方数据源
   通常会标注出来
2. `数据 > 请求` 按时间倒序，在触发该功能时观察新出现的域名
3. 对可疑域名 `nslookup` 看落在哪个 IP 段
4. 把域名按名写进规则集，置于 `GEOIP,CN` 之前

**为什么必须按域名而非依赖 GEOIP**：域名规则不需要解析即可匹配，结果确定；
GEOIP 依赖本地解析，面对地理调度 CDN 与被污染的 DNS 时不可靠。本仓库对国内
域名用 `DOMAIN-SET` 直连、对境外服务用 `RULE-SET` 代理，都是同一套推理的
两个方向。

### ⚠️ RULE-SET 与 DOMAIN-SET 不可混用

手册对两者的定义是互斥的：

| 引用方式 | 规则集格式 |
| --- | --- |
| `RULE-SET` | 组成部分**需包含**规则类型，如 `DOMAIN-SUFFIX,example.com` |
| `DOMAIN-SET` | 组成部分**不包含**规则类型，如 `.example.com` |

用错时 Shadowrocket 无法解析表内条目，整个规则集**静默失效**——不报错、不
提示，规则就像不存在一样，流量继续往下匹配。

本仓库引用的外部规则集：

| 规则集 | 格式 | 正确引用 |
| --- | --- | --- |
| `ChinaMax/ChinaMax_Domain.list` | 纯域名（111592 行，带前缀 0 行）| **`DOMAIN-SET`** |
| `BiliBili/BiliBili.list` | 含规则类型 | `RULE-SET` |
| 本仓库各 `.list` | 含规则类型 | `RULE-SET` |

误用 `DOMAIN-SET` 引用 ChinaMax 曾导致 11 万条国内域名直连规则全部失效，所有
国内站点转而落到 `GEOIP,CN` 上按本地解析结果判定。B 站是典型受害者：视频流走
`bilivideo.com` 与 `hdslb.com` 而非主站，这些 CDN 的 IP 分布广，GEOIP 判错即
绕行海外节点，表现为主站正常但播放卡顿。

新增外部规则集前，先确认格式：

```bash
curl -s <URL> | grep -vE '^\s*#|^\s*$' | grep -cE '^(DOMAIN|IP-CIDR|DST-PORT)'
```

计数为 0 即为纯域名表，必须用 `DOMAIN-SET`。

### Kraken

Raw URL:

```text
https://raw.githubusercontent.com/StevenG3/proxy-rules/main/shadowrocket/kraken.list
```

```text
RULE-SET,https://raw.githubusercontent.com/StevenG3/proxy-rules/main/shadowrocket/kraken.list,PROXY
```

**必须放在 `GEOIP,CN` 之前**，`personal-rules.module` 中已如此排列。

覆盖 Kraken 交易所、xStocks 代币化股票，以及**行情数据源 DXfeed**——图表由
DXfeed 提供，域名与 `kraken.com` 无关，是「余额正常但图表空白」的直接原因，
详见[通用诊断](#通用诊断某个服务主体能用某块功能空白)。

上游 blackmatrix7 的 `Crypto.list` 仅含 `DOMAIN-SUFFIX,kraken.com`，不含
DXfeed 与 xStocks。

### Bybit

Raw URL:

```text
https://raw.githubusercontent.com/StevenG3/proxy-rules/main/shadowrocket/bybit.list
```

```text
RULE-SET,https://raw.githubusercontent.com/StevenG3/proxy-rules/main/shadowrocket/bybit.list,PROXY
```

**必须放在 `GEOIP,CN` 之前**，`personal-rules.module` 中已如此排列。

### 部分请求"命中 PROXY 规则却没走代理"

同一现象通常有两个独立成因，两个都要处理。

#### 成因一：请求根本没命中 PROXY 规则

若某服务没有显式的域名规则，请求会一路落到 `GEOIP,CN`。GEOIP 必须先把域名
本地解析成 IP 才能判定归属地，而地理感知 CDN 会按解析来源返回就近节点——
配合国内 DNS 极易拿到被判为 CN 的地址，于是走 `DIRECT`。

实测 Bybit 的入口正是这种结构：

| 域名 | 落点 |
| --- | --- |
| `bybit.com` | CloudFront `18.160.x` |
| `www.bybit.com` | Akamai `23.33.x` |
| `api.bybit.com` | AWS `18.238.x` |

同一个机制此前已经让 Google Voice 中招，见
[Google Voice](#google-voice)。**解法是把域名规则显式写在 `GEOIP,CN` 之前**，
按名匹配不依赖解析结果——与本仓库对国内域名的处理是同一套推理。

#### 成因二：QUIC 绕过了代理

`udp-policy-not-supported-behaviour = DIRECT` 会在节点不支持 UDP 转发时把
UDP 流量回退为直连。该设置是为 VoIP 媒体流准备的，但网站的 HTTP/3 同样走
QUIC（UDP 443），于是这些请求虽然命中了 `PROXY` 规则，最终却以真实 IP 直连。

```text
block-quic = all-proxy
```

`all-proxy` 只对走代理的连接阻断 QUIC，迫使其回落到 TCP 上的 HTTP/2 正常
代理；直连连接不受干预，国内站点不受影响。已加入 `personal-rules.module`。

#### 排查方法

在 Shadowrocket 的 **数据 > 请求** 里筛选目标域名，逐条看策略列：

* 显示 `DIRECT` 且命中规则为 `GEOIP,CN` → 成因一，补域名规则
* 请求走的是 UDP/443 → 成因二，确认 `block-quic` 是否生效

#### 关于节点地区

Bybit 在韩国受监管施压，但**已确认的限制是 Google Play 的 App 安装**
（2025-03 起，2026-07 扩大至 29 家交易所），网页与 Apple App Store 访问不受
影响。iOS 上使用韩国节点目前无碍，后续若出现 IP 层限制再换区。

### Claude / Anthropic

**Anthropic 自有域名**（`anthropic.com`、`claude.ai`、`claude.com`、
`claudeusercontent.com`）由 [US-Apps](#us-appstiktok--claude-走美国节点)
独占并指向美国节点 `LA-REALITY`——Anthropic 不接受部分亚太云厂商的 IP 段。

`claude.list` 只保留**通用第三方依赖**（统计 / 客服 / CDN），以 `PROXY`
引用，走首页选中的节点即可。

> ⚠️ 两处都写 Anthropic 域名会造成**模块间策略冲突**：`personal-rules.module`
> 的 `claude.list,PROXY` 指向首页节点（日本），`us-apps.module` 指向
> `LA-REALITY`，谁生效取决于模块列表排序，结果不可预期——表现为 Claude
> 时好时坏或直接连不上。故已从 `claude.list` 中移除，切勿加回。

保留第三方域名的显式 `PROXY` 规则，是为了避免它们落到 `GEOIP,CN` 上：GEOIP
需先本地解析，结果可能被判为 CN 而走直连。

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
