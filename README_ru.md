[日本語](README.md) | [English](README_en.md) | [한국어](README_ko.md)

# TeloPon Extensions

Пакет расширений для TeloPon. Предоставляет дополнительные функции: плагины, промпты и темы, не включённые в стандартную поставку.

📖 [Документация TeloPon](https://github.com/miyumiyu/TeloPon)

---

## Установка

Скопируйте нужные файлы в соответствующую папку TeloPon.

| Тип | Источник | Назначение |
|---|---|---|
| Плагины | `plugins/*.py` | Папка `plugins/` TeloPon |
| Промпты | `prompts/ru/*.txt` | Папка `prompts/ru/` TeloPon |
| Темы | `themes/*.css` | Папка `themes/` TeloPon |

> **Для разработчиков:** Разместите как подмодуль `ex-plugins/` в TeloPon-dev для автоматической загрузки.

---

## Список плагинов

| | Плагин | Ver | Описание | DL |
|---|---|---|---|---|
| ▶️ | [YouTube OAuth](docs/ru/YoutubeLiveOAuth.md) | 1.00 | Продвинутая интеграция с YouTube через Data API + OAuth2.<br>Чтение/запись комментариев, опросы, изменение заголовка, число зрителей.<br>👉 [Подробнее](docs/ru/YoutubeLiveOAuth.md) | [📥](https://raw.githubusercontent.com/miyumiyu/TeloPon-Extensions/main/plugins/YoutubeLiveOAuth.py) |
| 🔊 | [Windows TTS](docs/ru/WindowsTTS.md) | 1.00 | Автоматическая озвучка телопов встроенным движком SAPI5.<br>Выбор голоса, скорости, тона, громкости и устройства.<br>👉 [Подробнее](docs/ru/WindowsTTS.md) | [📥](https://raw.githubusercontent.com/miyumiyu/TeloPon-Extensions/main/plugins/WindowsTTS.py) |
| 🎮 | [VCI OSC](docs/ru/VciOscPlugin.md) | 1.01 | Отправка телопов в [VirtualCast](https://virtualcast.jp/) VCI по OSC.<br>Отображение телопов ИИ в VR-пространстве.<br>👉 [Подробнее](docs/ru/VciOscPlugin.md) | [📥](https://raw.githubusercontent.com/miyumiyu/TeloPon-Extensions/main/plugins/VciOscPlugin.py) |
| 💬 | [Discord](docs/ru/discord_integration.md) | 1.00 | Получение комментариев из каналов [Discord](https://discord.com/) в реальном времени.<br>Автоматическая генерация URL-приглашения.<br>👉 [Подробнее](docs/ru/discord_integration.md) | [📥](https://raw.githubusercontent.com/miyumiyu/TeloPon-Extensions/main/plugins/discord_integration.py) |
| 🏢 | [Slack](docs/ru/slack_integration.md) | 1.00 | Получение комментариев из [Slack](https://slack.com/) без задержки через Socket Mode.<br>Авто-конвертация ID пользователей в имена.<br>👉 [Подробнее](docs/ru/slack_integration.md) | [📥](https://raw.githubusercontent.com/miyumiyu/TeloPon-Extensions/main/plugins/slack_integration.py) |
| 🗣️ | [VOICEVOX](docs/ru/voicevox_plugin.md) | 1.00 | Озвучка телопов движком [VOICEVOX](https://voicevox.hiroshiba.jp/).<br>Множество голосов персонажей и стилей.<br>👉 [Подробнее](docs/ru/voicevox_plugin.md) | [📥](https://raw.githubusercontent.com/miyumiyu/TeloPon-Extensions/main/plugins/voicevox_plugin.py) |
| 📊 | [PowerPoint](docs/ru/PowerPointPlugin.md) | 1.00 | Управление слайд-шоу PowerPoint голосом.<br>Следующий/предыдущий слайд, переход к странице, затемнение, начало/конец презентации.<br>Автоматическая передача заголовка и заметок слайда в ИИ.<br>👉 [Подробнее](docs/ru/PowerPointPlugin.md) | [📥](https://raw.githubusercontent.com/miyumiyu/TeloPon-Extensions/main/plugins/PowerPointPlugin.py) |
| 🐦 | [X (Twitter)](docs/ru/XTwitterPlugin.md) | 1.00 | Получение твитов по хэштегу и передача ИИ.<br>ИИ автоматически публикует твиты во время трансляции. Требуются API-ключи X Developer Portal (платно).<br>👉 [Подробнее](docs/ru/XTwitterPlugin.md) | [📥](https://raw.githubusercontent.com/miyumiyu/TeloPon-Extensions/main/plugins/XTwitterPlugin.py) |

---

## Промпты

(Готовятся)

## Темы

(Готовятся)

---

## Лицензия

Подчиняется той же лицензии, что и основное приложение TeloPon.
