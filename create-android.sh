#!/bin/bash
# Create Android project structure for WebView PWA wrapper
set -euo pipefail

BASE="/opt/data/projects/gym-recomendador/android"
PWA="/opt/data/projects/gym-recomendador/pwa"
JAVA_HOME="/opt/data/jdk-17.0.14+7"
ANDROID_HOME="/opt/data/android-sdk"
PKG="com.gymrecomendador.app"

export JAVA_HOME
export ANDROID_HOME
export PATH="$JAVA_HOME/bin:$ANDROID_HOME/cmdline-tools/latest/bin:$PATH"

echo "📁 Creando estructura de proyecto Android..."

# Create directories
mkdir -p "$BASE/app/src/main/java/com/gymrecomendador/app"
mkdir -p "$BASE/app/src/main/res/values"
mkdir -p "$BASE/app/src/main/res/layout"
mkdir -p "$BASE/app/src/main/res/mipmap-hdpi"
mkdir -p "$BASE/app/src/main/res/mipmap-mdpi"
mkdir -p "$BASE/app/src/main/res/mipmap-xhdpi"
mkdir -p "$BASE/app/src/main/res/mipmap-xxhdpi"
mkdir -p "$BASE/app/src/main/assets/pwa"
mkdir -p "$BASE/gradle/wrapper"

# Copy PWA files to Android assets
echo "📄 Copiando PWA a assets..."
cp -r "$PWA/index.html" "$BASE/app/src/main/assets/pwa/"
cp -r "$PWA/manifest.json" "$BASE/app/src/main/assets/pwa/"
cp -r "$PWA/sw.js" "$BASE/app/src/main/assets/pwa/"
mkdir -p "$BASE/app/src/main/assets/pwa/icons"
cp -r "$PWA/icons/"* "$BASE/app/src/main/assets/pwa/icons/" 2>/dev/null || true

# ─── Root build.gradle ──────────────────────────────────────
cat > "$BASE/build.gradle" << 'EOF'
buildscript {
    repositories {
        google()
        mavenCentral()
    }
    dependencies {
        classpath 'com.android.tools.build:gradle:8.2.0'
    }
}

allprojects {
    repositories {
        google()
        mavenCentral()
    }
}
EOF

# ─── settings.gradle ─────────────────────────────────────────
cat > "$BASE/settings.gradle" << 'EOF'
pluginManagement {
    repositories {
        google()
        mavenCentral()
        gradlePluginPortal()
    }
}
dependencyResolutionManagement {
    repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS)
    repositories {
        google()
        mavenCentral()
    }
}
rootProject.name = "GymRecomendador"
include ':app'
EOF

# ─── App build.gradle ────────────────────────────────────────
cat > "$BASE/app/build.gradle" << 'EOF'
plugins {
    id 'com.android.application'
}

android {
    namespace 'com.gymrecomendador.app'
    compileSdk 34

    defaultConfig {
        applicationId 'com.gymrecomendador.app'
        minSdk 21
        targetSdk 34
        versionCode 1
        versionName '1.0.0'
    }

    buildTypes {
        release {
            minifyEnabled false
        }
    }

    compileOptions {
        sourceCompatibility JavaVersion.VERSION_17
        targetCompatibility JavaVersion.VERSION_17
    }
}

dependencies {
    implementation 'androidx.appcompat:appcompat:1.6.1'
    implementation 'androidx.webkit:webkit:1.8.0'
}
EOF

# ─── AndroidManifest.xml ─────────────────────────────────────
cat > "$BASE/app/src/main/AndroidManifest.xml" << 'EOF'
<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android">

    <uses-permission android:name="android.permission.INTERNET" />

    <application
        android:allowBackup="true"
        android:icon="@mipmap/ic_launcher"
        android:label="@string/app_name"
        android:supportsRtl="true"
        android:theme="@style/Theme.GymRecomendador">

        <activity
            android:name=".MainActivity"
            android:exported="true"
            android:configChanges="orientation|screenSize|screenLayout|keyboardHidden"
            android:theme="@style/Theme.GymRecomendador">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>

    </application>
</manifest>
EOF

# ─── MainActivity.java ───────────────────────────────────────
cat > "$BASE/app/src/main/java/com/gymrecomendador/app/MainActivity.java" << 'EOF'
package com.gymrecomendador.app;

import android.os.Bundle;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import androidx.appcompat.app.AppCompatActivity;

public class MainActivity extends AppCompatActivity {
    private WebView webView;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        webView = new WebView(this);
        setContentView(webView);

        WebSettings settings = webView.getSettings();
        settings.setJavaScriptEnabled(true);
        settings.setDomStorageEnabled(true);
        settings.setCacheMode(WebSettings.LOAD_DEFAULT);
        settings.setAllowFileAccess(true);
        settings.setAllowContentAccess(true);

        // Enable dark mode
        settings.setForceDark(WebSettings.FORCE_DARK_ON);

        webView.setWebViewClient(new WebViewClient());

        // Load the PWA from assets
        webView.loadUrl("file:///android_asset/pwa/index.html");
    }

    @Override
    public void onBackPressed() {
        if (webView.canGoBack()) {
            webView.goBack();
        } else {
            super.onBackPressed();
        }
    }
}
EOF

# ─── strings.xml ─────────────────────────────────────────────
cat > "$BASE/app/src/main/res/values/strings.xml" << 'EOF'
<?xml version="1.0" encoding="utf-8"?>
<resources>
    <string name="app_name">Gym Recomendador</string>
</resources>
EOF

# ─── colors.xml ──────────────────────────────────────────────
cat > "$BASE/app/src/main/res/values/colors.xml" << 'EOF'
<?xml version="1.0" encoding="utf-8"?>
<resources>
    <color name="background">#0D0D0D</color>
    <color name="primary">#E63946</color>
</resources>
EOF

# ─── themes.xml ──────────────────────────────────────────────
cat > "$BASE/app/src/main/res/values/themes.xml" << 'EOF'
<?xml version="1.0" encoding="utf-8"?>
<resources>
    <style name="Theme.GymRecomendador" parent="Theme.AppCompat.DayNight.NoActionBar">
        <item name="android:statusBarColor">#0D0D0D</item>
        <item name="android:navigationBarColor">#0D0D0D</item>
        <item name="android:windowBackground">@color/background</item>
    </style>
</resources>
EOF

# ─── Generate launcher icons ─────────────────────────────────
echo "🖼️ Generando iconos..."
python3 /opt/data/projects/gym-recomendador/generate-android-icons.py "$BASE" 2>/dev/null || echo "   (iconos base)"

# ─── Gradle wrapper properties ───────────────────────────────
cat > "$BASE/gradle/wrapper/gradle-wrapper.properties" << 'EOF'
distributionBase=GRADLE_USER_HOME
distributionPath=wrapper/dists
distributionUrl=https\://services.gradle.org/distributions/gradle-8.5-bin.zip
zipStoreBase=GRADLE_USER_HOME
zipStorePath=wrapper/dists
EOF

echo "✅ Estructura Android creada en $BASE"
echo "PROGRESO:55"