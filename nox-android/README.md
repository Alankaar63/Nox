# NOX Android App

Native Android companion app for NOX backend.

## Features
- View NOX dashboard (goal, calories, streak, motivation)
- Log workouts
- Log meals
- Connects to the same NOX API endpoints used by web app
- NOX branded launcher icon + splash screen + dark theme

## Open in Android Studio
1. Open Android Studio.
2. Select `Open` and choose:
   - `/Users/vivektripathi/Trial-Ai agent/nox-android`
3. Let Gradle sync complete.

## Backend URL Configuration
Edit `NOX_BASE_URL` in:
- `/Users/vivektripathi/Trial-Ai agent/nox-android/gradle.properties`

Examples:
- Android Emulator -> `http://10.0.2.2:8080/`
- Physical phone on same Wi-Fi -> `http://<your-laptop-ip>:8080/`
- Hosted deployment -> `https://your-domain.com/`

## Build Release APK
In Android Studio:
1. Copy signing template:
   - `cp keystore.properties.example keystore.properties`
2. Edit `keystore.properties` with your real values.
3. In `/Users/vivektripathi/Trial-Ai agent/nox-android/gradle.properties` set:
   - `NOX_ENABLE_RELEASE_SIGNING=true`
3. Build in Android Studio:
   - `Build` -> `Generate Signed Bundle / APK`
   - Choose `APK` and select your keystore.

Or command line (after generating wrapper):
```bash
./gradlew assembleRelease
```

## Quick APK (No Signing Friction)

For immediate testing/deploy preview, generate debug APK:

```bash
cd "/Users/vivektripathi/Trial-Ai agent/nox-android"
./gradlew assembleDebug
```

Then publish to website link:

```bash
cd "/Users/vivektripathi/Trial-Ai agent"
./scripts/publish_android_apk.sh
```

If you see `validateSigningRelease` keystore path errors:
- Ensure `nox-android/keystore.properties` exists.
- Ensure `storeFile` points to an absolute path that exists (example `/Users/vivektripathi/keystores/nox-release.jks`).

## Visual Branding Files
- Icon: `/Users/vivektripathi/Trial-Ai agent/nox-android/app/src/main/res/drawable/ic_nox_logo.xml`
- Splash: `/Users/vivektripathi/Trial-Ai agent/nox-android/app/src/main/res/drawable/splash_screen.xml`
- Theme: `/Users/vivektripathi/Trial-Ai agent/nox-android/app/src/main/res/values/themes.xml`

## Publish APK To Website Download Link
Run:
```bash
cd "/Users/vivektripathi/Trial-Ai agent"
./scripts/publish_android_apk.sh
```

Then set in website file:
- `/Users/vivektripathi/Trial-Ai agent/fitness_nutrition_agent/web/app.js`
- Change `ANDROID_APP_AVAILABLE` to `true`

The website button serves:
- `/downloads/NOX-android-latest.apk`
