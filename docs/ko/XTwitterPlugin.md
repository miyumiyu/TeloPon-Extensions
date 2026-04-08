# 🐦 X (Twitter) 연동 플러그인 (XTwitterPlugin.py)

📥 **[XTwitterPlugin.py 다운로드](https://raw.githubusercontent.com/miyumiyu/TeloPon-Extensions/main/plugins/XTwitterPlugin.py)**

해시태그로 트윗을 정기 수집하여 AI에 주입하고, AI가 방송 중 자동으로 트윗을 게시할 수 있는 플러그인입니다.

> **주의:** 이 플러그인은 유료 X (Twitter) API를 사용합니다. X Developer Portal 등록과 API 과금이 필요합니다.

---

## 🌟 주요 기능

| 기능 | 설명 |
|---|---|
| 해시태그 검색 | 지정 해시태그의 트윗을 정기 폴링으로 가져와 AI에 주입 |
| 트윗 게시 | AI가 스트리머 지시에 따라 자동 트윗 (해시태그 자동 부여) |

---

## ⚙️ 필요 환경

- X (Twitter) Developer Portal 앱 (읽기+쓰기 권한)
- 필요 라이브러리: `pip install tweepy`

---

## 📋 설정 방법

1. X Developer Portal에서 앱 생성 후 4개 키 발급
2. TeloPon 설정 화면에서 키 입력 → "연결 테스트"
3. 검색 해시태그와 폴링 간격 설정
4. 트윗 게시 옵션과 기본 해시태그 설정

---

## ⚠️ 주의사항

- **유료 API:** X API는 무료 등급이 폐지되었습니다. 종량 과금 필요.
- **폴링 간격:** 짧을수록 비용 증가. 60초 이상 권장.

---

[⬅️ 확장 플러그인 목록으로 돌아가기](../../README_ko.md)
