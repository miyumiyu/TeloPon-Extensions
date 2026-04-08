# 🐦 X (Twitter) 연동 플러그인 (XTwitterPlugin.py)

📥 **[XTwitterPlugin.py 다운로드](https://raw.githubusercontent.com/miyumiyu/TeloPon-Extensions/main/plugins/XTwitterPlugin.py)**

해시태그로 트윗을 정기 수집하여 AI에 주입하고, AI가 텍스트·썸네일·게임 화면 캡처를 포함한 트윗을 자동 게시합니다.

> **주의:** 유료 X (Twitter) API를 사용합니다. X Developer Portal 등록과 Pay Per Use 과금이 필요합니다.

---

## 🌟 주요 기능

| 기능 | 설명 |
|---|---|
| 해시태그 검색 | 지정 해시태그 트윗을 정기 폴링으로 AI에 주입 |
| 텍스트 게시 | 해시태그·방송 URL 자동 부여하여 트윗 |
| 썸네일 게시 | 방송 썸네일 이미지 첨부 트윗 |
| 화면 캡처 게시 | OBS 캡처 이미지 첨부 트윗 |

---

## ⚙️ 필요 환경

- X Developer Portal 앱 (Pay Per Use 패키지에 추가 필요)
- 라이브러리: `pip install tweepy`

---

## 📋 설정 방법

1. X Developer Portal에서 앱 생성 → **Read and Write** 권한 → **Pay Per Use** 패키지에 추가
2. 4개 키 발급 + 크레딧 충전
3. TeloPon 설정 화면에서 키 입력 → "연결 테스트"
4. 해시태그·투고 설정·OBS 캡처 설정

---

## 🎤 음성 명령

| 음성 예시 | 동작 |
|---|---|
| "트윗해" / "X에 게시해" | 텍스트 트윗 |
| "썸네일 붙여서 트윗해" | 썸네일 이미지 첨부 트윗 |
| "게임 화면 붙여서 트윗해" | OBS 캡처 첨부 트윗 |

---

## ⚠️ 주의사항

- **유료 API:** 무료 등급 폐지. Pay Per Use 과금 필요.
- **Pay Per Use 패키지:** 추가하지 않으면 403 오류.
- **크레딧 잔액:** 없으면 402 오류.
- **트윗 글자 수:** URL·해시태그 자동 부여를 고려해 본문 100자 이내 권장.

---

[⬅️ 확장 플러그인 목록으로 돌아가기](../../README_ko.md)
