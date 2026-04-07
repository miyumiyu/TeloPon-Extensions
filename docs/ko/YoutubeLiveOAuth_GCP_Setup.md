# YouTube OAuth 연동 - Google Cloud Console 설정 가이드

YouTube OAuth 연동 플러그인을 사용하기 위해 필요한 Google Cloud Console 설정 절차를 이미지와 함께 자세히 설명합니다.

> 소요 시간: 약 10~15분

---

## Step 1: Google Cloud Console에 로그인

[Google Cloud Console](https://console.cloud.google.com/)에 접속하여 Google 계정으로 로그인합니다.  
처음인 경우 이용약관에 동의합니다.

<img src="../images/YoutubeLiveOAuth/YoutubeLiveOAuth1.png" width="500">

이용약관에 체크를 넣고 「동의 후 계속」을 클릭합니다.

> ⚠️ **아래 화면이 표시되는 경우:** Google 계정의 2단계 인증(MFA)이 설정되지 않았습니다.  
> 「설정으로 이동」에서 활성화해 주세요. 활성화 후 약 60초 정도 지나면 접속할 수 있습니다.
>
> <img src="../images/YoutubeLiveOAuth/YoutubeLiveOAuth2FAError.png" width="500">

---

## Step 2: 새 프로젝트 생성

화면 상단의 「프로젝트 선택」을 클릭합니다.

<img src="../images/YoutubeLiveOAuth/YoutubeLiveOAuth2.png" width="600">

오른쪽 상단의 「새 프로젝트」를 클릭합니다.

<img src="../images/YoutubeLiveOAuth/YoutubeLiveOAuth3.png" width="500">

프로젝트 이름에 `TeloPon` (임의의 이름)을 입력하고 「만들기」를 클릭합니다.

---

## Step 3: OAuth 동의 화면 설정

먼저, 화면 왼쪽 상단의 프로젝트 이름이 **TeloPon** (Step 2에서 생성한 프로젝트)으로 되어 있는지 확인해 주세요.  
다른 경우 프로젝트 이름을 클릭하여 전환해 주세요.

<img src="../images/YoutubeLiveOAuth/YoutubeLiveOAuth10.png" width="600">

왼쪽 상단의 삼선 아이콘(≡)을 클릭하여 메뉴를 열고, 「API 및 서비스」→「OAuth 동의 화면」을 선택합니다.

「Google Auth Platform이 아직 구성되지 않았습니다」라고 표시되면 「시작」을 클릭합니다.

<img src="../images/YoutubeLiveOAuth/YoutubeLiveOAuth4.png" width="600">

### 3-1: 앱 정보

앱 이름에 `TeloPon`을 입력하고, 지원용 이메일 주소를 선택한 후 「다음」을 클릭합니다.

<img src="../images/YoutubeLiveOAuth/YoutubeLiveOAuth5.png" width="500">

### 3-2: 대상

**「외부」**를 선택하고 「다음」을 클릭합니다.

<img src="../images/YoutubeLiveOAuth/YoutubeLiveOAuth6.png" width="400">

> 「내부」는 Google Workspace(기업/학교) 계정 전용입니다. 개인 Google 계정에서는 「외부」를 선택해 주세요.

### 3-3: 연락처 정보

이메일 주소가 표시되어 있는지 확인하고 「다음」을 클릭합니다.

<img src="../images/YoutubeLiveOAuth/YoutubeLiveOAuth7.png" width="500">

### 3-4: 완료

「Google API 서비스: 사용자 데이터에 관한 정책에 동의합니다」에 체크를 넣고 「계속」을 클릭합니다.

<img src="../images/YoutubeLiveOAuth/YoutubeLiveOAuth8.png" width="500">

모든 단계에 체크 표시가 되면 「만들기」를 클릭합니다.

<img src="../images/YoutubeLiveOAuth/YoutubeLiveOAuth9.png" width="400">

---

## Step 4: YouTube Data API v3 활성화

화면 상단의 검색창에서 `YouTube Data API v3`를 검색합니다.

<img src="../images/YoutubeLiveOAuth/YoutubeLiveOAuth11.png" width="600">

검색 결과에서 「YouTube Data API v3」를 클릭하고, 「사용」 버튼을 누릅니다.

<img src="../images/YoutubeLiveOAuth/YoutubeLiveOAuth12.png" width="600">

---

## Step 5: 범위(Scope) 설정

왼쪽 메뉴의 「데이터 액세스」를 클릭합니다.

<img src="../images/YoutubeLiveOAuth/YoutubeLiveOAuth16.png" width="600">

「범위 추가 또는 삭제」를 클릭하고, 필터에 `youtube.force-ssl`을 입력하여 검색합니다.

<img src="../images/YoutubeLiveOAuth/YoutubeLiveOAuth17.png" width="500">

`https://www.googleapis.com/auth/youtube.force-ssl`에 체크를 넣고 「업데이트」를 클릭합니다.

<img src="../images/YoutubeLiveOAuth/YoutubeLiveOAuth18.png" width="600">

---

## Step 6: 테스트 사용자 추가

왼쪽 메뉴의 「대상」을 클릭하고, 화면 하단의 「테스트 사용자」 섹션에서 「+ Add users」를 클릭합니다.

<img src="../images/YoutubeLiveOAuth/YoutubeLiveOAuth19.png" width="600">

**TeloPon에서 인증에 사용할 Google 계정의 이메일 주소**를 입력하고 「저장」을 클릭합니다.

<img src="../images/YoutubeLiveOAuth/YoutubeLiveOAuth20.png" width="500">

> **중요:** 여기에 추가한 이메일 주소의 계정만 인증할 수 있습니다.  
> 본인 외에도 TeloPon을 사용하는 사람이 있다면, 그 사람의 이메일 주소도 추가해 주세요 (최대 100명).

---

## Step 7: OAuth 클라이언트 ID 생성

왼쪽 메뉴의 「API 및 서비스」→「사용자 인증 정보」를 클릭합니다.  
상단의 「+ 사용자 인증 정보 만들기」 버튼에서 **「OAuth 클라이언트 ID」**를 선택합니다.

<img src="../images/YoutubeLiveOAuth/YoutubeLiveOAuth13.png" width="600">

아래 내용을 입력합니다.

| 항목 | 입력 내용 |
|---|---|
| 애플리케이션 유형 | **데스크톱 앱** |
| 이름 | `TeloPon` (임의) |

<img src="../images/YoutubeLiveOAuth/YoutubeLiveOAuth14.png" width="500">

「만들기」를 클릭하면 **Client ID**와 **Client Secret**이 표시됩니다.  
이 두 가지를 복사해 주세요.

<img src="../images/YoutubeLiveOAuth/YoutubeLiveOAuth15.png" width="400">

> ⚠️ 이 대화상자를 닫으면 Client Secret은 다시 표시할 수 없습니다. 반드시 복사하거나 JSON을 다운로드해 주세요.

---

## Step 8: TeloPon에 입력하여 인증하기

TeloPon의 플러그인 설정 화면을 열고, **Client ID**와 **Client Secret**을 붙여넣은 후 「Google로 인증하기」를 클릭합니다.

<img src="../images/YoutubeLiveOAuth/YoutubeLiveOAuth21.png" width="500">

브라우저가 열리고 Google 계정 선택 화면이 표시됩니다.  
TeloPon에서 사용할 계정 (Step 6에서 테스트 사용자로 추가한 계정)을 선택합니다.

<img src="../images/YoutubeLiveOAuth/YoutubeLiveOAuth22.png" width="600">

> 다른 채널의 관리자 권한으로 연결하는 경우, 관리 대상의 Brand Account를 선택해 주세요.

「이 앱은 Google에서 확인하지 않았습니다」라고 표시되지만, 직접 만든 앱이므로 문제없습니다.  
**「계속」**을 클릭합니다.

<img src="../images/YoutubeLiveOAuth/YoutubeLiveOAuth23.png" width="600">

접근 권한 확인 화면이 표시됩니다. 「계속」을 클릭하여 허용합니다.

<img src="../images/YoutubeLiveOAuth/YoutubeLiveOAuth24.png" width="600">

인증이 성공하면 TeloPon의 설정 화면에 채널명과 썸네일이 표시됩니다.

<img src="../images/YoutubeLiveOAuth/YoutubeLiveOAuth25.png" width="500">

---

## 완료!

이것으로 Google Cloud Console 설정이 완료되었습니다.  
이후에는 TeloPon의 설정 화면에서 방송을 선택하고 연결하기만 하면 사용할 수 있습니다.

👉 [YouTube OAuth 연동 플러그인 사용법으로 돌아가기](YoutubeLiveOAuth.md)
