# 🎮 VCI 텔롭 전송 (VciOscPlugin.py)

📥 **[VciOscPlugin.py 다운로드](https://raw.githubusercontent.com/miyumiyu/TeloPon-Extensions/main/plugins/VciOscPlugin.py)**

이 플러그인은 AI가 출력한 자막을 **OSC(OpenSound Control)** 프로토콜을 통해 **VirtualCast의 VCI**에 실시간 전송합니다.
VirtualCast의 가상 공간 내에 자막을 표시할 수 있습니다.

---

## 🛠️ 준비

### 필요한 것

1. **VirtualCast** (PC판)가 설치 및 실행 완료
2. VirtualCast 설정에서 **OSC 수신 기능**이 활성화 (포트: 19100)
3. 자막 표시용 **VCI**가 VirtualCast에 배치되어 있을 것

### VirtualCast 측 OSC 설정

1. VirtualCast 타이틀 화면 → **「VCI」** 설정을 엽니다
2. **「OSC 수신 기능」**을 **「활성화」** 또는 **「크리에이터만」**으로 설정
3. 수신 포트가 **19100** (기본값)으로 되어 있는지 확인

### VCI 측 수신 스크립트 (Lua)

자막 표시용 VCI에 다음과 같은 Lua 스크립트를 설정합니다:

```lua
-- TeloPon에서 자막을 수신하여 표시
vci.osc.RegisterMethod("/telopon/telop/text", function(sender, name, args)
    local text = args[1]
    vci.assets.SetText("TextBoard", text)
end, {ExportOscType.String})

-- 배지(감정 태그)를 수신하는 경우
vci.osc.RegisterMethod("/telopon/telop/text/badge", function(sender, name, args)
    local badge = args[1]
    -- 배지에 따른 연출 등
end, {ExportOscType.String})

-- 윈도우 종류를 수신하는 경우
vci.osc.RegisterMethod("/telopon/telop/text/window", function(sender, name, args)
    local window = args[1]
    -- 윈도우 종류에 따른 표시 전환 등
end, {ExportOscType.String})
```

> ⚠️ OSC 주소는 기본값 `/telopon/telop/text`입니다. TeloPon 측 설정과 일치시켜 주세요.

---

## ⚙️ TeloPon 측 설정 및 사용법

### 1. 조작 패널 열기

TeloPon의 메인 화면 오른쪽, 「확장 기능(플러그인)」 패널에 있는 **「VCI OSC 자막」**의 **「조작 패널」** 버튼을 클릭합니다.

<img width="400" alt="VCI OSC 자막 설정 화면" src="../images/VciOscPlugin.png" />

### 2. OSC 전송 ON

**「OSC 전송 ON」** 체크박스를 켜면, 자막이 나올 때마다 자동으로 VCI에 OSC 메시지가 전송됩니다.

### 3. 연결 설정

| 설정 | 기본값 | 설명 |
|---|---|---|
| **전송 대상 IP** | `127.0.0.1` | VirtualCast가 동작 중인 PC의 IP 주소 (같은 PC라면 그대로) |
| **전송 대상 포트** | `19100` | VirtualCast의 OSC 수신 포트 |
| **OSC 주소** | `/telopon/telop/text` | VCI 측의 `RegisterMethod`와 일치시킴 |

### 4. 테스트 전송

**「테스트 전송」** 버튼을 누르면 테스트 메시지가 전송됩니다. VCI 측에서 텍스트가 표시되면 연결 성공입니다.

### 5. 전송 내용 설정

| 설정 | 기본값 | 설명 |
|---|---|---|
| **📌 TOPIC도 전송** | ON | ON인 경우 「TOPIC \| MAIN」 형식으로 전송. OFF이면 MAIN만 |
| **🏷️ 배지도 전송** | OFF | ON인 경우, 배지(감정 태그)를 `/address/badge`로 별도 전송 |

### 6. 닫기

**「닫기」** 버튼 또는 **×** 버튼으로 설정 패널을 닫습니다. 설정은 자동으로 `plugins/vci_osc.json`에 저장됩니다.

---

## 📡 전송되는 OSC 메시지

| OSC 주소 | 데이터 타입 | 내용 | 예 |
|---|---|---|---|
| `/telopon/telop/text` | String | 자막 본문 (TOPIC 포함 가능) | `방송 시작 \| 테로뽕 님이 오셨다!` |
| `/telopon/telop/text/badge` | String | 배지명 (옵션) | `놀람` |
| `/telopon/telop/text/window` | String | 윈도우 종류 (항상 전송) | `window-simple` |

> 💡 자막 본문의 HTML 태그(`<b1>`, `<b2>`, 마작패 태그 등)는 자동으로 제거되어 플레인 텍스트로 전송됩니다.

---

## ❓ 문제 해결

### Q. 테스트 전송에서 「❌ 전송 실패」가 나옴
- 전송 대상 IP와 포트가 올바른지 확인해 주세요
- 방화벽이 UDP 포트 19100을 차단하고 있지 않은지 확인해 주세요

### Q. VCI 측에서 텍스트가 표시되지 않음
- VirtualCast의 OSC 수신 기능이 활성화되어 있는지 확인해 주세요
- VCI의 Lua 스크립트의 OSC 주소가 TeloPon 측과 일치하는지 확인해 주세요
- VCI가 VirtualCast에 배치되어 있는지 확인해 주세요

### Q. 다른 PC의 VirtualCast로 전송하고 싶음
- 전송 대상 IP를 VirtualCast가 동작 중인 PC의 IP 주소로 변경해 주세요
- 수신 측 PC의 방화벽에서 포트 19100 (UDP)을 허용해 주세요

---

## 📋 기술 사양

| 항목 | 값 |
|---|---|
| 프로토콜 | OSC over UDP |
| 라이브러리 | python-osc (pythonosc) |
| 메시지 크기 상한 | 약 4000바이트 (VCI 측 제한) |
| 지원 | VirtualCast PC판 전용 |

---
