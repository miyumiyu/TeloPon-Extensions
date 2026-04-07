# Интеграция YouTube OAuth — Руководство по настройке Google Cloud Console

Подробное пошаговое руководство с изображениями по настройке Google Cloud Console, необходимой для использования плагина интеграции YouTube OAuth.

> Примерное время: около 10–15 минут

---

## Шаг 1: Войдите в Google Cloud Console

Перейдите на [Google Cloud Console](https://console.cloud.google.com/) и войдите с помощью аккаунта Google.  
При первом входе примите условия использования.

<img src="../images/YoutubeLiveOAuth/YoutubeLiveOAuth1.png" width="500">

Установите флажок согласия с условиями использования и нажмите «Принять и продолжить».

> ⚠️ **Если отображается следующий экран:** Двухэтапная аутентификация (MFA) аккаунта Google не настроена.  
> Нажмите «Перейти к настройкам» и включите её. После активации доступ станет возможен примерно через 60 секунд.
>
> <img src="../images/YoutubeLiveOAuth/YoutubeLiveOAuth2FAError.png" width="500">

---

## Шаг 2: Создайте новый проект

Нажмите «Выбрать проект» в верхней части экрана.

<img src="../images/YoutubeLiveOAuth/YoutubeLiveOAuth2.png" width="600">

Нажмите «Новый проект» в правом верхнем углу.

<img src="../images/YoutubeLiveOAuth/YoutubeLiveOAuth3.png" width="500">

Введите название проекта `TeloPon` (или любое другое) и нажмите «Создать».

---

## Шаг 3: Настройка экрана согласия OAuth

Сначала убедитесь, что название проекта в левом верхнем углу экрана — **TeloPon** (проект, созданный на Шаге 2).  
Если отображается другой проект, нажмите на его название и переключитесь.

<img src="../images/YoutubeLiveOAuth/YoutubeLiveOAuth10.png" width="600">

Нажмите на три горизонтальные линии (≡) в левом верхнем углу, чтобы открыть меню, и выберите «API и сервисы» → «Экран согласия OAuth».

Отобразится сообщение «Google Auth Platform ещё не настроена» — нажмите «Начать».

<img src="../images/YoutubeLiveOAuth/YoutubeLiveOAuth4.png" width="600">

### 3-1: Информация о приложении

Введите `TeloPon` в качестве названия приложения, выберите email для поддержки и нажмите «Далее».

<img src="../images/YoutubeLiveOAuth/YoutubeLiveOAuth5.png" width="500">

### 3-2: Аудитория

Выберите **«Внешний»** и нажмите «Далее».

<img src="../images/YoutubeLiveOAuth/YoutubeLiveOAuth6.png" width="400">

> «Внутренний» предназначен только для аккаунтов Google Workspace (организации, учебные заведения). Для личного аккаунта Google выберите «Внешний».

### 3-3: Контактная информация

Убедитесь, что адрес электронной почты отображается, и нажмите «Далее».

<img src="../images/YoutubeLiveOAuth/YoutubeLiveOAuth7.png" width="500">

### 3-4: Завершение

Установите флажок «Я соглашаюсь с Политикой Google API Services в отношении пользовательских данных» и нажмите «Продолжить».

<img src="../images/YoutubeLiveOAuth/YoutubeLiveOAuth8.png" width="500">

Когда все шаги будут отмечены галочками, нажмите «Создать».

<img src="../images/YoutubeLiveOAuth/YoutubeLiveOAuth9.png" width="400">

---

## Шаг 4: Включите YouTube Data API v3

Введите `YouTube Data API v3` в строке поиска в верхней части экрана.

<img src="../images/YoutubeLiveOAuth/YoutubeLiveOAuth11.png" width="600">

В результатах поиска нажмите на «YouTube Data API v3» и нажмите кнопку «Включить».

<img src="../images/YoutubeLiveOAuth/YoutubeLiveOAuth12.png" width="600">

---

## Шаг 5: Настройка областей доступа (Scopes)

Нажмите «Доступ к данным» в левом меню.

<img src="../images/YoutubeLiveOAuth/YoutubeLiveOAuth16.png" width="600">

Нажмите «Добавить или удалить области доступа», введите `youtube.force-ssl` в фильтр и выполните поиск.

<img src="../images/YoutubeLiveOAuth/YoutubeLiveOAuth17.png" width="500">

Установите флажок для `https://www.googleapis.com/auth/youtube.force-ssl` и нажмите «Обновить».

<img src="../images/YoutubeLiveOAuth/YoutubeLiveOAuth18.png" width="600">

---

## Шаг 6: Добавление тестовых пользователей

Нажмите «Аудитория» в левом меню, в разделе «Тестовые пользователи» внизу экрана нажмите «+ Add users».

<img src="../images/YoutubeLiveOAuth/YoutubeLiveOAuth19.png" width="600">

Введите **адрес электронной почты аккаунта Google, который будет использоваться для авторизации в TeloPon**, и нажмите «Сохранить».

<img src="../images/YoutubeLiveOAuth/YoutubeLiveOAuth20.png" width="500">

> **Важно:** Авторизоваться смогут только аккаунты с email, добавленными здесь.  
> Если TeloPon будут использовать другие люди, добавьте и их email (максимум 100 человек).

---

## Шаг 7: Создание OAuth Client ID

Нажмите «API и сервисы» → «Учётные данные» в левом меню.  
Нажмите кнопку «+ Создать учётные данные» вверху и выберите **«OAuth Client ID»**.

<img src="../images/YoutubeLiveOAuth/YoutubeLiveOAuth13.png" width="600">

Заполните следующие поля.

| Поле | Значение |
|---|---|
| Тип приложения | **Приложение для ПК** |
| Название | `TeloPon` (произвольное) |

<img src="../images/YoutubeLiveOAuth/YoutubeLiveOAuth14.png" width="500">

Нажмите «Создать» — отобразятся **Client ID** и **Client Secret**.  
Скопируйте оба значения.

<img src="../images/YoutubeLiveOAuth/YoutubeLiveOAuth15.png" width="400">

> ⚠️ После закрытия этого диалога Client Secret нельзя будет просмотреть повторно. Обязательно скопируйте его или скачайте JSON-файл.

---

## Шаг 8: Ввод данных в TeloPon и авторизация

Откройте экран настроек плагина в TeloPon, вставьте **Client ID** и **Client Secret** и нажмите «Авторизоваться через Google».

<img src="../images/YoutubeLiveOAuth/YoutubeLiveOAuth21.png" width="500">

Откроется браузер с экраном выбора аккаунта Google.  
Выберите аккаунт, который вы используете с TeloPon (аккаунт, добавленный в тестовые пользователи на Шаге 6).

<img src="../images/YoutubeLiveOAuth/YoutubeLiveOAuth22.png" width="600">

> Если вы подключаетесь с правами администратора другого канала, выберите управляемый Brand Account.

Отобразится сообщение «Это приложение не проверено Google», но поскольку вы сами его создали, это не проблема.  
Нажмите **«Продолжить»**.

<img src="../images/YoutubeLiveOAuth/YoutubeLiveOAuth23.png" width="600">

Появится экран подтверждения прав доступа. Нажмите «Продолжить», чтобы предоставить разрешение.

<img src="../images/YoutubeLiveOAuth/YoutubeLiveOAuth24.png" width="600">

После успешной авторизации на экране настроек TeloPon отобразятся название канала и миниатюра.

<img src="../images/YoutubeLiveOAuth/YoutubeLiveOAuth25.png" width="500">

---

## Готово!

Настройка Google Cloud Console завершена.  
Теперь для использования достаточно выбрать трансляцию и подключиться к ней на экране настроек TeloPon.

👉 [Вернуться к инструкции по плагину YouTube OAuth](YoutubeLiveOAuth.md)
