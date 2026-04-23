# AI Harness Node Pairing 使用指南

## 概述

Node Pairing 提供設備配對和安全驗證功能。

## 配對流程

```
1. 設備請求配對
   ↓
2. Gateway 產生 6 位數配對碼
   ↓
3. 使用者在 Gateway 確認配對碼
   ↓
4. 配對成功，產生設備令牌
   ↓
5. 設備使用令牌連線
```

## 使用方式

```python
from src.core.node import NodePairing, DeviceType

# 初始化
pairing = NodePairing(Path("data/nodes"))

# ===== 設備端 =====
# 請求配對
request = pairing.initiate_pairing(
    device_type=DeviceType.ANDROID,
    device_name="My Phone",
    device_info={"model": "Pixel 7"}
)
print(f"配對碼: {request['pairing_code']}")

# ===== Gateway 端 =====
# 確認配對
result = pairing.confirm_pairing(
    request_id=request['request_id'],
    pairing_code=request['pairing_code']
)
print(f"設備令牌: {result['device_token']}")

# ===== 設備端 =====
# 使用令牌連線
device = pairing.verify_token(result['device_token'])
if device:
    print(f"已連線到: {device.device_name}")
```

## 安全性

- 配對碼 6 位數，5 分鐘有效期
- 設備令牌使用 SHA-256 hash 儲存
- 預設配對有效期 365 天
- 可隨時撤銷配對

---

*最後更新：2026-04-23*
