# 💬 Slack (slack_integration.py)

이 플러그인을 사용하면, 회사의 Slack 워크스페이스나 팀 채널에 게시된 댓글을 TeloPon의 AI가 지연 없이 읽어줍니다!
최신 「Socket Mode」 기술을 사용하기 때문에, 놀라울 정도로 실시간으로 반응합니다.

설정은 크게 **「① 플러그인 설치」**, **「② Slack 측에서 Bot 생성 (2개의 키 취득)」**, **「③ TeloPon 화면에서 설정」**의 3단계입니다. 절차가 다소 많지만, 순서대로 진행하면 확실하게 설정할 수 있습니다!

---

## 📥 Step 1: 플러그인 설치 및 준비

📥 **[slack_integration.py 다운로드](https://raw.githubusercontent.com/miyumiyu/TeloPon-Extensions/main/plugins/slack_integration.py)**

1. 위 링크에서 파일을 다운로드합니다.
2. TeloPon 본체 폴더 안에 있는 **`plugins`** 폴더에 다운로드한 파일을 넣습니다.
3. TeloPon을 실행하고, 메인 화면의 「🔌 확장 기능」에 **「🏢 Slack 댓글 연동」**이 추가되어 있으면 성공입니다!

---

## 🛠️ Step 2: Slack Bot을 생성하고 「2개의 토큰」을 취득하기

AI가 Slack의 댓글을 읽으려면, 전용 「Bot(앱)」을 생성합니다. 여기서는 **2종류의 토큰(키)**을 취득합니다.

### 1. 앱 생성 및 이름 설정
1. PC 브라우저에서 [Slack API (Your Apps)](https://api.slack.com/apps)에 접속하고, 오른쪽 상단의 **「Create New App」**을 누릅니다.
2. **「From scratch」**를 선택하고, 원하는 이름 (예: `TeloPon 연동 Bot`)과 설치할 워크스페이스를 선택한 후 **「Create App」**을 누릅니다.
3. **[중요]** 왼쪽 메뉴의 **「App Home」**을 열고, 아래에 있는 **「Your App's Presence in Slack」**의 「Edit」 버튼을 눌러 `Display Name` (표시명)과 `Default Username` (내부 ID, 소문자 영숫자만)을 설정하고 저장합니다. 이것을 하지 않으면 Bot을 초대할 수 없습니다!

### 2. Socket Mode를 ON으로 설정하고 「App-Level 토큰」 받기!
1. 왼쪽 메뉴에서 **「Socket Mode」**를 엽니다.
2. **「Enable Socket Mode」** 스위치를 **ON(녹색)**으로 설정합니다.
3. 토큰 이름을 물어보면 적절히 입력 (`telopon-socket` 등)하고 「Generate」를 누릅니다.
4. **`xapp-`**로 시작하는 문자열이 표시됩니다. 이것이 **[App-Level 토큰]**입니다. 복사하여 메모해 둡니다.

### 3. 메시지를 읽는 권한(Scopes) 부여하기
1. 왼쪽 메뉴에서 **「OAuth & Permissions」**를 엽니다.
2. 아래로 스크롤하여, **「Scopes」** 내의 **「Bot Token Scopes」**에서 「Add an OAuth Scope」를 누르고, 다음 5개를 추가합니다.
   * `channels:history` / `groups:history` / `channels:read` / `groups:read` / `users:read`

### 4. 실시간 수신 설정 (Event Subscriptions)
1. 왼쪽 메뉴에서 **「Event Subscriptions」**를 엽니다.
2. 맨 위의 **「Enable Events」**를 **ON(녹색)**으로 설정합니다.
3. 바로 아래의 **「Subscribe to bot events」**를 열고, 「Add Bot User Event」에서 다음 2개를 추가한 후, 오른쪽 하단의 **「Save Changes」**를 누릅니다.
   * `message.channels` / `message.groups`

### 5. 워크스페이스에 설치하고 「Bot 토큰」 받기!
1. 왼쪽 메뉴에서 **「Install App」**을 열고, **「Install to Workspace」**를 누릅니다. (※권한을 변경한 경우 「Reinstall」로 표시됩니다)
2. 허가 화면이 나오면 「허용 (Allow)」을 누릅니다.
3. **`xoxb-`**로 시작하는 문자열이 표시됩니다. 이것이 **[Bot 토큰]**입니다. 복사하여 메모해 둡니다.

### 6. [매우 중요] Slack 채널에 Bot을 「초대」하기
Slack을 열고, **모니터링할 채널 (#general 등)의 입력란에서 `@TeloPon 연동 Bot`과 같이 Bot에게 멘션(@)을 전송**합니다. 「채널에 추가하시겠습니까?」라고 물어보면 반드시 추가해 주세요. 이것을 잊으면 댓글을 읽을 수 없습니다!

---

## 🖥️ Step 3: TeloPon UI에서 설정 및 연결

TeloPon 화면으로 돌아가서, 「🏢 Slack 댓글 연동」의 설정(⚙️) 패널을 엽니다.

![Slack 연동 설정 화면](../images/discord_integration.png)

1. **토큰 입력**
   * 「App-Level 토큰」 란에 Step 2에서 취득한 **`xapp-`**로 시작하는 문자를 붙여넣습니다.
   * 「Bot 토큰」 란에 Step 2에서 취득한 **`xoxb-`**로 시작하는 문자를 붙여넣습니다.
2. **채널 목록 가져오기**
   * **「🔄 토큰 확인 & 채널 목록 가져오기」** 버튼을 누릅니다.
   * 성공하면, Slack에 있는 채널이 목록으로 가져와집니다.
3. **모니터링할 채널 선택**
   * 드롭다운에서 모니터링할 채널을 선택합니다. (공개 채널은 💬, 비공개는 🔒 아이콘이 표시됩니다)
4. **연결!**
   * 마지막으로 파란색 **「연결」** 버튼을 눌러, 상태가 녹색의 「⚡ 상태: 연결 중 (Socket Mode 가동 중)」으로 바뀌면 준비 완료입니다!

---

## 💡 사용법 및 팁

설정이 완료되면, TeloPon의 메인 화면에서 「라이브 방송에 연결(AI 시작)」을 누르기만 하면 됩니다! 지정한 Slack 채널의 발언에 AI가 빠르게 반응해 줍니다.

* **이름 자동 변환**: Slack 고유의 사용자 ID (U1234... 등)는 TeloPon 내부에서 자동으로 「발언자의 표시명 (홍길동 등)」으로 변환되어 AI에게 전달됩니다. AI가 이름을 불러 답해 줍니다!
* **프롬프트 커스터마이징**: 설정 화면 하단에 있는 지시 텍스트를 「팀 멤버의 채팅입니다! 밝게 격려해 주세요!」 등으로 변경하면, AI의 캐릭터성을 더욱 끌어낼 수 있습니다.
