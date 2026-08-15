#!/usr/bin/env python3
"""查询运营商 ePDG（VoWiFi / Wi-Fi 通话接入网关）的公网地址。

用法:
    python3 tools/lookup-epdg.py              # 查询内置的常见运营商
    python3 tools/lookup-epdg.py 460-00 454-12  # 查询指定的 MCC-MNC

背景:
    ePDG 的域名格式由 3GPP 规定为
        epdg.epc.mnc<MNC>.mcc<MCC>.pub.3gppnetwork.org
    其中 pub 意为 public —— 该区确实可以从公网 DNS 解析。

    注意 pub.3gppnetwork.org 配置了通配记录：未发布 ePDG 的运营商会返回
    127.0.0.1 / ::1 而不是 NXDOMAIN。本脚本会把这类结果标记为「未发布」，
    不要把 127.0.0.1 当成真实网关地址填进规则里。
"""

import socket
import sys

# MCC-MNC -> 运营商名称
CARRIERS = [
    ("460-00", "中国移动"),
    ("460-01", "中国联通"),
    ("460-03", "中国电信"),
    ("460-11", "中国电信"),
    ("460-15", "中国广电"),
    ("454-00", "CSL/PCCW 香港"),
    ("454-06", "SmarTone 香港"),
    ("454-12", "中国移动香港"),
    ("454-16", "csl 香港"),
    ("466-92", "中华电信"),
    ("466-97", "台湾大哥大"),
    ("440-51", "au KDDI 日本"),
    ("310-260", "T-Mobile US"),
    ("310-410", "AT&T US"),
]

WILDCARD = {"127.0.0.1", "::1"}


def resolve(mcc: str, mnc: str) -> tuple[list[str], list[str]]:
    host = f"epdg.epc.mnc{mnc.zfill(3)}.mcc{mcc}.pub.3gppnetwork.org"
    out = []
    for family in (socket.AF_INET, socket.AF_INET6):
        try:
            out.append(sorted({r[4][0] for r in socket.getaddrinfo(host, None, family)}))
        except socket.gaierror:
            out.append([])
    return out[0], out[1]


def main() -> None:
    codes = sys.argv[1:]
    targets = (
        [(c, "") for c in codes] if codes else CARRIERS
    )

    for code, name in targets:
        mcc, _, mnc = code.partition("-")
        if not mnc:
            print(f"{code}: 格式应为 MCC-MNC，例如 460-00")
            continue

        v4, v6 = resolve(mcc, mnc)
        found = [ip for ip in v4 + v6 if ip not in WILDCARD]

        if not found:
            status = "未发布 ePDG（该运营商不提供 VoWiFi，或未公开地址）"
        else:
            status = " ".join(found)

        print(f"{code:9s} {name:14s} {status}")


if __name__ == "__main__":
    main()
