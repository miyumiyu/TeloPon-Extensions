[日本語](README.md) | [English](README_en.md) | [Русский](README_ru.md)

# TeloPon Extensions

TeloPon의 확장 팩입니다. 표준 배포에 포함되지 않는 플러그인, 프롬프트, 테마 등의 옵션 기능을 제공합니다.

📖 [TeloPon 본체 문서](https://github.com/miyumiyu/TeloPon)

---

## 설치 방법

사용하고 싶은 파일을 TeloPon의 해당 폴더에 복사하세요.

| 종류 | 원본 | 대상 |
|---|---|---|
| 플러그인 | `plugins/*.py` | TeloPon의 `plugins/` 폴더 |
| 프롬프트 | `prompts/ko/*.txt` | TeloPon의 `prompts/ko/` 폴더 |
| 테마 | `themes/*.css` | TeloPon의 `themes/` 폴더 |

> **개발자용:** TeloPon-dev의 서브모듈로 `ex-plugins/`에 배치하면 자동으로 로드됩니다.

---

## 플러그인 목록

| | 플러그인 | Ver | 설명 | DL |
|---|---|---|---|---|
| ▶️ | [YouTube OAuth 연동](docs/ko/YoutubeLiveOAuth.md) | 1.00 | YouTube Data API + OAuth2를 활용한 고급 연동.<br>댓글 읽기/쓰기, 설문, 제목 변경, 시청자 수 등.<br>👉 [상세](docs/ko/YoutubeLiveOAuth.md) | [📥](https://raw.githubusercontent.com/miyumiyu/TeloPon-Extensions/main/plugins/YoutubeLiveOAuth.py) |
| 🔊 | [Windows TTS](docs/ko/WindowsTTS.md) | 1.00 | Windows 내장 SAPI5 엔진으로 텔롭 자동 읽기.<br>음성, 속도, 피치, 음량, 출력 장치 선택 가능.<br>👉 [상세](docs/ko/WindowsTTS.md) | [📥](https://raw.githubusercontent.com/miyumiyu/TeloPon-Extensions/main/plugins/WindowsTTS.py) |
| 🎮 | [VCI OSC 텔롭](docs/ko/VciOscPlugin.md) | 1.00 | [VirtualCast](https://virtualcast.jp/) VCI에 OSC로 텔롭 전송.<br>VR 공간에 AI 텔롭 표시.<br>👉 [상세](docs/ko/VciOscPlugin.md) | [📥](https://raw.githubusercontent.com/miyumiyu/TeloPon-Extensions/main/plugins/VciOscPlugin.py) |
| 💬 | [Discord 연동](docs/ko/discord_integration.md) | 1.00 | [Discord](https://discord.com/) 서버 채널에서 실시간 댓글 가져오기.<br>초대 URL 자동 생성 포함.<br>👉 [상세](docs/ko/discord_integration.md) | [📥](https://raw.githubusercontent.com/miyumiyu/TeloPon-Extensions/main/plugins/discord_integration.py) |
| 🏢 | [Slack 연동](docs/ko/slack_integration.md) | 1.00 | [Slack](https://slack.com/) 채널에서 Socket Mode로 지연 없는 실시간 댓글.<br>사용자 ID→이름 자동 변환.<br>👉 [상세](docs/ko/slack_integration.md) | [📥](https://raw.githubusercontent.com/miyumiyu/TeloPon-Extensions/main/plugins/slack_integration.py) |
| 🗣️ | [VOICEVOX 읽기](docs/ko/voicevox_plugin.md) | 1.00 | [VOICEVOX](https://voicevox.hiroshiba.jp/) 음성 합성 엔진으로 읽기.<br>다수의 캐릭터 보이스와 스타일 지원.<br>👉 [상세](docs/ko/voicevox_plugin.md) | [📥](https://raw.githubusercontent.com/miyumiyu/TeloPon-Extensions/main/plugins/voicevox_plugin.py) |

---

## 프롬프트

(준비 중)

## 테마

(준비 중)

---

## 라이선스

TeloPon 본체와 동일한 라이선스를 따릅니다.
