# YouTube OAuth Integration - Google Cloud Console Setup Guide

This guide provides detailed, step-by-step instructions with screenshots for setting up Google Cloud Console, which is required to use the YouTube OAuth integration plugin.

> Estimated time: approximately 10-15 minutes

---

## Step 1: Log in to Google Cloud Console

Go to [Google Cloud Console](https://console.cloud.google.com/) and log in with your Google account.  
If this is your first time, agree to the terms of service.

<img src="../images/YoutubeLiveOAuth/YoutubeLiveOAuth1.png" width="500">

Check the box for the terms of service and click "Agree and Continue".

> **If the following screen appears:** Two-factor authentication (MFA) for your Google account is not set up.  
> Click "Go to Settings" to enable it. After enabling, you should be able to access the console within about 60 seconds.
>
> <img src="../images/YoutubeLiveOAuth/YoutubeLiveOAuth2FAError.png" width="500">

---

## Step 2: Create a New Project

Click "Select a project" at the top of the screen.

<img src="../images/YoutubeLiveOAuth/YoutubeLiveOAuth2.png" width="600">

Click "New Project" in the upper right.

<img src="../images/YoutubeLiveOAuth/YoutubeLiveOAuth3.png" width="500">

Enter `TeloPon` (or any name you like) as the project name and click "Create".

---

## Step 3: Configure the OAuth Consent Screen

First, make sure the project name in the upper left of the screen is **TeloPon** (the project you created in Step 2).  
If it's different, click the project name to switch.

<img src="../images/YoutubeLiveOAuth/YoutubeLiveOAuth10.png" width="600">

Click the three horizontal lines (hamburger menu) in the upper left to open the menu, then select "APIs & Services" -> "OAuth consent screen".

If you see "Google Auth Platform has not been configured yet", click "Get Started".

<img src="../images/YoutubeLiveOAuth/YoutubeLiveOAuth4.png" width="600">

### 3-1: App Information

Enter `TeloPon` as the app name, select your support email address, and click "Next".

<img src="../images/YoutubeLiveOAuth/YoutubeLiveOAuth5.png" width="500">

### 3-2: Audience

Select **"External"** and click "Next".

<img src="../images/YoutubeLiveOAuth/YoutubeLiveOAuth6.png" width="400">

> "Internal" is only for Google Workspace (enterprise/school) accounts. For personal Google accounts, select "External".

### 3-3: Contact Information

Confirm that your email address is displayed and click "Next".

<img src="../images/YoutubeLiveOAuth/YoutubeLiveOAuth7.png" width="500">

### 3-4: Finish

Check the box for "I agree to the Google API Services: User Data Policy" and click "Continue".

<img src="../images/YoutubeLiveOAuth/YoutubeLiveOAuth8.png" width="500">

Once all steps have checkmarks, click "Create".

<img src="../images/YoutubeLiveOAuth/YoutubeLiveOAuth9.png" width="400">

---

## Step 4: Enable YouTube Data API v3

Search for `YouTube Data API v3` in the search bar at the top of the screen.

<img src="../images/YoutubeLiveOAuth/YoutubeLiveOAuth11.png" width="600">

Click "YouTube Data API v3" from the search results, then click the "Enable" button.

<img src="../images/YoutubeLiveOAuth/YoutubeLiveOAuth12.png" width="600">

---

## Step 5: Configure Scopes

Click "Data Access" in the left menu.

<img src="../images/YoutubeLiveOAuth/YoutubeLiveOAuth16.png" width="600">

Click "Add or Remove Scopes", then type `youtube.force-ssl` in the filter to search.

<img src="../images/YoutubeLiveOAuth/YoutubeLiveOAuth17.png" width="500">

Check the box for `https://www.googleapis.com/auth/youtube.force-ssl` and click "Update".

<img src="../images/YoutubeLiveOAuth/YoutubeLiveOAuth18.png" width="600">

---

## Step 6: Add Test Users

Click "Audience" in the left menu, then click "+ Add users" in the "Test users" section at the bottom of the page.

<img src="../images/YoutubeLiveOAuth/YoutubeLiveOAuth19.png" width="600">

Enter **the email address of the Google account you will use for TeloPon authentication** and click "Save".

<img src="../images/YoutubeLiveOAuth/YoutubeLiveOAuth20.png" width="500">

> **Important:** Only accounts with email addresses added here can authenticate.  
> If other people will also use TeloPon, add their email addresses as well (up to 100 users).

---

## Step 7: Create an OAuth Client ID

Click "APIs & Services" -> "Credentials" in the left menu.  
Click the "+ Create Credentials" button at the top and select **"OAuth client ID"**.

<img src="../images/YoutubeLiveOAuth/YoutubeLiveOAuth13.png" width="600">

Enter the following information:

| Field | Value |
|---|---|
| Application type | **Desktop app** |
| Name | `TeloPon` (or any name) |

<img src="../images/YoutubeLiveOAuth/YoutubeLiveOAuth14.png" width="500">

Click "Create", and the **Client ID** and **Client Secret** will be displayed.  
Copy both of these.

<img src="../images/YoutubeLiveOAuth/YoutubeLiveOAuth15.png" width="400">

> The Client Secret cannot be displayed again after closing this dialog. Be sure to copy it or download the JSON file.

---

## Step 8: Enter Credentials in TeloPon and Authenticate

Open TeloPon's plugin settings screen, paste the **Client ID** and **Client Secret**, and click "Authenticate with Google".

<img src="../images/YoutubeLiveOAuth/YoutubeLiveOAuth21.png" width="500">

A browser window will open showing the Google account selection screen.  
Select the account you want to use with TeloPon (the account you added as a test user in Step 6).

<img src="../images/YoutubeLiveOAuth/YoutubeLiveOAuth22.png" width="600">

> If you are connecting with manager permissions for another channel, select the managed Brand Account.

A message saying "This app isn't verified by Google" will appear, but since you created the app yourself, this is fine.  
Click **"Continue"**.

<img src="../images/YoutubeLiveOAuth/YoutubeLiveOAuth23.png" width="600">

A permission confirmation screen will appear. Click "Continue" to grant access.

<img src="../images/YoutubeLiveOAuth/YoutubeLiveOAuth24.png" width="600">

Once authentication is successful, the channel name and thumbnail will appear on TeloPon's settings screen.

<img src="../images/YoutubeLiveOAuth/YoutubeLiveOAuth25.png" width="500">

---

## Done!

The Google Cloud Console setup is now complete.  
From now on, you can simply select a stream and connect from TeloPon's settings screen.

[Back to YouTube OAuth Integration Plugin Usage](YoutubeLiveOAuth.md)
