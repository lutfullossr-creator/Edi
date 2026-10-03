#!/usr/bin/env python3
# Edi APK loyihasini android/ papkasida yaratadi (GitHub Actions ishlatadi).
import glob, os, shutil, sys

ROOT = 'android'
PKG = 'com.lutfullo.edi'
F = {}

F['settings.gradle.kts'] = r'''pluginManagement {
    repositories { google(); mavenCentral(); gradlePluginPortal() }
}
dependencyResolutionManagement {
    repositoriesMode.set(RepositoriesMode.PREFER_SETTINGS)
    repositories { google(); mavenCentral() }
}
rootProject.name = "Edi"
include(":app")
'''

F['build.gradle.kts'] = r'''plugins {
    id("com.android.application") version "8.5.2" apply false
    id("org.jetbrains.kotlin.android") version "1.9.24" apply false
}
'''

F['gradle.properties'] = r'''org.gradle.jvmargs=-Xmx2g -Dfile.encoding=UTF-8
android.useAndroidX=false
android.nonTransitiveRClass=true
kotlin.code.style=official
'''

F['app/build.gradle.kts'] = r'''plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
}

val runNum = (System.getenv("RUN_NUM") ?: "1").toInt()

android {
    namespace = "com.lutfullo.edi"
    compileSdk = 34

    defaultConfig {
        applicationId = "com.lutfullo.edi"
        minSdk = 26
        targetSdk = 34
        versionCode = runNum
        versionName = "1.0." + runNum
    }

    signingConfigs {
        getByName("debug") {
            val ks = rootProject.file("edi.keystore")
            val pw = System.getenv("EDI_KS_PASS")
            if (ks.exists() && !pw.isNullOrEmpty()) {
                storeFile = ks
                storePassword = pw
                keyAlias = "edi"
                keyPassword = pw
                storeType = "pkcs12"
            }
        }
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }
    kotlinOptions { jvmTarget = "17" }
}
'''

F['app/src/main/AndroidManifest.xml'] = r'''<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android">

    <uses-permission android:name="android.permission.INTERNET" />
    <uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />
    <uses-permission android:name="android.permission.CAMERA" />
    <uses-permission android:name="android.permission.RECORD_AUDIO" />
    <uses-permission android:name="android.permission.MODIFY_AUDIO_SETTINGS" />
    <uses-permission android:name="android.permission.READ_CONTACTS" />
    <uses-permission android:name="android.permission.CALL_PHONE" />
    <uses-permission android:name="android.permission.SEND_SMS" />
    <uses-permission android:name="android.permission.ANSWER_PHONE_CALLS" />
    <uses-permission android:name="android.permission.ACCESS_FINE_LOCATION" />
    <uses-permission android:name="android.permission.ACCESS_COARSE_LOCATION" />
    <uses-permission android:name="android.permission.READ_MEDIA_AUDIO" />
    <uses-permission android:name="android.permission.READ_EXTERNAL_STORAGE" android:maxSdkVersion="32" />
    <uses-permission android:name="android.permission.WRITE_EXTERNAL_STORAGE" android:maxSdkVersion="28" />
    <uses-permission android:name="android.permission.POST_NOTIFICATIONS" />
    <uses-permission android:name="android.permission.SYSTEM_ALERT_WINDOW" />
    <uses-permission android:name="android.permission.WRITE_SETTINGS" />
    <uses-permission android:name="android.permission.ACCESS_NOTIFICATION_POLICY" />
    <uses-permission android:name="com.android.alarm.permission.SET_ALARM" />
    <uses-permission android:name="android.permission.KILL_BACKGROUND_PROCESSES" />
    <uses-permission android:name="android.permission.REQUEST_DELETE_PACKAGES" />
    <uses-permission android:name="android.permission.VIBRATE" />
    <uses-permission android:name="android.permission.WAKE_LOCK" />
    <uses-permission android:name="android.permission.RECEIVE_BOOT_COMPLETED" />
    <uses-permission android:name="android.permission.REQUEST_IGNORE_BATTERY_OPTIMIZATIONS" />
    <uses-permission android:name="android.permission.FOREGROUND_SERVICE" />
    <uses-permission android:name="android.permission.FOREGROUND_SERVICE_MICROPHONE" />
    <uses-permission android:name="android.permission.FOREGROUND_SERVICE_SPECIAL_USE" />
    <uses-permission android:name="android.permission.REQUEST_INSTALL_PACKAGES" />

    <uses-feature android:name="android.hardware.camera" android:required="false" />
    <uses-feature android:name="android.hardware.microphone" android:required="false" />
    <uses-feature android:name="android.hardware.telephony" android:required="false" />

    <queries>
        <intent>
            <action android:name="android.intent.action.MAIN" />
            <category android:name="android.intent.category.LAUNCHER" />
        </intent>
    </queries>

    <application
        android:label="Edi"
        android:icon="@mipmap/ic_launcher"
        android:roundIcon="@mipmap/ic_launcher"
        android:allowBackup="false"
        android:usesCleartextTraffic="false"
        android:hardwareAccelerated="true"
        android:theme="@android:style/Theme.DeviceDefault.NoActionBar">

        <activity
            android:name=".MainActivity"
            android:exported="true"
            android:launchMode="singleTask"
            android:windowSoftInputMode="adjustResize"
            android:configChanges="orientation|screenSize|keyboardHidden|smallestScreenSize|screenLayout|uiMode|density|keyboard|navigation">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>

        <service
            android:name=".EdiAccessibility"
            android:exported="true"
            android:label="Edi"
            android:permission="android.permission.BIND_ACCESSIBILITY_SERVICE">
            <intent-filter>
                <action android:name="android.accessibilityservice.AccessibilityService" />
            </intent-filter>
            <meta-data
                android:name="android.accessibilityservice"
                android:resource="@xml/edi_access" />
        </service>

        <service
            android:name=".EdiNotifListener"
            android:exported="true"
            android:label="Edi"
            android:permission="android.permission.BIND_NOTIFICATION_LISTENER_SERVICE">
            <intent-filter>
                <action android:name="android.service.notification.NotificationListenerService" />
            </intent-filter>
        </service>

        <service
            android:name=".ListenService"
            android:exported="false"
            android:foregroundServiceType="microphone" />

        <receiver
            android:name=".InstallReceiver"
            android:exported="false" />

        <receiver
            android:name=".BootReceiver"
            android:exported="true">
            <intent-filter>
                <action android:name="android.intent.action.BOOT_COMPLETED" />
                <action android:name="android.intent.action.MY_PACKAGE_REPLACED" />
                <action android:name="android.intent.action.QUICKBOOT_POWERON" />
            </intent-filter>
        </receiver>

        <service
            android:name=".BubbleService"
            android:exported="false"
            android:foregroundServiceType="specialUse|microphone">
            <property
                android:name="android.app.PROPERTY_SPECIAL_USE_FGS_SUBTYPE"
                android:value="voice_assistant_overlay" />
        </service>
    </application>
</manifest>
'''

F['app/src/main/res/values/strings.xml'] = r'''<?xml version="1.0" encoding="utf-8"?>
<resources>
    <string name="app_name">Edi</string>
    <string name="access_desc">Edi buyruqlari uchun: orqaga, skrinshot, ekranni qulflash, so\'nggi ilovalar va bildirishnoma paneli.</string>
</resources>
'''

F['app/src/main/res/values/colors.xml'] = r'''<?xml version="1.0" encoding="utf-8"?>
<resources>
    <color name="ic_bg">#2563EB</color>
</resources>
'''

F['app/src/main/res/xml/edi_access.xml'] = r'''<?xml version="1.0" encoding="utf-8"?>
<accessibility-service xmlns:android="http://schemas.android.com/apk/res/android"
    android:accessibilityEventTypes="typeWindowStateChanged"
    android:accessibilityFeedbackType="feedbackGeneric"
    android:accessibilityFlags="flagDefault"
    android:canRetrieveWindowContent="true"
    android:canPerformGestures="true"
    android:description="@string/access_desc"
    android:notificationTimeout="200" />
'''

F['app/src/main/res/mipmap-anydpi-v26/ic_launcher.xml'] = r'''<?xml version="1.0" encoding="utf-8"?>
<adaptive-icon xmlns:android="http://schemas.android.com/apk/res/android">
    <background android:drawable="@color/ic_bg" />
    <foreground android:drawable="@drawable/ic_fg" />
</adaptive-icon>
'''

F['app/src/main/res/drawable/ic_fg.xml'] = r'''<?xml version="1.0" encoding="utf-8"?>
<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="108dp"
    android:height="108dp"
    android:viewportWidth="108"
    android:viewportHeight="108">
    <path
        android:fillColor="#FFFFFF"
        android:pathData="M38,32 H70 A8,8 0 0 1 78,40 V60 A8,8 0 0 1 70,68 H52 L42,78 V68 H38 A8,8 0 0 1 30,60 V40 A8,8 0 0 1 38,32 Z" />
    <path
        android:fillColor="#2563EB"
        android:pathData="M43,50 a3,3 0 1 0 6,0 a3,3 0 1 0 -6,0 Z M59,50 a3,3 0 1 0 6,0 a3,3 0 1 0 -6,0 Z" />
</vector>
'''

KT = 'app/src/main/java/com/lutfullo/edi/'

F[KT + 'EdiAccessibility.kt'] = r'''package com.lutfullo.edi

import android.accessibilityservice.AccessibilityService
import android.accessibilityservice.GestureDescription
import android.content.Intent
import android.graphics.Path
import android.os.Build
import android.os.Bundle
import android.view.accessibility.AccessibilityEvent
import android.view.accessibility.AccessibilityNodeInfo

class EdiAccessibility : AccessibilityService() {
    companion object {
        @Volatile var inst: EdiAccessibility? = null
    }

    override fun onServiceConnected() { inst = this }
    override fun onAccessibilityEvent(e: AccessibilityEvent?) {}
    override fun onInterrupt() {}
    override fun onUnbind(i: Intent?): Boolean { inst = null; return super.onUnbind(i) }

    private fun low(s: CharSequence?): String = (s?.toString() ?: "").lowercase()

    private fun clickableOf(n0: AccessibilityNodeInfo?): AccessibilityNodeInfo? {
        var c = n0
        var d = 0
        while (c != null && d < 7) {
            if (c.isClickable && c.isEnabled) return c
            c = c.parent
            d++
        }
        return null
    }

    private fun walk(n: AccessibilityNodeInfo?, out: MutableList<AccessibilityNodeInfo>, depth: Int) {
        if (n == null || depth > 40 || out.size > 600) return
        out.add(n)
        for (i in 0 until n.childCount) walk(n.getChild(i), out, depth + 1)
    }

    private fun all(): List<AccessibilityNodeInfo> {
        val r = rootInActiveWindow ?: return emptyList()
        val out = ArrayList<AccessibilityNodeInfo>()
        walk(r, out, 0)
        return out
    }

    fun clickText(t: String): String {
        val q = low(t).trim()
        if (q.isEmpty()) return "❓ Nimani bosish kerak?"
        val nodes = all()
        if (nodes.isEmpty()) return "⚠️ Ekran o'qilmadi"
        var best: AccessibilityNodeInfo? = null
        for (n in nodes) {
            val tx = low(n.text)
            val cd = low(n.contentDescription)
            val id = low(n.viewIdResourceName)
            if (tx == q || cd == q) { best = n; break }
        }
        if (best == null) for (n in nodes) {
            if (low(n.text).contains(q) || low(n.contentDescription).contains(q) || low(n.viewIdResourceName).endsWith("/" + q)) { best = n; break }
        }
        if (best == null) return "❌ «" + t + "» ekranda topilmadi"
        val c = clickableOf(best)
        if (c != null && c.performAction(AccessibilityNodeInfo.ACTION_CLICK)) return "👆 Bosildi: " + t
        val r = android.graphics.Rect()
        best.getBoundsInScreen(r)
        return if (tap(r.centerX().toFloat(), r.centerY().toFloat())) "👆 Bosildi: " + t else "❌ Bosilmadi"
    }

    fun tap(x: Float, y: Float): Boolean {
        if (Build.VERSION.SDK_INT < 24) return false
        val p = Path(); p.moveTo(x, y)
        val g = GestureDescription.Builder().addStroke(GestureDescription.StrokeDescription(p, 0, 60)).build()
        return dispatchGesture(g, null, null)
    }

    fun swipe(dir: String): String {
        if (Build.VERSION.SDK_INT < 24) return "⚠️ Android 7+ kerak"
        val m = resources.displayMetrics
        val w = m.widthPixels.toFloat(); val h = m.heightPixels.toFloat()
        val p = Path()
        when (dir) {
            "down" -> { p.moveTo(w / 2, h * 0.75f); p.lineTo(w / 2, h * 0.25f) }
            "up" -> { p.moveTo(w / 2, h * 0.25f); p.lineTo(w / 2, h * 0.75f) }
            "left" -> { p.moveTo(w * 0.8f, h / 2); p.lineTo(w * 0.2f, h / 2) }
            else -> { p.moveTo(w * 0.2f, h / 2); p.lineTo(w * 0.8f, h / 2) }
        }
        val g = GestureDescription.Builder().addStroke(GestureDescription.StrokeDescription(p, 0, 320)).build()
        return if (dispatchGesture(g, null, null)) "↕️ Surildi" else "❌ Surilmadi"
    }

    fun scroll(dir: String): String {
        val fwd = dir == "down" || dir == "right"
        val sc = all().firstOrNull { it.isScrollable }
        if (sc != null) {
            val act = if (fwd) AccessibilityNodeInfo.ACTION_SCROLL_FORWARD else AccessibilityNodeInfo.ACTION_SCROLL_BACKWARD
            if (sc.performAction(act)) return if (fwd) "⬇️ Pastga" else "⬆️ Tepaga"
        }
        return swipe(dir)
    }

    fun typeText(t: String): String {
        val r = rootInActiveWindow ?: return "⚠️ Ekran o'qilmadi"
        var f = r.findFocus(AccessibilityNodeInfo.FOCUS_INPUT)
        if (f == null) f = all().firstOrNull { it.isEditable }
        if (f == null) return "❌ Yozish maydoni topilmadi. Avval maydonni bosing"
        val old = if (f.text != null && !f.isShowingHintText) f.text.toString() else ""
        val b = Bundle()
        b.putCharSequence(AccessibilityNodeInfo.ACTION_ARGUMENT_SET_TEXT_CHARSEQUENCE, old + t)
        if (f.performAction(AccessibilityNodeInfo.ACTION_SET_TEXT, b)) return "⌨️ Yozildi: " + t
        try {
            val cm = getSystemService(android.content.Context.CLIPBOARD_SERVICE) as android.content.ClipboardManager
            cm.setPrimaryClip(android.content.ClipData.newPlainText("edi", t))
            f.performAction(AccessibilityNodeInfo.ACTION_FOCUS)
            if (f.performAction(AccessibilityNodeInfo.ACTION_PASTE)) return "⌨️ Yozildi: " + t
        } catch (e: Exception) {}
        return "❌ Yozilmadi"
    }

    fun clearText(): String {
        val r = rootInActiveWindow ?: return "⚠️ Ekran o'qilmadi"
        val f = r.findFocus(AccessibilityNodeInfo.FOCUS_INPUT) ?: return "❌ Yozish maydoni yo'q"
        val b = Bundle()
        b.putCharSequence(AccessibilityNodeInfo.ACTION_ARGUMENT_SET_TEXT_CHARSEQUENCE, "")
        return if (f.performAction(AccessibilityNodeInfo.ACTION_SET_TEXT, b)) "🧹 Tozalandi" else "❌ Bajarilmadi"
    }

    fun enter(): String {
        val r = rootInActiveWindow ?: return "⚠️ Ekran o'qilmadi"
        val f = r.findFocus(AccessibilityNodeInfo.FOCUS_INPUT) ?: return "❌ Yozish maydoni yo'q"
        if (Build.VERSION.SDK_INT >= 30) {
            if (f.performAction(AccessibilityNodeInfo.AccessibilityAction.ACTION_IME_ENTER.id)) return "↩️ Enter"
        }
        return "❌ Enter bajarilmadi"
    }

    private fun findNode(q: String): AccessibilityNodeInfo? {
        val nodes = all()
        for (n in nodes) { if (low(n.text) == q || low(n.contentDescription) == q) return n }
        for (n in nodes) { if (low(n.text).contains(q) || low(n.contentDescription).contains(q)) return n }
        return null
    }

    fun longPress(t: String): String {
        val q = low(t).trim()
        val n = findNode(q) ?: return "❌ «" + t + "» topilmadi"
        var c: AccessibilityNodeInfo? = n
        var d = 0
        while (c != null && d < 7) {
            if (c.isLongClickable && c.performAction(AccessibilityNodeInfo.ACTION_LONG_CLICK)) return "👆 Uzoq bosildi: " + t
            c = c.parent
            d++
        }
        if (Build.VERSION.SDK_INT >= 24) {
            val r = android.graphics.Rect()
            n.getBoundsInScreen(r)
            val p = Path(); p.moveTo(r.centerX().toFloat(), r.centerY().toFloat())
            val g = GestureDescription.Builder().addStroke(GestureDescription.StrokeDescription(p, 0, 800)).build()
            if (dispatchGesture(g, null, null)) return "👆 Uzoq bosildi: " + t
        }
        return "❌ Bajarilmadi"
    }

    fun tapPct(a: String): String {
        val p = a.split(",")
        if (p.size < 2) return "❓ Format: x,y (foizda)"
        val m = resources.displayMetrics
        val x = (p[0].trim().toFloatOrNull() ?: 50f) / 100f * m.widthPixels
        val y = (p[1].trim().toFloatOrNull() ?: 50f) / 100f * m.heightPixels
        return if (tap(x, y)) "👆 Bosildi" else "❌ Bosilmadi"
    }

    fun edit(kind: String): String {
        val r = rootInActiveWindow ?: return "⚠️ Ekran o'qilmadi"
        val f = r.findFocus(AccessibilityNodeInfo.FOCUS_INPUT) ?: all().firstOrNull { it.isEditable } ?: return "❌ Yozish maydoni yo'q"
        f.performAction(AccessibilityNodeInfo.ACTION_FOCUS)
        if (kind == "all") {
            val b = Bundle()
            b.putInt(AccessibilityNodeInfo.ACTION_ARGUMENT_SELECTION_START_INT, 0)
            b.putInt(AccessibilityNodeInfo.ACTION_ARGUMENT_SELECTION_END_INT, (f.text?.length ?: 0))
            return if (f.performAction(AccessibilityNodeInfo.ACTION_SET_SELECTION, b)) "✅ Hammasi belgilandi" else "❌ Bajarilmadi"
        }
        val act = when (kind) {
            "copy" -> AccessibilityNodeInfo.ACTION_COPY
            "cut" -> AccessibilityNodeInfo.ACTION_CUT
            else -> AccessibilityNodeInfo.ACTION_PASTE
        }
        return if (f.performAction(act)) "✅ Bajarildi" else "❌ Bajarilmadi"
    }

    fun screenText(): String {
        val sb = StringBuilder()
        for (n in all()) {
            val t = (n.text ?: n.contentDescription)?.toString() ?: continue
            if (t.isBlank() || sb.length > 700) continue
            sb.append(t.trim()).append("; ")
        }
        return if (sb.isEmpty()) "🖥 Ekranda matn topilmadi" else "🖥 Ekranda: " + sb.toString()
    }
}
'''

F[KT + 'EdiNotifListener.kt'] = r'''package com.lutfullo.edi

import android.service.notification.NotificationListenerService

class EdiNotifListener : NotificationListenerService() {
    companion object {
        @Volatile var inst: EdiNotifListener? = null
    }

    override fun onListenerConnected() { inst = this }
    override fun onListenerDisconnected() { inst = null }
}
'''

F[KT + 'ListenService.kt'] = r'''package com.lutfullo.edi

import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.app.Service
import android.content.Intent
import android.content.pm.ServiceInfo
import android.os.Build
import android.os.Bundle
import android.os.Handler
import android.os.IBinder
import android.os.Looper
import android.speech.RecognitionListener
import android.speech.RecognizerIntent
import android.speech.SpeechRecognizer
import org.json.JSONObject

class ListenService : Service() {
    private var sr: SpeechRecognizer? = null
    private val h = Handler(Looper.getMainLooper())
    private var on = false
    private val wake = Regex("^\\s*(?:(?:hey|hay|ey|ok|okay|hi)\\s+)?(?:edi|eddi|eddy|edy|eddie|edie|эди|еди|ади)\\b[\\s,.:!-]*", RegexOption.IGNORE_CASE)

    override fun onBind(i: Intent?): IBinder? = null

    override fun onStartCommand(i: Intent?, f: Int, id: Int): Int {
        val nm = getSystemService(NotificationManager::class.java)
        nm.createNotificationChannel(NotificationChannel("edi_listen", "Edi tinglash", NotificationManager.IMPORTANCE_LOW))
        val pi = PendingIntent.getActivity(this, 0, Intent(this, MainActivity::class.java), PendingIntent.FLAG_IMMUTABLE)
        val n = Notification.Builder(this, "edi_listen")
            .setContentTitle("Edi tinglayapti")
            .setContentText("\"Edi, ...\" deb buyruq bering")
            .setSmallIcon(android.R.drawable.ic_btn_speak_now)
            .setContentIntent(pi)
            .setOngoing(true)
            .build()
        if (Build.VERSION.SDK_INT >= 29) startForeground(77, n, ServiceInfo.FOREGROUND_SERVICE_TYPE_MICROPHONE)
        else startForeground(77, n)
        if (!on) { on = true; h.post { begin() } }
        return START_STICKY
    }

    private fun begin() {
        if (!on) return
        if (!SpeechRecognizer.isRecognitionAvailable(this)) { stopSelf(); return }
        try { sr?.destroy() } catch (e: Exception) {}
        val r = SpeechRecognizer.createSpeechRecognizer(this)
        sr = r
        r.setRecognitionListener(object : RecognitionListener {
            override fun onReadyForSpeech(p: Bundle?) {}
            override fun onBeginningOfSpeech() {}
            override fun onRmsChanged(v: Float) {}
            override fun onBufferReceived(b: ByteArray?) {}
            override fun onEndOfSpeech() {}
            override fun onPartialResults(p: Bundle?) {}
            override fun onEvent(t: Int, p: Bundle?) {}
            override fun onError(e: Int) {
                if (e == SpeechRecognizer.ERROR_INSUFFICIENT_PERMISSIONS) { stopSelf(); return }
                again(if (e == SpeechRecognizer.ERROR_RECOGNIZER_BUSY) 1500L else 400L)
            }
            override fun onResults(res: Bundle?) {
                val list = res?.getStringArrayList(SpeechRecognizer.RESULTS_RECOGNITION)
                if (list != null) handle(list)
                again(300L)
            }
        })
        val it = Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH)
            .putExtra(RecognizerIntent.EXTRA_LANGUAGE_MODEL, RecognizerIntent.LANGUAGE_MODEL_FREE_FORM)
            .putExtra(RecognizerIntent.EXTRA_LANGUAGE, "uz-UZ")
            .putExtra(RecognizerIntent.EXTRA_PARTIAL_RESULTS, false)
            .putExtra(RecognizerIntent.EXTRA_MAX_RESULTS, 5)
        try { r.startListening(it) } catch (e: Exception) { again(1500L) }
    }

    private fun again(ms: Long) { if (on) h.postDelayed({ begin() }, ms) }

    // Faqat "Edi, ..." bilan boshlangan gaplar buyruq sifatida yuboriladi
    private fun handle(list: List<String>) {
        for (t in list) {
            val m = wake.find(t) ?: continue
            val cmd = t.substring(m.range.last + 1).trim()
            if (cmd.isEmpty()) return
            val q = JSONObject.quote(cmd)
            val w = MainActivity.web
            if (w != null) {
                w.post { w.evaluateJavascript("window.ediVoice&&window.ediVoice(" + q + ")", null) }
                return
            }
            val e = BubbleService.engine
            if (e != null) e.post { e.evaluateJavascript("window.ediBg&&window.ediBg(" + q + ")", null) }
            return
        }
    }

    override fun onDestroy() {
        on = false
        h.removeCallbacksAndMessages(null)
        try { sr?.destroy() } catch (e: Exception) {}
        super.onDestroy()
    }
}
'''

F[KT + 'MainActivity.kt'] = r'''package com.lutfullo.edi

import android.Manifest
import android.app.Activity
import android.app.AlertDialog
import android.content.Intent
import android.content.pm.PackageManager
import android.graphics.Bitmap
import android.graphics.Color
import android.net.ConnectivityManager
import android.net.NetworkCapabilities
import android.net.Uri
import android.os.Bundle
import android.os.Handler
import android.os.Looper
import android.speech.RecognizerIntent
import android.webkit.GeolocationPermissions
import android.webkit.JsPromptResult
import android.webkit.JsResult
import android.webkit.PermissionRequest
import android.webkit.ValueCallback
import android.webkit.WebChromeClient
import android.webkit.WebResourceError
import android.webkit.WebResourceRequest
import android.webkit.WebSettings
import android.webkit.WebView
import android.webkit.WebViewClient
import android.widget.EditText
import android.widget.Toast
import org.json.JSONObject

class MainActivity : Activity() {
    companion object {
        const val URL = "https://lutfullossr-creator.github.io/Edi/"
        const val HOST = "lutfullossr-creator.github.io"
        const val RC_FILE = 9001
        const val RC_VOICE = 9002
        const val RC_WEBPERM = 9003
        const val RC_GEO = 9004
        @Volatile var web: WebView? = null
        @Volatile var visible = false

        // Blob yuklab olishni ushlab, native saqlashga yo'naltiradi
        const val DL_JS = """(function(){if(window.__ediDl)return;window.__ediDl=1;var o=HTMLAnchorElement.prototype.click;HTMLAnchorElement.prototype.click=function(){var a=this;if(a.download&&a.href&&a.href.indexOf('blob:')===0&&window.Android&&window.Android.saveFile){fetch(a.href).then(function(r){return r.blob()}).then(function(b){var f=new FileReader();f.onloadend=function(){window.Android.saveFile(a.download,b.type||'application/octet-stream',String(f.result).split(',')[1])};f.readAsDataURL(b)});return}return o.apply(this,arguments)}})();"""

        // Orqaga tugmasi: ochiq oynalarni yopadi
        const val CLOSE_JS = """(function(){var q=[['pmod','pcl'],['ocrmod','ocrcl']];for(var i=0;i<q.length;i++){var m=document.getElementById(q[i][0]);if(m&&m.classList.contains('on')){var b=document.getElementById(q[i][1]);if(b){b.click();return 1}}}var d=document.querySelectorAll('.modal.on');if(d.length){d[d.length-1].classList.remove('on');return 1}return 0})()"""
    }

    private lateinit var bridge: Bridge
    private var pendingQ: String? = null
    private var loaded = false
    private var fileCb: ValueCallback<Array<Uri>>? = null
    private var pendingWeb: PermissionRequest? = null
    private var pendingGeoOrigin: String? = null
    private var pendingGeoCb: GeolocationPermissions.Callback? = null

    private fun online(): Boolean {
        val cm = getSystemService(CONNECTIVITY_SERVICE) as ConnectivityManager
        val n = cm.activeNetwork ?: return false
        val c = cm.getNetworkCapabilities(n) ?: return false
        return c.hasCapability(NetworkCapabilities.NET_CAPABILITY_INTERNET)
    }

    private fun okOrigin(u: Uri?): Boolean {
        if (u == null) return false
        return u.host == HOST || u.scheme == "file"
    }

    private fun handleWebPerm(r: PermissionRequest) {
        if (!okOrigin(r.origin)) { r.deny(); return }
        val need = ArrayList<String>()
        for (res in r.resources) {
            if (res == PermissionRequest.RESOURCE_VIDEO_CAPTURE) need.add(Manifest.permission.CAMERA)
            if (res == PermissionRequest.RESOURCE_AUDIO_CAPTURE) need.add(Manifest.permission.RECORD_AUDIO)
        }
        val miss = need.filter { checkSelfPermission(it) != PackageManager.PERMISSION_GRANTED }
        if (miss.isEmpty()) { r.grant(r.resources); return }
        pendingWeb?.deny()
        pendingWeb = r
        requestPermissions(miss.toTypedArray(), RC_WEBPERM)
    }

    override fun onCreate(b: Bundle?) {
        super.onCreate(b)
        pendingQ = intent?.getStringExtra("q")
        window.statusBarColor = Color.parseColor("#0a0a0a")
        window.navigationBarColor = Color.parseColor("#0a0a0a")
        val w = WebView(this)
        web = w
        setContentView(w)
        w.setBackgroundColor(Color.parseColor("#0a0a0a"))
        val s = w.settings
        s.javaScriptEnabled = true
        s.domStorageEnabled = true
        s.databaseEnabled = true
        s.mediaPlaybackRequiresUserGesture = false
        s.javaScriptCanOpenWindowsAutomatically = true
        s.setSupportMultipleWindows(false)
        s.setGeolocationEnabled(true)
        s.textZoom = 100
        s.cacheMode = if (online()) WebSettings.LOAD_DEFAULT else WebSettings.LOAD_CACHE_ELSE_NETWORK

        bridge = Bridge(this, w, this)
        w.addJavascriptInterface(bridge, "Android")

        w.webViewClient = object : WebViewClient() {
            override fun shouldOverrideUrlLoading(v: WebView?, r: WebResourceRequest?): Boolean {
                val u = r?.url ?: return true
                val sch = u.scheme ?: ""
                if ((sch == "https" || sch == "http") && u.host == HOST) return false
                if (sch == "file") return false
                if (sch == "http" || sch == "https" || sch == "tel" || sch == "mailto") {
                    try { startActivity(Intent(Intent.ACTION_VIEW, u)) } catch (e: Exception) {}
                }
                return true
            }

            override fun onPageStarted(v: WebView?, url: String?, f: Bitmap?) { v?.evaluateJavascript(DL_JS, null) }
            override fun onPageFinished(v: WebView?, url: String?) { v?.evaluateJavascript(DL_JS, null); loaded = true; runPending() }

            override fun onReceivedError(v: WebView?, r: WebResourceRequest?, e: WebResourceError?) {
                if (r != null && r.isForMainFrame && v != null && !(v.url ?: "").startsWith("file:")) {
                    v.loadUrl("file:///android_asset/index.html")
                }
            }
        }

        w.webChromeClient = object : WebChromeClient() {
            override fun onPermissionRequest(request: PermissionRequest?) {
                if (request == null) return
                runOnUiThread { handleWebPerm(request) }
            }

            override fun onGeolocationPermissionsShowPrompt(origin: String?, callback: GeolocationPermissions.Callback?) {
                if (origin == null || callback == null) return
                runOnUiThread {
                    if (checkSelfPermission(Manifest.permission.ACCESS_FINE_LOCATION) == PackageManager.PERMISSION_GRANTED) {
                        callback.invoke(origin, true, false)
                    } else {
                        pendingGeoOrigin = origin
                        pendingGeoCb = callback
                        requestPermissions(arrayOf(Manifest.permission.ACCESS_FINE_LOCATION), RC_GEO)
                    }
                }
            }

            override fun onShowFileChooser(v: WebView?, cb: ValueCallback<Array<Uri>>?, p: FileChooserParams?): Boolean {
                if (cb == null || p == null) return false
                fileCb?.onReceiveValue(null)
                fileCb = cb
                return try {
                    startActivityForResult(p.createIntent(), RC_FILE)
                    true
                } catch (e: Exception) {
                    fileCb = null
                    false
                }
            }

            override fun onJsAlert(v: WebView?, url: String?, message: String?, r: JsResult?): Boolean {
                if (r == null) return false
                AlertDialog.Builder(this@MainActivity).setMessage(message)
                    .setPositiveButton("OK") { _, _ -> r.confirm() }
                    .setOnCancelListener { r.cancel() }.show()
                return true
            }

            override fun onJsConfirm(v: WebView?, url: String?, message: String?, r: JsResult?): Boolean {
                if (r == null) return false
                AlertDialog.Builder(this@MainActivity).setMessage(message)
                    .setPositiveButton("OK") { _, _ -> r.confirm() }
                    .setNegativeButton("Bekor") { _, _ -> r.cancel() }
                    .setOnCancelListener { r.cancel() }.show()
                return true
            }

            override fun onJsPrompt(v: WebView?, url: String?, message: String?, def: String?, r: JsPromptResult?): Boolean {
                if (r == null) return false
                val et = EditText(this@MainActivity)
                et.setText(def ?: "")
                AlertDialog.Builder(this@MainActivity).setMessage(message).setView(et)
                    .setPositiveButton("OK") { _, _ -> r.confirm(et.text.toString()) }
                    .setNegativeButton("Bekor") { _, _ -> r.cancel() }
                    .setOnCancelListener { r.cancel() }.show()
                return true
            }
        }

        w.loadUrl(URL)
    }

    override fun onResume() {
        super.onResume()
        visible = true
        val w = web ?: return
        if ((w.url ?: "").startsWith("file:") && online()) w.loadUrl(URL)
    }

    override fun onPause() {
        visible = false
        super.onPause()
    }

    override fun onNewIntent(i: Intent?) {
        super.onNewIntent(i)
        setIntent(i)
        pendingQ = i?.getStringExtra("q")
        if (loaded) runPending()
    }

    // Suzuvchi tugmadan kelgan matnni Edi chatiga yuboradi
    private fun runPending() {
        val q = pendingQ ?: return
        pendingQ = null
        Handler(Looper.getMainLooper()).postDelayed({
            web?.evaluateJavascript("window.ediVoice&&window.ediVoice(" + JSONObject.quote(q) + ")", null)
        }, 1200L)
    }

    fun startListen() {
        try {
            val i = Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH)
                .putExtra(RecognizerIntent.EXTRA_LANGUAGE_MODEL, RecognizerIntent.LANGUAGE_MODEL_FREE_FORM)
                .putExtra(RecognizerIntent.EXTRA_LANGUAGE, "uz-UZ")
                .putExtra(RecognizerIntent.EXTRA_PROMPT, "Buyruq ayting")
            startActivityForResult(i, RC_VOICE)
        } catch (e: Exception) {
            Toast.makeText(this, "Ovoz tanish xizmati topilmadi", Toast.LENGTH_LONG).show()
        }
    }

    override fun onActivityResult(rc: Int, res: Int, data: Intent?) {
        super.onActivityResult(rc, res, data)
        if (rc == RC_FILE) {
            fileCb?.onReceiveValue(WebChromeClient.FileChooserParams.parseResult(res, data))
            fileCb = null
        } else if (rc == RC_VOICE && res == RESULT_OK) {
            val t = data?.getStringArrayListExtra(RecognizerIntent.EXTRA_RESULTS)?.firstOrNull()
            if (!t.isNullOrBlank()) {
                web?.evaluateJavascript("window.ediVoice&&window.ediVoice(" + JSONObject.quote(t) + ")", null)
            }
        }
    }

    override fun onRequestPermissionsResult(code: Int, perms: Array<out String>, res: IntArray) {
        super.onRequestPermissionsResult(code, perms, res)
        val ok = res.isNotEmpty() && res.all { it == PackageManager.PERMISSION_GRANTED }
        when (code) {
            RC_WEBPERM -> {
                val r = pendingWeb
                pendingWeb = null
                if (r != null) { if (ok) r.grant(r.resources) else r.deny() }
            }
            RC_GEO -> {
                val cb = pendingGeoCb
                val o = pendingGeoOrigin
                pendingGeoCb = null
                pendingGeoOrigin = null
                if (cb != null && o != null) cb.invoke(o, ok, false)
            }
            else -> bridge.permResult(code, res)
        }
    }

    @Deprecated("Deprecated in Java")
    override fun onBackPressed() {
        val w = web
        if (w == null) { super.onBackPressed(); return }
        w.evaluateJavascript(CLOSE_JS) { r ->
            if (r != "1") {
                if (w.canGoBack()) w.goBack() else moveTaskToBack(true)
            }
        }
    }

    override fun onDestroy() {
        web?.destroy()
        web = null
        super.onDestroy()
    }
}
'''

F[KT + 'Bridge.kt'] = r'''package com.lutfullo.edi

import android.accessibilityservice.AccessibilityService
import android.app.ActivityManager
import android.app.AlertDialog
import android.app.Notification
import android.app.NotificationManager
import android.app.PendingIntent
import android.content.ContentUris
import android.content.ContentValues
import android.content.Context
import android.content.Intent
import android.content.pm.PackageInstaller
import android.content.pm.PackageManager
import android.hardware.camera2.CameraCharacteristics
import android.hardware.camera2.CameraManager
import android.media.AudioAttributes
import android.media.AudioManager
import android.media.MediaPlayer
import android.net.Uri
import android.os.BatteryManager
import android.os.Build
import android.os.Environment
import android.os.Handler
import android.os.Looper
import android.provider.AlarmClock
import android.provider.ContactsContract
import android.provider.MediaStore
import android.provider.Settings
import android.speech.tts.TextToSpeech
import android.telecom.TelecomManager
import android.telephony.SmsManager
import android.util.Base64
import android.view.ContextThemeWrapper
import android.view.KeyEvent
import android.view.WindowManager
import android.webkit.JavascriptInterface
import android.webkit.WebView
import android.widget.Toast
import org.json.JSONObject
import java.io.File
import java.net.HttpURLConnection
import java.net.URL
import java.util.Locale
import java.util.concurrent.CountDownLatch
import java.util.concurrent.TimeUnit
import java.util.concurrent.atomic.AtomicBoolean

class Bridge(base: Context, private val web: WebView, private val activity: MainActivity?) {
    private val ctx: Context = base.applicationContext
    var onBg: ((String, Boolean) -> Unit)? = null
    private val ui = Handler(Looper.getMainLooper())
    private val audio = ctx.getSystemService(Context.AUDIO_SERVICE) as AudioManager
    private val nm = ctx.getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager
    private val rt = HashMap<String, String>()
    private val codes = HashMap<Int, String>()
    private var nextCode = 100

    init {
        rt["camera"] = android.Manifest.permission.CAMERA
        rt["mic"] = android.Manifest.permission.RECORD_AUDIO
        rt["contacts"] = android.Manifest.permission.READ_CONTACTS
        rt["call"] = android.Manifest.permission.CALL_PHONE
        rt["sms"] = android.Manifest.permission.SEND_SMS
        rt["location"] = android.Manifest.permission.ACCESS_FINE_LOCATION
        rt["answercalls"] = android.Manifest.permission.ANSWER_PHONE_CALLS
        rt["audio"] = if (Build.VERSION.SDK_INT >= 33) "android.permission.READ_MEDIA_AUDIO" else android.Manifest.permission.READ_EXTERNAL_STORAGE
        if (Build.VERSION.SDK_INT >= 33) rt["notif"] = "android.permission.POST_NOTIFICATIONS"
    }

    // ------------------------------------------------------------ yordamchilar
    private fun js(code: String) { web.post { web.evaluateJavascript(code, null) } }
    private fun toast(m: String) { ui.post { Toast.makeText(ctx, m, Toast.LENGTH_LONG).show() } }
    private fun start(i: Intent) { i.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK); ctx.startActivity(i) }
    private fun norm(s: String): String = s.lowercase().replace(Regex("[^\\p{L}\\p{N}]"), "")

    private fun confirm(msg: String): Boolean {
        val latch = CountDownLatch(1)
        val ok = AtomicBoolean(false)
        ui.post {
            try {
                val a = activity
                val useAct = a != null && MainActivity.visible && !a.isFinishing
                val b = if (a != null && useAct) AlertDialog.Builder(a) else AlertDialog.Builder(ContextThemeWrapper(ctx, android.R.style.Theme_DeviceDefault_Dialog_Alert))
                val d = b.setMessage(msg)
                    .setPositiveButton("Ha") { _, _ -> ok.set(true); latch.countDown() }
                    .setNegativeButton("Yo'q") { _, _ -> latch.countDown() }
                    .setOnCancelListener { latch.countDown() }
                    .create()
                if (!useAct) d.window?.setType(WindowManager.LayoutParams.TYPE_APPLICATION_OVERLAY)
                d.show()
            } catch (e: Exception) { latch.countDown() }
        }
        latch.await(30, TimeUnit.SECONDS)
        return ok.get()
    }

    // ------------------------------------------------------------ ruxsatlar
    @JavascriptInterface
    fun hasPerm(id: String): Boolean {
        return when (id) {
            "overlay" -> Settings.canDrawOverlays(ctx)
            "writesettings" -> Settings.System.canWrite(ctx)
            "dnd" -> nm.isNotificationPolicyAccessGranted
            "access" -> (Settings.Secure.getString(ctx.contentResolver, Settings.Secure.ENABLED_ACCESSIBILITY_SERVICES) ?: "").contains(ctx.packageName + "/")
            "notiflisten" -> (Settings.Secure.getString(ctx.contentResolver, "enabled_notification_listeners") ?: "").contains(ctx.packageName)
            else -> {
                val p = rt[id]
                if (p == null) true else ctx.checkSelfPermission(p) == PackageManager.PERMISSION_GRANTED
            }
        }
    }

    private fun permJs(id: String, ok: Boolean, blocked: Boolean) {
        js("window.ediPermResult&&window.ediPermResult('" + id + "'," + ok + "," + blocked + ")")
    }

    @JavascriptInterface
    fun askPerm(id: String) {
        ui.post {
            try {
                val sp: String? = when (id) {
                    "overlay" -> Settings.ACTION_MANAGE_OVERLAY_PERMISSION
                    "writesettings" -> Settings.ACTION_MANAGE_WRITE_SETTINGS
                    "dnd" -> Settings.ACTION_NOTIFICATION_POLICY_ACCESS_SETTINGS
                    "access" -> Settings.ACTION_ACCESSIBILITY_SETTINGS
                    "notiflisten" -> Settings.ACTION_NOTIFICATION_LISTENER_SETTINGS
                    else -> null
                }
                if (sp != null) {
                    val i = Intent(sp)
                    if (id == "overlay" || id == "writesettings") i.data = Uri.parse("package:" + ctx.packageName)
                    start(i)
                } else {
                    val p = rt[id]
                    if (p == null) {
                        permJs(id, true, false)
                    } else {
                        val c = nextCode++
                        codes[c] = id
                        val a = activity
                        if (a == null) {
                            toast("🔐 Ruxsat uchun Edi ilovasini oching")
                            permJs(id, false, false)
                        } else {
                            a.requestPermissions(arrayOf(p), c)
                        }
                    }
                }
            } catch (e: Exception) {
                permJs(id, false, false)
            }
        }
    }

    @JavascriptInterface
    fun openAppSettings() {
        ui.post {
            val i = Intent(Settings.ACTION_APPLICATION_DETAILS_SETTINGS, Uri.parse("package:" + ctx.packageName))
            start(i)
        }
    }

    fun permResult(code: Int, res: IntArray) {
        val id = codes.remove(code) ?: return
        val ok = res.isNotEmpty() && res[0] == PackageManager.PERMISSION_GRANTED
        val p = rt[id]
        val a = activity
        val blocked = !ok && p != null && a != null && !a.shouldShowRequestPermissionRationale(p)
        permJs(id, ok, blocked)
    }

    // ------------------------------------------------------------ ilovalar
    @JavascriptInterface
    fun findApp(name: String): String {
        val key = norm(name)
        if (key.isEmpty()) return ""
        val pm = ctx.packageManager
        val list = pm.queryIntentActivities(Intent(Intent.ACTION_MAIN).addCategory(Intent.CATEGORY_LAUNCHER), 0)
        var best = ""
        var bs = 0
        for (ri in list) {
            val label = norm(ri.loadLabel(pm).toString())
            val pk = ri.activityInfo.packageName
            val sc = when {
                label == key -> 3
                label.length >= 3 && (label.startsWith(key) || key.startsWith(label)) -> 2
                key.length >= 3 && label.contains(key) -> 1
                else -> 0
            }
            if (sc > bs) { bs = sc; best = pk }
        }
        return best
    }

    @JavascriptInterface
    fun openApp(pk: String) {
        ui.post {
            val i = ctx.packageManager.getLaunchIntentForPackage(pk)
            try {
                if (i != null) start(i)
                else start(Intent(Intent.ACTION_VIEW, Uri.parse("market://details?id=" + pk)))
            } catch (e: Exception) { toast("❌ Ochilmadi") }
        }
    }

    @JavascriptInterface
    fun clearCache() {
        ui.post {
            web.clearCache(true)
            try { ctx.cacheDir.deleteRecursively() } catch (e: Exception) {}
        }
    }

    @JavascriptInterface
    fun takePhoto() {
        ui.post {
            try { start(Intent(MediaStore.ACTION_IMAGE_CAPTURE)) }
            catch (e: Exception) { toast("❌ Kamera ochilmadi") }
        }
    }

    @JavascriptInterface
    fun overlay() {
        ui.post {
            val i = Intent(Settings.ACTION_MANAGE_OVERLAY_PERMISSION, Uri.parse("package:" + ctx.packageName))
            start(i)
        }
    }

    // ------------------------------------------------------------ ovoz
    private var tts: TextToSpeech? = null
    private var ttsReady = false
    private var pendingSpeech: String? = null

    private fun speakNow(t: String) { tts?.speak(t, TextToSpeech.QUEUE_FLUSH, null, "edi") }

    @JavascriptInterface
    fun speak(text: String) {
        ui.post {
            if (ttsReady) { speakNow(text); return@post }
            pendingSpeech = text
            if (tts == null) {
                tts = TextToSpeech(ctx) { st ->
                    if (st == TextToSpeech.SUCCESS) {
                        val t = tts
                        if (t != null) {
                            var r = t.setLanguage(Locale("uz", "UZ"))
                            if (r < 0) r = t.setLanguage(Locale("tr", "TR"))
                            ttsReady = true
                            val p = pendingSpeech
                            pendingSpeech = null
                            if (p != null) speakNow(p)
                        }
                    }
                }
            }
        }
    }

    @JavascriptInterface
    fun listen() { ui.post { activity?.startListen() } }

    @JavascriptInterface
    fun loop(on: Boolean) {
        ui.post {
            try {
                if (on) {
                    if (ctx.checkSelfPermission(android.Manifest.permission.RECORD_AUDIO) != PackageManager.PERMISSION_GRANTED) {
                        toast("🔐 Mikrofon ruxsati kerak")
                    } else {
                        ctx.startForegroundService(Intent(ctx, ListenService::class.java))
                    }
                } else {
                    ctx.stopService(Intent(ctx, ListenService::class.java))
                }
            } catch (e: Exception) { toast("❌ Tinglash boshlanmadi: " + e.message) }
        }
    }

    // ------------------------------------------------------------ ilova ichidan yangilash
    private val repo = "lutfullossr-creator/Edi"

    @Suppress("DEPRECATION")
    private fun curCode(): Int {
        val pi = ctx.packageManager.getPackageInfo(ctx.packageName, 0)
        return if (Build.VERSION.SDK_INT >= 28) pi.longVersionCode.toInt() else pi.versionCode
    }

    private fun curName(): String {
        return ctx.packageManager.getPackageInfo(ctx.packageName, 0).versionName ?: "?"
    }

    private fun upd(m: String) { js("window.ediUpd&&window.ediUpd(" + JSONObject.quote(m) + ")") }

    // (versiya raqami, teg, apk havolasi)
    private fun latest(): Triple<Int, String, String> {
        val c = URL("https://api.github.com/repos/" + repo + "/releases/latest").openConnection() as HttpURLConnection
        c.connectTimeout = 10000
        c.readTimeout = 15000
        c.setRequestProperty("Accept", "application/vnd.github+json")
        c.setRequestProperty("User-Agent", "EdiApp")
        if (c.responseCode != 200) throw Exception("GitHub javobi: " + c.responseCode)
        val j = JSONObject(c.inputStream.bufferedReader().use { it.readText() })
        val tag = j.optString("tag_name", "")
        val n = Regex("(\\d+)$").find(tag)?.groupValues?.get(1)?.toIntOrNull() ?: 0
        var url = ""
        val arr = j.optJSONArray("assets")
        if (arr != null) {
            for (i in 0 until arr.length()) {
                val a = arr.getJSONObject(i)
                if (a.optString("name").endsWith(".apk")) { url = a.optString("browser_download_url"); break }
            }
        }
        return Triple(n, tag, url)
    }

    private fun download(url: String, f: File) {
        val c = URL(url).openConnection() as HttpURLConnection
        c.connectTimeout = 15000
        c.readTimeout = 30000
        c.setRequestProperty("User-Agent", "EdiApp")
        if (c.responseCode !in 200..299) throw Exception("Yuklab bo'lmadi: " + c.responseCode)
        c.inputStream.use { i -> f.outputStream().use { o -> i.copyTo(o) } }
    }

    private fun install(f: File) {
        val pi = ctx.packageManager.packageInstaller
        val p = PackageInstaller.SessionParams(PackageInstaller.SessionParams.MODE_FULL_INSTALL)
        p.setSize(f.length())
        val id = pi.createSession(p)
        val ses = pi.openSession(id)
        ses.openWrite("edi.apk", 0L, f.length()).use { o ->
            f.inputStream().use { it.copyTo(o) }
            ses.fsync(o)
        }
        val flags = PendingIntent.FLAG_UPDATE_CURRENT or (if (Build.VERSION.SDK_INT >= 31) PendingIntent.FLAG_MUTABLE else 0)
        val pend = PendingIntent.getBroadcast(ctx, id, Intent(ctx, InstallReceiver::class.java), flags)
        ses.commit(pend.intentSender)
        ses.close()
    }

    private fun updateFlow(mode: String) {
        try {
            val l = latest()
            val cur = curCode()
            if (l.first <= cur) {
                if (mode != "auto") upd("✅ Eng so'nggi versiya (" + curName() + ")")
                return
            }
            if (mode != "install") {
                upd("🆕 Yangi versiya: " + l.second + " (hozir " + curName() + "). «ilovani yangila» deb ayting")
                return
            }
            if (l.third.isEmpty()) { upd("❌ Yangi versiyada APK fayl topilmadi"); return }
            if (!confirm("Edi " + l.second + " tayyor. Yuklab o'rnatilsinmi?")) { upd("↩️ Bekor qilindi"); return }
            if (!ctx.packageManager.canRequestPackageInstalls()) {
                start(Intent(Settings.ACTION_MANAGE_UNKNOWN_APP_SOURCES, Uri.parse("package:" + ctx.packageName)))
                upd("🔒 «Shu manbadan o'rnatish»ni yoqing, keyin «ilovani yangila» deb qayta ayting")
                return
            }
            upd("⬇️ Yuklanmoqda…")
            val f = File(ctx.cacheDir, "edi_update.apk")
            download(l.third, f)
            upd("📲 O'rnatish oynasi ochilmoqda…")
            install(f)
        } catch (e: Exception) {
            if (mode != "auto") upd("❌ Yangilash xatosi: " + (e.message ?: "noma'lum"))
        }
    }

    @JavascriptInterface
    fun version(): String = curName()

    @JavascriptInterface
    fun update(mode: String): String {
        Thread { updateFlow(mode) }.start()
        return ""
    }

    // ------------------------------------------------------------ kalit, til, suzuvchi tugma
    @JavascriptInterface
    fun setKey(k: String) { Stt.setKey(ctx, k) }

    @JavascriptInterface
    fun setVoiceLang(l: String) { Stt.setLang(ctx, l) }

    @JavascriptInterface
    fun bgDone(msg: String, isCmd: Boolean) { onBg?.invoke(msg, isCmd) }

    @JavascriptInterface
    fun bubble(on: Boolean): String {
        try {
            if (on) {
                if (!Settings.canDrawOverlays(ctx)) return "🔒 «Boshqa ilovalar ustida» ruxsati yo'q. «ruxsatlar» deb ayting"
                if (ctx.checkSelfPermission(android.Manifest.permission.RECORD_AUDIO) != PackageManager.PERMISSION_GRANTED) return "🔒 Mikrofon ruxsati kerak"
                ctx.startForegroundService(Intent(ctx, BubbleService::class.java))
                ctx.getSharedPreferences("edi", Context.MODE_PRIVATE).edit().putBoolean("bubble_on", true).apply()
                try {
                    val pm = ctx.getSystemService(Context.POWER_SERVICE) as android.os.PowerManager
                    if (!pm.isIgnoringBatteryOptimizations(ctx.packageName))
                        start(Intent(Settings.ACTION_REQUEST_IGNORE_BATTERY_OPTIMIZATIONS, Uri.parse("package:" + ctx.packageName)))
                } catch (e: Exception) {}
                return "🎙 Suzuvchi tugma yoqildi. Bosing va gapiring. Ushlab turib o'chirasiz. Telefon qayta yonganda ham o'zi yoqiladi"
            }
            ctx.getSharedPreferences("edi", Context.MODE_PRIVATE).edit().putBoolean("bubble_on", false).apply()
            ctx.stopService(Intent(ctx, BubbleService::class.java))
            return "🎙 Suzuvchi tugma o'chirildi"
        } catch (e: Exception) {
            return "❌ " + (e.message ?: "xato")
        }
    }

    // ------------------------------------------------------------ fayl saqlash
    @JavascriptInterface
    fun saveFile(name: String, mime: String, b64: String) {
        try {
            val bytes = Base64.decode(b64, Base64.DEFAULT)
            val safe = name.replace(Regex("[\\\\/:*?\"<>|]"), "_")
            if (Build.VERSION.SDK_INT >= 29) {
                val v = ContentValues()
                v.put(MediaStore.Downloads.DISPLAY_NAME, safe)
                v.put(MediaStore.Downloads.MIME_TYPE, mime)
                v.put(MediaStore.Downloads.RELATIVE_PATH, Environment.DIRECTORY_DOWNLOADS)
                val u = ctx.contentResolver.insert(MediaStore.Downloads.EXTERNAL_CONTENT_URI, v) ?: throw Exception("insert")
                ctx.contentResolver.openOutputStream(u)!!.use { it.write(bytes) }
            } else {
                val d = Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_DOWNLOADS)
                d.mkdirs()
                File(d, safe).writeBytes(bytes)
            }
            toast("📥 Yuklandi: Download/" + safe)
        } catch (e: Exception) {
            toast("❌ Saqlanmadi: " + e.message)
        }
    }

    // ------------------------------------------------------------ kontakt, qo'ng'iroq, sms
    private fun contacts(name: String): List<Array<String>> {
        if (ctx.checkSelfPermission(android.Manifest.permission.READ_CONTACTS) != PackageManager.PERMISSION_GRANTED) return emptyList()
        val words = name.lowercase().split(" ").filter { it.length > 1 }
        val ws = if (words.isEmpty()) listOf(name) else words
        val col = ContactsContract.CommonDataKinds.Phone.DISPLAY_NAME
        val sel = ws.joinToString(" AND ") { col + " LIKE ?" }
        val args = ws.map { "%" + it + "%" }.toTypedArray()
        val out = ArrayList<Array<String>>()
        val c = ctx.contentResolver.query(
            ContactsContract.CommonDataKinds.Phone.CONTENT_URI,
            arrayOf(col, ContactsContract.CommonDataKinds.Phone.NUMBER), sel, args, null
        )
        c?.use { while (it.moveToNext() && out.size < 8) out.add(arrayOf(it.getString(0) ?: "", it.getString(1) ?: "")) }
        return out
    }

    private fun call(num: String, who: String): String {
        val clean = num.replace(Regex("[^0-9+*#]"), "")
        if (clean.isEmpty()) return "❌ Raqam noto'g'ri"
        val uri = Uri.fromParts("tel", clean, null)
        if (ctx.checkSelfPermission(android.Manifest.permission.CALL_PHONE) != PackageManager.PERMISSION_GRANTED) {
            start(Intent(Intent.ACTION_DIAL, uri))
            return "📞 Raqam terildi (qo'ng'iroq ruxsati yo'q)"
        }
        if (!confirm("Qo'ng'iroq qilinsinmi?\n" + who + " " + clean)) return "↩️ Bekor qilindi"
        start(Intent(Intent.ACTION_CALL, uri))
        return "📞 Qo'ng'iroq: " + (if (who.isEmpty()) clean else who)
    }

    @Suppress("DEPRECATION")
    private fun sms(arg: String): String {
        val i = arg.indexOf('|')
        val num = (if (i >= 0) arg.substring(0, i) else arg).replace(Regex("[^0-9+]"), "")
        val txt = if (i >= 0) arg.substring(i + 1).trim() else ""
        if (num.isEmpty()) return "❌ Raqam ayting: «sms yoz 998901234567 salom»"
        if (txt.isEmpty()) return "❌ SMS matni bo'sh"
        if (!confirm("SMS yuborilsinmi?\n" + num + "\n" + txt)) return "↩️ Bekor qilindi"
        val sm = if (Build.VERSION.SDK_INT >= 31) ctx.getSystemService(SmsManager::class.java) else SmsManager.getDefault()
        sm.sendMultipartTextMessage(num, null, sm.divideMessage(txt), null, null)
        return "💬 SMS yuborildi: " + num
    }

    // ------------------------------------------------------------ musiqa
    private class Trk(val uri: Uri, val title: String, val artist: String)

    private var mp: MediaPlayer? = null
    private var queue: List<Trk> = emptyList()
    private var qi = 0
    private var shuf = false
    private var rep = false

    private fun musicUi(title: String, playing: Boolean) {
        js("window.ediMusic&&window.ediMusic(" + JSONObject.quote(title) + "," + playing + ")")
    }

    private fun allTracks(): List<Trk> {
        val out = ArrayList<Trk>()
        val base = MediaStore.Audio.Media.EXTERNAL_CONTENT_URI
        val c = ctx.contentResolver.query(
            base,
            arrayOf(MediaStore.Audio.Media._ID, MediaStore.Audio.Media.TITLE, MediaStore.Audio.Media.ARTIST),
            MediaStore.Audio.Media.IS_MUSIC + " != 0", null, MediaStore.Audio.Media.TITLE + " ASC"
        )
        c?.use { while (it.moveToNext()) out.add(Trk(ContentUris.withAppendedId(base, it.getLong(0)), it.getString(1) ?: "", it.getString(2) ?: "")) }
        return out
    }

    private fun playAt(i: Int): String {
        if (queue.isEmpty()) return "🎵 Navbat bo'sh"
        qi = ((i % queue.size) + queue.size) % queue.size
        val t = queue[qi]
        try { mp?.release() } catch (e: Exception) {}
        val p = MediaPlayer()
        p.setAudioAttributes(AudioAttributes.Builder().setUsage(AudioAttributes.USAGE_MEDIA).setContentType(AudioAttributes.CONTENT_TYPE_MUSIC).build())
        p.setDataSource(ctx, t.uri)
        p.setOnCompletionListener {
            try { if (rep) playAt(qi) else playAt(qi + 1) } catch (e: Exception) {}
        }
        p.prepare()
        p.start()
        mp = p
        val who = if (t.artist.isNotEmpty() && t.artist != "<unknown>") " — " + t.artist else ""
        musicUi(t.title + who, true)
        return "🎵 " + t.title + who
    }

    @Synchronized
    private fun music(a: String): String {
        val k = a.substringBefore(":")
        val v = a.substringAfter(":", "").trim()
        val p = mp
        when (k) {
            "online" -> {
                start(Intent(Intent.ACTION_VIEW, Uri.parse("https://www.youtube.com/results?search_query=" + Uri.encode(v))))
                return "🎵 YouTube'da qidirilmoqda: " + v
            }
            "play", "random" -> {
                if (!hasPerm("audio")) return "🔒 Musiqa fayllari ruxsati kerak"
                val all = allTracks()
                if (all.isEmpty()) return "🎵 Telefonda musiqa topilmadi"
                if (k == "random" || v.isEmpty()) { queue = all.shuffled(); return playAt(0) }
                val ws = v.lowercase().split(" ").map { norm(it) }.filter { it.isNotEmpty() }
                val m = all.filter { tr -> val h = norm(tr.title + tr.artist); ws.all { w -> h.contains(w) } }
                if (m.isEmpty()) return "🎵 «" + v + "» telefonda topilmadi. «internetdan top» deb ayting"
                queue = if (shuf) m.shuffled() else m
                return playAt(0)
            }
            "pause" -> { p?.pause(); return "⏸ Pauza" }
            "resume" -> { p?.start(); return "▶️ Davom etmoqda" }
            "toggle" -> {
                if (p == null) return "🎵 Hech narsa ijro etilmayapti"
                if (p.isPlaying) p.pause() else p.start()
                return if (p.isPlaying) "▶️ Davom etmoqda" else "⏸ Pauza"
            }
            "stop" -> {
                try { p?.release() } catch (e: Exception) {}
                mp = null
                musicUi("", false)
                return "⏹ To'xtatildi"
            }
            "next" -> return playAt(qi + 1)
            "prev" -> return playAt(qi - 1)
            "shuffle" -> {
                shuf = !shuf
                if (shuf && queue.isNotEmpty()) queue = queue.shuffled()
                return if (shuf) "🔀 Aralashtirish yoqildi" else "🔀 Aralashtirish o'chdi"
            }
            "repeat" -> { rep = !rep; return if (rep) "🔁 Takrorlash yoqildi" else "🔁 Takrorlash o'chdi" }
            "seek" -> {
                if (p == null) return "🎵 Hech narsa ijro etilmayapti"
                val n = v.toIntOrNull() ?: 10
                p.seekTo((p.currentPosition + n * 1000).coerceIn(0, p.duration))
                return "⏩ " + n + " soniya"
            }
            "now" -> return if (p != null && queue.isNotEmpty()) "🎵 " + queue[qi].title else "🎵 Hech narsa ijro etilmayapti"
            "list" -> return "🎵 Telefonda " + allTracks().size + " ta qo'shiq bor"
        }
        return "❓ Musiqa buyrug'i noma'lum: " + a
    }

    // ------------------------------------------------------------ asosiy buyruqlar
    private fun sys(a: String): String {
        val kk = a.substringBefore(":")
        val v = a.substringAfter(":", "")
        try {
            when (kk) {
                "set" -> {
                    val act = when (v) {
                        "display" -> Settings.ACTION_DISPLAY_SETTINGS
                        "sound" -> Settings.ACTION_SOUND_SETTINGS
                        "apps" -> Settings.ACTION_APPLICATION_SETTINGS
                        "storage" -> Settings.ACTION_INTERNAL_STORAGE_SETTINGS
                        "nfc" -> Settings.ACTION_NFC_SETTINGS
                        "date" -> Settings.ACTION_DATE_SETTINGS
                        "locale" -> Settings.ACTION_LOCALE_SETTINGS
                        "battery" -> "android.intent.action.POWER_USAGE_SUMMARY"
                        "battsaver" -> "android.settings.BATTERY_SAVER_SETTINGS"
                        "security" -> Settings.ACTION_SECURITY_SETTINGS
                        "dev" -> Settings.ACTION_APPLICATION_DEVELOPMENT_SETTINGS
                        "hotspot" -> "android.settings.TETHER_SETTINGS"
                        "cast" -> "android.settings.CAST_SETTINGS"
                        "privacy" -> Settings.ACTION_PRIVACY_SETTINGS
                        "vpn" -> "android.settings.VPN_SETTINGS"
                        "access" -> Settings.ACTION_ACCESSIBILITY_SETTINGS
                        "input" -> Settings.ACTION_INPUT_METHOD_SETTINGS
                        else -> Settings.ACTION_SETTINGS
                    }
                    start(Intent(act)); return "⚙️ Sozlama ochildi"
                }
                "app" -> {
                    val cat = when (v) {
                        "calculator" -> Intent.CATEGORY_APP_CALCULATOR
                        "gallery" -> Intent.CATEGORY_APP_GALLERY
                        "contacts" -> Intent.CATEGORY_APP_CONTACTS
                        "calendar" -> Intent.CATEGORY_APP_CALENDAR
                        "files" -> "android.intent.category.APP_FILES"
                        "mail" -> Intent.CATEGORY_APP_EMAIL
                        "browser" -> Intent.CATEGORY_APP_BROWSER
                        "maps" -> Intent.CATEGORY_APP_MAPS
                        "messages" -> Intent.CATEGORY_APP_MESSAGING
                        "music" -> Intent.CATEGORY_APP_MUSIC
                        else -> ""
                    }
                    when {
                        v == "clock" -> start(Intent(AlarmClock.ACTION_SHOW_ALARMS))
                        v == "camera" -> start(Intent(MediaStore.INTENT_ACTION_STILL_IMAGE_CAMERA))
                        v == "video" -> start(Intent(MediaStore.INTENT_ACTION_VIDEO_CAMERA))
                        v == "calllog" -> start(Intent(Intent.ACTION_VIEW).setType("vnd.android.cursor.dir/calls"))
                        cat.isNotEmpty() -> start(Intent(Intent.ACTION_MAIN).addCategory(cat))
                        else -> return "❓ Noma'lum ilova: " + v
                    }
                    return "🚀 Ochildi"
                }
                "market" -> {
                    try { start(Intent(Intent.ACTION_VIEW, Uri.parse("market://search?q=" + Uri.encode(v)))) }
                    catch (e: Exception) { start(Intent(Intent.ACTION_VIEW, Uri.parse("https://play.google.com/store/search?q=" + Uri.encode(v)))) }
                    return "🛍 Play Market: " + v
                }
                "share" -> {
                    val i = Intent(Intent.ACTION_SEND).setType("text/plain").putExtra(Intent.EXTRA_TEXT, v)
                    start(Intent.createChooser(i, "Edi").addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)); return "📤 Ulashish oynasi ochildi"
                }
                "mail" -> {
                    val p = v.split("|")
                    val i = Intent(Intent.ACTION_SENDTO, Uri.parse("mailto:" + (p.getOrNull(0) ?: "")))
                        .putExtra(Intent.EXTRA_SUBJECT, p.getOrNull(1) ?: "").putExtra(Intent.EXTRA_TEXT, p.getOrNull(2) ?: "")
                    start(i); return "✉️ Xat tayyorlandi"
                }
                "event" -> {
                    val p = v.split("|")
                    val ms = p.getOrNull(1)?.toLongOrNull() ?: (System.currentTimeMillis() + 3600000L)
                    val i = Intent(Intent.ACTION_INSERT).setData(android.provider.CalendarContract.Events.CONTENT_URI)
                        .putExtra("title", p.getOrNull(0) ?: "Edi").putExtra("beginTime", ms).putExtra("endTime", ms + 3600000L)
                    start(i); return "📅 Taqvim: " + (p.getOrNull(0) ?: "")
                }
                "rotate" -> {
                    if (!Settings.System.canWrite(ctx)) return "🔒 «Tizim sozlamalari» ruxsati yo'q. «ruxsatlar» deb ayting"
                    Settings.System.putInt(ctx.contentResolver, Settings.System.ACCELEROMETER_ROTATION, if (v == "1") 1 else 0)
                    return if (v == "1") "🔄 Avto-burilish yoqildi" else "🔒 Burilish qulflandi"
                }
                "timeout" -> {
                    if (!Settings.System.canWrite(ctx)) return "🔒 «Tizim sozlamalari» ruxsati yo'q. «ruxsatlar» deb ayting"
                    val sec = (v.toIntOrNull() ?: 60).coerceIn(15, 1800)
                    Settings.System.putInt(ctx.contentResolver, Settings.System.SCREEN_OFF_TIMEOUT, sec * 1000)
                    return "⏱ Ekran " + sec + " soniyada o'chadi"
                }
                "battopt" -> {
                    val pm = ctx.getSystemService(Context.POWER_SERVICE) as android.os.PowerManager
                    if (pm.isIgnoringBatteryOptimizations(ctx.packageName)) return "🔋 Fonda ishlash allaqachon ruxsat etilgan"
                    start(Intent(Settings.ACTION_REQUEST_IGNORE_BATTERY_OPTIMIZATIONS, Uri.parse("package:" + ctx.packageName)))
                    return "🔋 «Ruxsat berish» ni bosing"
                }
                "bgstatus" -> {
                    val pm = ctx.getSystemService(Context.POWER_SERVICE) as android.os.PowerManager
                    val ov = Settings.canDrawOverlays(ctx)
                    val bt = pm.isIgnoringBatteryOptimizations(ctx.packageName)
                    val ac = EdiAccessibility.inst != null
                    val bb = ctx.getSharedPreferences("edi", Context.MODE_PRIVATE).getBoolean("bubble_on", false)
                    return "📡 Fon holati\n" + (if (ov) "✅" else "❌") + " Ilovalar ustida ko'rinish\n" + (if (bt) "✅" else "❌") + " Batareya cheklovisiz\n" +
                        (if (ac) "✅" else "❌") + " Maxsus imkoniyatlar\n" + (if (bb) "✅" else "❌") + " Suzuvchi tugma yoqiq (qayta yonganda ham)"
                }
                "ring" -> {
                    val m = when (v) { "0" -> AudioManager.RINGER_MODE_SILENT; "1" -> AudioManager.RINGER_MODE_VIBRATE; else -> AudioManager.RINGER_MODE_NORMAL }
                    try { audio.ringerMode = m } catch (e: SecurityException) { return "🔒 «Bezovta qilmang» ruxsati kerak. «ruxsatlar» deb ayting" }
                    return when (v) { "0" -> "🔕 Jim rejim"; "1" -> "📳 Tebranish rejimi"; else -> "🔔 Oddiy rejim" }
                }
                "stream" -> {
                    val p = v.split(":")
                    val st = when (p[0]) { "ring" -> AudioManager.STREAM_RING; "alarm" -> AudioManager.STREAM_ALARM; "call" -> AudioManager.STREAM_VOICE_CALL; else -> AudioManager.STREAM_NOTIFICATION }
                    val mx = audio.getStreamMaxVolume(st)
                    val pct = (p.getOrNull(1)?.toIntOrNull() ?: 50).coerceIn(0, 100)
                    try { audio.setStreamVolume(st, mx * pct / 100, AudioManager.FLAG_SHOW_UI) } catch (e: SecurityException) { return "🔒 «Bezovta qilmang» ruxsati kerak" }
                    return "🔊 " + p[0] + " ovozi " + pct + "%"
                }
                "wake" -> {
                    val pm = ctx.getSystemService(Context.POWER_SERVICE) as android.os.PowerManager
                    @Suppress("DEPRECATION")
                    val wl = pm.newWakeLock(android.os.PowerManager.FULL_WAKE_LOCK or android.os.PowerManager.ACQUIRE_CAUSES_WAKEUP, "edi:wake")
                    wl.acquire(4000)
                    return "💡 Ekran yoqildi"
                }
                "notifclear" -> {
                    val n = EdiNotifListener.inst ?: return "🔒 «Bildirishnomalarni o'qish» ruxsati yo'q. «ruxsatlar» deb ayting"
                    n.cancelAllNotifications(); return "🧹 Bildirishnomalar tozalandi"
                }
                "split" -> return global(AccessibilityService.GLOBAL_ACTION_TOGGLE_SPLIT_SCREEN, "◫ Ekran bo'lindi")
                "addcontact" -> {
                    val p = v.split("|")
                    val i = Intent(Intent.ACTION_INSERT, ContactsContract.Contacts.CONTENT_URI)
                        .putExtra(ContactsContract.Intents.Insert.NAME, p.getOrNull(0) ?: "")
                        .putExtra(ContactsContract.Intents.Insert.PHONE, p.getOrNull(1) ?: "")
                    start(i); return "👤 Kontakt qo'shish oynasi ochildi"
                }
                "alarmoff" -> {
                    val i = Intent(AlarmClock.ACTION_DISMISS_ALARM).putExtra(AlarmClock.EXTRA_ALARM_SEARCH_MODE, AlarmClock.ALARM_SEARCH_MODE_NEXT)
                    start(i); return "⏰ Budilnik bekor qilindi"
                }
                "timeroff" -> { start(Intent(AlarmClock.ACTION_DISMISS_TIMER)); return "⏳ Taymer bekor qilindi" }
                "ussd" -> { start(Intent(Intent.ACTION_DIAL, Uri.parse("tel:" + Uri.encode(v)))); return "☎️ Raqam terildi: " + v }
                "info" -> {
                    val am = ctx.getSystemService(Context.ACTIVITY_SERVICE) as android.app.ActivityManager
                    val mi = android.app.ActivityManager.MemoryInfo(); am.getMemoryInfo(mi)
                    val st = android.os.StatFs(Environment.getDataDirectory().path)
                    val free = st.availableBytes / 1073741824.0; val tot = st.totalBytes / 1073741824.0
                    return "📱 " + Build.MANUFACTURER + " " + Build.MODEL + ", Android " + Build.VERSION.RELEASE +
                        "\n🧠 RAM bo'sh: " + (mi.availMem / 1048576) + " / " + (mi.totalMem / 1048576) + " MB" +
                        "\n💾 Xotira bo'sh: " + String.format("%.1f", free) + " / " + String.format("%.1f", tot) + " GB"
                }
            }
        } catch (e: Exception) { return "❌ " + (e.message ?: e.javaClass.simpleName) }
        return "❓ Noma'lum sys: " + a
    }

    private fun global(action: Int, ok: String): String {
        val s = EdiAccessibility.inst ?: return "🔒 «Maxsus imkoniyatlar» yoqilmagan. «ruxsatlar» deb ayting"
        return if (s.performGlobalAction(action)) ok else "❌ Bajarilmadi"
    }

    @JavascriptInterface
    fun act(n: String, a: String): String {
        return try { runCmd(n, a) } catch (e: Exception) { "❌ " + (e.message ?: e.javaClass.simpleName) }
    }

    private fun runCmd(n: String, a: String): String {
        when (n) {
            "flash" -> {
                val cm = ctx.getSystemService(Context.CAMERA_SERVICE) as CameraManager
                val id = cm.cameraIdList.firstOrNull { cm.getCameraCharacteristics(it).get(CameraCharacteristics.FLASH_INFO_AVAILABLE) == true }
                    ?: return "❌ Fonar topilmadi"
                cm.setTorchMode(id, a == "1")
                return if (a == "1") "🔦 Fonar yoqildi" else "🔦 Fonar o'chdi"
            }
            "vol" -> {
                val mx = audio.getStreamMaxVolume(AudioManager.STREAM_MUSIC)
                if (a == "up") audio.adjustStreamVolume(AudioManager.STREAM_MUSIC, AudioManager.ADJUST_RAISE, AudioManager.FLAG_SHOW_UI)
                else if (a == "down") audio.adjustStreamVolume(AudioManager.STREAM_MUSIC, AudioManager.ADJUST_LOWER, AudioManager.FLAG_SHOW_UI)
                else if (a.startsWith("set:")) {
                    val pct = (a.substring(4).toIntOrNull() ?: 50).coerceIn(0, 100)
                    audio.setStreamVolume(AudioManager.STREAM_MUSIC, mx * pct / 100, AudioManager.FLAG_SHOW_UI)
                }
                return "🔊 Ovoz: " + (audio.getStreamVolume(AudioManager.STREAM_MUSIC) * 100 / mx) + "%"
            }
            "mute" -> {
                audio.adjustStreamVolume(AudioManager.STREAM_MUSIC, if (a == "1") AudioManager.ADJUST_MUTE else AudioManager.ADJUST_UNMUTE, AudioManager.FLAG_SHOW_UI)
                return if (a == "1") "🔇 Ovoz o'chirildi" else "🔊 Ovoz yoqildi"
            }
            "settings" -> {
                val act = when (a) {
                    "wifi" -> if (Build.VERSION.SDK_INT >= 29) Settings.Panel.ACTION_INTERNET_CONNECTIVITY else Settings.ACTION_WIFI_SETTINGS
                    "bt" -> Settings.ACTION_BLUETOOTH_SETTINGS
                    "airplane" -> Settings.ACTION_AIRPLANE_MODE_SETTINGS
                    "data" -> Settings.ACTION_WIRELESS_SETTINGS
                    "gps" -> Settings.ACTION_LOCATION_SOURCE_SETTINGS
                    else -> Settings.ACTION_SETTINGS
                }
                start(Intent(act))
                return "⚙️ Sozlamalar ochildi (Android o'zi yoqib-o'chirishga ruxsat bermaydi)"
            }
            "battery" -> {
                val bm = ctx.getSystemService(Context.BATTERY_SERVICE) as BatteryManager
                val p = bm.getIntProperty(BatteryManager.BATTERY_PROPERTY_CAPACITY)
                return "🔋 Batareya: " + p + "%" + (if (bm.isCharging) " (zaryadlanmoqda)" else "")
            }
            "home" -> { start(Intent(Intent.ACTION_MAIN).addCategory(Intent.CATEGORY_HOME)); return "🏠 Bosh ekran" }
            "alarm" -> {
                val hm = a.split(":")
                val h = hm[0].trim().toInt()
                val m = if (hm.size > 1) hm[1].trim().toInt() else 0
                start(Intent(AlarmClock.ACTION_SET_ALARM)
                    .putExtra(AlarmClock.EXTRA_HOUR, h).putExtra(AlarmClock.EXTRA_MINUTES, m)
                    .putExtra(AlarmClock.EXTRA_MESSAGE, "Edi").putExtra(AlarmClock.EXTRA_SKIP_UI, true))
                return "⏰ Budilnik: " + String.format("%02d:%02d", h, m)
            }
            "timer" -> {
                val sec = a.trim().toInt()
                start(Intent(AlarmClock.ACTION_SET_TIMER)
                    .putExtra(AlarmClock.EXTRA_LENGTH, sec).putExtra(AlarmClock.EXTRA_SKIP_UI, true))
                return "⏳ Taymer: " + (if (sec >= 60) (sec / 60).toString() + " daqiqa" else sec.toString() + " soniya")
            }
            "search" -> {
                start(Intent(Intent.ACTION_VIEW, Uri.parse("https://www.google.com/search?q=" + Uri.encode(a))))
                return "🔎 Qidirilmoqda: " + a
            }
            "media" -> {
                val code = when (a) {
                    "next" -> KeyEvent.KEYCODE_MEDIA_NEXT
                    "prev" -> KeyEvent.KEYCODE_MEDIA_PREVIOUS
                    else -> KeyEvent.KEYCODE_MEDIA_PLAY_PAUSE
                }
                audio.dispatchMediaKeyEvent(KeyEvent(KeyEvent.ACTION_DOWN, code))
                audio.dispatchMediaKeyEvent(KeyEvent(KeyEvent.ACTION_UP, code))
                return "🎵 Bajarildi"
            }
            "nav" -> {
                if (a.isBlank()) return "Qayerga borasiz?"
                try { start(Intent(Intent.ACTION_VIEW, Uri.parse("google.navigation:q=" + Uri.encode(a)))) }
                catch (e: Exception) { start(Intent(Intent.ACTION_VIEW, Uri.parse("geo:0,0?q=" + Uri.encode(a)))) }
                return "🧭 Yo'l: " + a
            }
            "dial" -> return call(a, "")
            "callname" -> {
                val r = contacts(a)
                if (r.isEmpty()) return "❌ Kontakt topilmadi: " + a
                return call(r[0][1], r[0][0])
            }
            "contact" -> {
                val r = contacts(a)
                if (r.isEmpty()) return "❌ Kontakt topilmadi: " + a
                return "📇 " + r.take(5).joinToString("\n") { it[0] + ": " + it[1] }
            }
            "sms" -> return sms(a)
            "open" -> {
                val pk = findApp(a)
                if (pk.isEmpty()) return "❌ Ilova topilmadi: " + a
                val i = ctx.packageManager.getLaunchIntentForPackage(pk) ?: return "❌ Ochib bo'lmadi"
                start(i)
                return "🚀 Ochildi: " + a
            }
            "shot" -> {
                if (Build.VERSION.SDK_INT < 28) return "⚠️ Skrinshot uchun Android 9+ kerak"
                return global(AccessibilityService.GLOBAL_ACTION_TAKE_SCREENSHOT, "📸 Skrinshot olindi")
            }
            "lock" -> {
                if (Build.VERSION.SDK_INT < 28) return "⚠️ Qulflash uchun Android 9+ kerak"
                return global(AccessibilityService.GLOBAL_ACTION_LOCK_SCREEN, "🔒 Ekran qulflandi")
            }
            "back" -> return global(AccessibilityService.GLOBAL_ACTION_BACK, "◀️ Orqaga")
            "recents" -> return global(AccessibilityService.GLOBAL_ACTION_RECENTS, "🗂 So'nggi ilovalar")
            "shade" -> return global(AccessibilityService.GLOBAL_ACTION_NOTIFICATIONS, "🔔 Bildirishnoma paneli")
            "notifs" -> {
                val l = EdiNotifListener.inst ?: return "🔒 «Bildirishnomalarga kirish» yoqilmagan. «ruxsatlar» deb ayting"
                val pm = ctx.packageManager
                val items = ArrayList<String>()
                for (sbn in l.activeNotifications) {
                    if (items.size >= 8) break
                    val ex = sbn.notification.extras
                    val title = ex.getCharSequence(Notification.EXTRA_TITLE)?.toString() ?: ""
                    val text = ex.getCharSequence(Notification.EXTRA_TEXT)?.toString() ?: ""
                    if (title.isEmpty() && text.isEmpty()) continue
                    val app = try { pm.getApplicationLabel(pm.getApplicationInfo(sbn.packageName, 0)).toString() } catch (e: Exception) { sbn.packageName }
                    items.add(app + ": " + title + (if (text.isNotEmpty()) " — " + text else ""))
                }
                return if (items.isEmpty()) "🔔 Yangi bildirishnoma yo'q" else "🔔 Bildirishnomalar:\n" + items.joinToString("\n")
            }
            "answer" -> {
                val tm = ctx.getSystemService(Context.TELECOM_SERVICE) as TelecomManager
                tm.acceptRingingCall()
                return "📞 Qo'ng'iroqqa javob berildi"
            }
            "reject" -> {
                if (Build.VERSION.SDK_INT < 28) return "⚠️ Rad etish uchun Android 9+ kerak"
                val tm = ctx.getSystemService(Context.TELECOM_SERVICE) as TelecomManager
                return if (tm.endCall()) "📵 Qo'ng'iroq rad etildi" else "❌ Faol qo'ng'iroq yo'q"
            }
            "bright" -> {
                if (!Settings.System.canWrite(ctx)) return "🔒 «Tizim sozlamalari» ruxsati yo'q. «ruxsatlar» deb ayting"
                val cr = ctx.contentResolver
                Settings.System.putInt(cr, Settings.System.SCREEN_BRIGHTNESS_MODE, Settings.System.SCREEN_BRIGHTNESS_MODE_MANUAL)
                val cur = Settings.System.getInt(cr, Settings.System.SCREEN_BRIGHTNESS, 128)
                val v = (if (a.startsWith("set:")) (a.substring(4).toIntOrNull() ?: 50) * 255 / 100 else if (a == "up") cur + 38 else cur - 38).coerceIn(5, 255)
                Settings.System.putInt(cr, Settings.System.SCREEN_BRIGHTNESS, v)
                return "☀️ Yorqinlik: " + (v * 100 / 255) + "%"
            }
            "dnd" -> {
                if (!nm.isNotificationPolicyAccessGranted) return "🔒 «Bezovta qilmaslik» ruxsati yo'q. «ruxsatlar» deb ayting"
                nm.setInterruptionFilter(if (a == "1") NotificationManager.INTERRUPTION_FILTER_NONE else NotificationManager.INTERRUPTION_FILTER_ALL)
                return if (a == "1") "🔕 Bezovta qilmaslik yoqildi" else "🔔 Bezovta qilmaslik o'chdi"
            }
            "kill" -> {
                val pk = findApp(a)
                if (pk.isEmpty()) return "❌ Ilova topilmadi: " + a
                (ctx.getSystemService(Context.ACTIVITY_SERVICE) as ActivityManager).killBackgroundProcesses(pk)
                return "🛑 To'xtatildi: " + a
            }
            "uninstall" -> {
                val pk = findApp(a)
                if (pk.isEmpty()) return "❌ Ilova topilmadi: " + a
                start(Intent(Intent.ACTION_DELETE, Uri.parse("package:" + pk)))
                return "🗑 O'chirish oynasi ochildi: " + a
            }
            "music" -> return music(a)
            "sys" -> return sys(a)
            "url" -> { start(Intent(Intent.ACTION_VIEW, Uri.parse(a))); return "🔗 Ochildi" }
            "click", "scroll", "swipe", "type", "cleartext", "enter", "screentext", "power", "qs", "longpress", "tappct", "edit" -> {
                val s = EdiAccessibility.inst ?: return "🔒 «Maxsus imkoniyatlar» yoqilmagan. «ruxsatlar» deb ayting"
                return when (n) {
                    "click" -> s.clickText(a)
                    "scroll" -> s.scroll(a)
                    "swipe" -> s.swipe(a)
                    "type" -> s.typeText(a)
                    "cleartext" -> s.clearText()
                    "enter" -> s.enter()
                    "screentext" -> s.screenText()
                    "longpress" -> s.longPress(a)
                    "tappct" -> s.tapPct(a)
                    "edit" -> s.edit(a)
                    "power" -> global(AccessibilityService.GLOBAL_ACTION_POWER_DIALOG, "⏻ Quvvat menyusi")
                    else -> if (Build.VERSION.SDK_INT >= 31) global(AccessibilityService.GLOBAL_ACTION_QUICK_SETTINGS, "⚙️ Tezkor sozlamalar") else "⚠️ Android 12+ kerak"
                }
            }
        }
        return "❓ Noma'lum buyruq: " + n
    }
}
'''

F[KT + 'Stt.kt'] = r'''package com.lutfullo.edi

import android.content.Context
import org.json.JSONObject
import java.io.DataOutputStream
import java.io.File
import java.net.HttpURLConnection
import java.net.URL

object Stt {
    const val PROMPT = "Edi, fonar yoq, musiqa qo'y, ovozni balandla, ilovani och, qo'ng'iroq qil, sms yoz, skrinshot ol, yorqinlik, kontakt top, tarjima qil."

    private fun sp(c: Context) = c.getSharedPreferences("edi", Context.MODE_PRIVATE)
    fun key(c: Context): String = sp(c).getString("qk", "") ?: ""
    fun setKey(c: Context, k: String) { sp(c).edit().putString("qk", k).apply() }
    fun lang(c: Context): String = sp(c).getString("vl", "uz") ?: "uz"
    fun setLang(c: Context, l: String) { sp(c).edit().putString("vl", l).apply() }

    // Groq Whisper: ovozni matnga aylantiradi (fon oqimida chaqiring)
    fun whisper(key: String, f: File, lang: String): String {
        var err = "noma'lum xato"
        for (model in arrayOf("whisper-large-v3", "whisper-large-v3-turbo")) {
            try {
                val b = "----edi" + System.currentTimeMillis()
                val c = URL("https://api.groq.com/openai/v1/audio/transcriptions").openConnection() as HttpURLConnection
                c.requestMethod = "POST"
                c.doOutput = true
                c.connectTimeout = 15000
                c.readTimeout = 40000
                c.setRequestProperty("Authorization", "Bearer " + key)
                c.setRequestProperty("Content-Type", "multipart/form-data; boundary=" + b)
                val o = DataOutputStream(c.outputStream)
                fun w(s: String) { o.write(s.toByteArray(Charsets.UTF_8)) }
                fun part(n: String, v: String) {
                    w("--" + b + "\r\nContent-Disposition: form-data; name=\"" + n + "\"\r\n\r\n" + v + "\r\n")
                }
                part("model", model)
                part("response_format", "json")
                part("temperature", "0")
                if (lang != "auto") part("language", lang)
                if (lang == "uz" || lang == "auto") part("prompt", PROMPT)
                w("--" + b + "\r\nContent-Disposition: form-data; name=\"file\"; filename=\"cmd.m4a\"\r\nContent-Type: audio/mp4\r\n\r\n")
                o.write(f.readBytes())
                w("\r\n--" + b + "--\r\n")
                o.flush()
                o.close()
                val code = c.responseCode
                val stream = if (code in 200..299) c.inputStream else c.errorStream
                val body = if (stream != null) stream.bufferedReader().use { it.readText() } else ""
                if (code in 200..299) return JSONObject(body).optString("text", "").trim()
                if (code == 401) { err = "Groq kaliti noto'g'ri"; break }
                err = "HTTP " + code + (if (code == 429) " (limit tugadi, biroz kuting)" else "")
            } catch (e: Exception) {
                err = e.message ?: "tarmoq xatosi"
            }
        }
        throw Exception(err)
    }
}
'''

F[KT + 'Rec.kt'] = r'''package com.lutfullo.edi

import android.content.Context
import android.media.MediaRecorder
import android.os.Build
import android.os.Handler
import java.io.File

// Ovozni yozadi va jim qolganda o'zi to'xtaydi
class Rec(private val ctx: Context, private val h: Handler, private val f: File, private val done: (Boolean) -> Unit) {
    private var mr: MediaRecorder? = null
    private var t0 = 0L
    private var lastVoice = 0L
    private var heard = false
    private var base = 0
    private var n = 0

    private val poll = object : Runnable {
        override fun run() {
            val m = mr ?: return
            val amp = try { m.maxAmplitude } catch (e: Exception) { 0 }
            val now = System.currentTimeMillis()
            val el = now - t0
            if (el < 500) {
                base += amp
                n += 1
            } else {
                val th = Math.max(1500, (base / Math.max(n, 1)) * 3)
                if (amp > th) { heard = true; lastVoice = now }
            }
            if ((heard && now - lastVoice > 1300) || el > 15000 || (!heard && el > 7000)) { finish(); return }
            h.postDelayed(this, 120L)
        }
    }

    @Suppress("DEPRECATION")
    fun start(): Boolean {
        return try {
            val r = if (Build.VERSION.SDK_INT >= 31) MediaRecorder(ctx) else MediaRecorder()
            r.setAudioSource(MediaRecorder.AudioSource.VOICE_RECOGNITION)
            r.setOutputFormat(MediaRecorder.OutputFormat.MPEG_4)
            r.setAudioEncoder(MediaRecorder.AudioEncoder.AAC)
            r.setAudioSamplingRate(16000)
            r.setAudioEncodingBitRate(64000)
            r.setAudioChannels(1)
            r.setOutputFile(f.absolutePath)
            r.prepare()
            r.start()
            mr = r
            t0 = System.currentTimeMillis()
            h.postDelayed(poll, 150L)
            true
        } catch (e: Exception) {
            false
        }
    }

    fun cancel() {
        h.removeCallbacks(poll)
        try { mr?.release() } catch (e: Exception) {}
        mr = null
    }

    private fun finish() {
        val r = mr ?: return
        mr = null
        var ok = heard
        try { r.stop() } catch (e: Exception) { ok = false }
        try { r.release() } catch (e: Exception) {}
        done(ok && f.length() > 800L)
    }
}
'''

F[KT + 'BubbleService.kt'] = r'''package com.lutfullo.edi

import android.Manifest
import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.app.Service
import android.content.Intent
import android.content.pm.PackageManager
import android.content.pm.ServiceInfo
import android.graphics.Color
import android.graphics.PixelFormat
import android.graphics.drawable.GradientDrawable
import android.os.Build
import android.os.Bundle
import android.os.Handler
import android.os.IBinder
import android.os.Looper
import android.provider.Settings
import android.speech.RecognitionListener
import android.speech.RecognizerIntent
import android.speech.SpeechRecognizer
import android.view.Gravity
import android.view.MotionEvent
import android.view.View
import android.view.WindowManager
import android.webkit.WebSettings
import android.webkit.WebView
import android.webkit.WebViewClient
import android.widget.LinearLayout
import android.widget.TextView
import org.json.JSONObject
import java.io.File

// Boshqa ilovalar ustida suzuvchi mikrofon tugmasi + fon dvigateli (yashirin WebView)
class BubbleService : Service() {
    companion object {
        @Volatile var engine: WebView? = null
    }

    private lateinit var wm: WindowManager
    private var root: LinearLayout? = null
    private var btn: TextView? = null
    private var msg: TextView? = null
    private val h = Handler(Looper.getMainLooper())
    private var busy = false
    private var rec: Rec? = null
    private var sr: SpeechRecognizer? = null
    private var guard: Runnable? = null
    private var pendingText = ""
    private val hideR = Runnable { msg?.visibility = View.GONE }

    override fun onBind(i: Intent?): IBinder? = null

    override fun onCreate() {
        super.onCreate()
        wm = getSystemService(WINDOW_SERVICE) as WindowManager
    }

    private fun dp(v: Int): Int = (v * resources.displayMetrics.density).toInt()

    override fun onStartCommand(i: Intent?, f: Int, id: Int): Int {
        startFg()
        if (!Settings.canDrawOverlays(this)) { stopSelf(); return START_NOT_STICKY }
        if (root == null) {
            buildEngine()
            buildBubble()
        }
        return START_STICKY
    }

    private fun upgradeMic() {
        try {
            val pm = getSystemService(POWER_SERVICE) as android.os.PowerManager
            pm.newWakeLock(android.os.PowerManager.PARTIAL_WAKE_LOCK, "edi:cmd").acquire(60000)
        } catch (e: Exception) {}
        try {
            if (Build.VERSION.SDK_INT >= 30) {
                val n = Notification.Builder(this, "edi_bubble")
                    .setContentTitle("Edi tinglayapti")
                    .setSmallIcon(android.R.drawable.ic_btn_speak_now)
                    .setOngoing(true)
                    .build()
                startForeground(78, n, ServiceInfo.FOREGROUND_SERVICE_TYPE_SPECIAL_USE or ServiceInfo.FOREGROUND_SERVICE_TYPE_MICROPHONE)
            }
        } catch (e: Exception) {}
    }

    private fun startFg() {
        val nm = getSystemService(NotificationManager::class.java)
        nm.createNotificationChannel(NotificationChannel("edi_bubble", "Edi suzuvchi tugma", NotificationManager.IMPORTANCE_LOW))
        val pi = PendingIntent.getActivity(this, 1, Intent(this, MainActivity::class.java), PendingIntent.FLAG_IMMUTABLE)
        val n = Notification.Builder(this, "edi_bubble")
            .setContentTitle("Edi suzuvchi tugma yoqilgan")
            .setContentText("Tugmani ushlab turib o'chirasiz")
            .setSmallIcon(android.R.drawable.ic_btn_speak_now)
            .setContentIntent(pi)
            .setOngoing(true)
            .build()
        if (Build.VERSION.SDK_INT >= 34) startForeground(78, n, ServiceInfo.FOREGROUND_SERVICE_TYPE_SPECIAL_USE)
        else startForeground(78, n)
    }

    private fun buildEngine() {
        val w = WebView(applicationContext)
        val s = w.settings
        s.javaScriptEnabled = true
        s.domStorageEnabled = true
        s.databaseEnabled = true
        s.mediaPlaybackRequiresUserGesture = false
        s.cacheMode = WebSettings.LOAD_DEFAULT
        val b = Bridge(applicationContext, w, null)
        b.onBg = { m, c -> h.post { onResult(m, c) } }
        w.addJavascriptInterface(b, "Android")
        w.webViewClient = WebViewClient()
        val lp = WindowManager.LayoutParams(
            1, 1, WindowManager.LayoutParams.TYPE_APPLICATION_OVERLAY,
            WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE or WindowManager.LayoutParams.FLAG_NOT_TOUCHABLE,
            PixelFormat.TRANSLUCENT
        )
        lp.gravity = Gravity.TOP or Gravity.START
        wm.addView(w, lp)
        w.loadUrl(MainActivity.URL + "?bg=1")
        engine = w
    }

    private fun buildBubble() {
        val col = LinearLayout(this)
        col.orientation = LinearLayout.VERTICAL
        col.gravity = Gravity.CENTER_HORIZONTAL

        val t = TextView(this)
        t.text = "🎙"
        t.textSize = 24f
        t.gravity = Gravity.CENTER
        val bg = GradientDrawable()
        bg.shape = GradientDrawable.OVAL
        bg.setColor(Color.parseColor("#2563EB"))
        bg.setStroke(dp(2), Color.WHITE)
        t.background = bg
        col.addView(t, LinearLayout.LayoutParams(dp(56), dp(56)))

        val m = TextView(this)
        m.setTextColor(Color.WHITE)
        m.textSize = 13f
        m.setPadding(dp(10), dp(6), dp(10), dp(6))
        m.maxWidth = dp(260)
        val mb = GradientDrawable()
        mb.cornerRadius = dp(12).toFloat()
        mb.setColor(Color.parseColor("#E6111111"))
        m.background = mb
        m.visibility = View.GONE
        val mlp = LinearLayout.LayoutParams(LinearLayout.LayoutParams.WRAP_CONTENT, LinearLayout.LayoutParams.WRAP_CONTENT)
        mlp.topMargin = dp(6)
        col.addView(m, mlp)

        val lp = WindowManager.LayoutParams(
            WindowManager.LayoutParams.WRAP_CONTENT, WindowManager.LayoutParams.WRAP_CONTENT,
            WindowManager.LayoutParams.TYPE_APPLICATION_OVERLAY,
            WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE,
            PixelFormat.TRANSLUCENT
        )
        lp.gravity = Gravity.TOP or Gravity.START
        lp.x = dp(12)
        lp.y = dp(220)

        t.setOnTouchListener(object : View.OnTouchListener {
            var sx = 0
            var sy = 0
            var tx = 0f
            var ty = 0f
            var moved = false
            var closed = false
            val lpr = Runnable {
                if (!moved) { closed = true; stopSelf() }
            }

            override fun onTouch(v: View, e: MotionEvent): Boolean {
                when (e.action) {
                    MotionEvent.ACTION_DOWN -> {
                        sx = lp.x; sy = lp.y; tx = e.rawX; ty = e.rawY; moved = false; closed = false
                        h.postDelayed(lpr, 900L)
                        return true
                    }
                    MotionEvent.ACTION_MOVE -> {
                        val dx = (e.rawX - tx).toInt()
                        val dy = (e.rawY - ty).toInt()
                        if (Math.abs(dx) > dp(6) || Math.abs(dy) > dp(6)) { moved = true; h.removeCallbacks(lpr) }
                        if (moved) {
                            lp.x = sx + dx
                            lp.y = sy + dy
                            try { wm.updateViewLayout(col, lp) } catch (x: Exception) {}
                        }
                        return true
                    }
                    MotionEvent.ACTION_UP -> {
                        h.removeCallbacks(lpr)
                        if (!moved && !closed) onTap()
                        return true
                    }
                }
                return false
            }
        })

        wm.addView(col, lp)
        root = col
        btn = t
        msg = m
    }

    private fun say(text: String) {
        val m = msg ?: return
        m.text = text
        m.visibility = View.VISIBLE
        h.removeCallbacks(hideR)
        h.postDelayed(hideR, 6000L)
    }

    private fun setBtn(listening: Boolean) { btn?.text = if (listening) "🔴" else "🎙" }

    private fun onTap() {
        if (busy) return
        if (checkSelfPermission(Manifest.permission.RECORD_AUDIO) != PackageManager.PERMISSION_GRANTED) {
            say("🔐 Mikrofon ruxsati yo'q. Edi ni oching")
            return
        }
        busy = true
        upgradeMic()
        setBtn(true)
        say("🎤 Gapiring…")
        val key = Stt.key(this)
        if (key.isNotEmpty()) recordWhisper(key) else recognizeGoogle()
    }

    private fun recordWhisper(key: String) {
        val f = File(cacheDir, "cmd.m4a")
        val r = Rec(this, h, f) { ok ->
            setBtn(false)
            if (!ok) {
                busy = false
                say("🤷 Ovoz eshitilmadi")
            } else {
                say("🔄 Tanilmoqda…")
                Thread {
                    try {
                        val t = Stt.whisper(key, f, Stt.lang(this))
                        h.post { handleText(t) }
                    } catch (e: Exception) {
                        h.post { busy = false; say("⚠️ " + (e.message ?: "xato")) }
                    }
                }.start()
            }
        }
        rec = r
        if (!r.start()) {
            busy = false
            setBtn(false)
            say("❌ Mikrofon ochilmadi")
        }
    }

    // Groq kaliti bo'lmasa: Google ovoz tanish (kamroq aniq)
    private fun recognizeGoogle() {
        if (!SpeechRecognizer.isRecognitionAvailable(this)) {
            busy = false
            setBtn(false)
            say("❌ Ovoz tanish xizmati yo'q. Edi sozlamalariga Groq kalitini kiriting")
            return
        }
        val r = SpeechRecognizer.createSpeechRecognizer(this)
        sr = r
        r.setRecognitionListener(object : RecognitionListener {
            override fun onReadyForSpeech(p: Bundle?) {}
            override fun onBeginningOfSpeech() {}
            override fun onRmsChanged(v: Float) {}
            override fun onBufferReceived(b: ByteArray?) {}
            override fun onEndOfSpeech() {}
            override fun onPartialResults(p: Bundle?) {}
            override fun onEvent(t: Int, p: Bundle?) {}
            override fun onError(e: Int) {
                try { r.destroy() } catch (x: Exception) {}
                busy = false
                setBtn(false)
                say("🤷 Ovoz eshitilmadi")
            }
            override fun onResults(res: Bundle?) {
                val t = res?.getStringArrayList(SpeechRecognizer.RESULTS_RECOGNITION)?.firstOrNull() ?: ""
                try { r.destroy() } catch (x: Exception) {}
                setBtn(false)
                handleText(t)
            }
        })
        val i = Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH)
            .putExtra(RecognizerIntent.EXTRA_LANGUAGE_MODEL, RecognizerIntent.LANGUAGE_MODEL_FREE_FORM)
            .putExtra(RecognizerIntent.EXTRA_LANGUAGE, "uz-UZ")
        try { r.startListening(i) } catch (e: Exception) { busy = false; setBtn(false) }
    }

    private fun handleText(t0: String) {
        val t = t0.trim()
        if (t.isEmpty()) {
            busy = false
            say("🤷 Ovoz tanilmadi")
            return
        }
        say("🗣 " + t)
        pendingText = t
        val e = engine
        if (e == null) {
            busy = false
            openEdi(t)
            return
        }
        e.evaluateJavascript("window.ediBg?window.ediBg(" + JSONObject.quote(t) + "):Android.bgDone('',false)", null)
        val g = Runnable {
            if (busy) {
                busy = false
                say("⚠️ Dvigatel javob bermadi, Edi ni bir marta oching")
            }
        }
        guard = g
        h.postDelayed(g, 60000L)
    }

    private fun onResult(m: String, isCmd: Boolean) {
        guard?.let { h.removeCallbacks(it) }
        busy = false
        if (isCmd) say(m.take(220)) else openEdi(pendingText)
    }

    private fun openEdi(q: String) {
        try {
            val i = Intent(this, MainActivity::class.java)
            i.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
            i.putExtra("q", q)
            startActivity(i)
        } catch (e: Exception) {
            say("❌ Edi ochilmadi")
        }
    }

    override fun onDestroy() {
        h.removeCallbacksAndMessages(null)
        rec?.cancel()
        try { sr?.destroy() } catch (e: Exception) {}
        try { root?.let { wm.removeView(it) } } catch (e: Exception) {}
        try {
            val e = engine
            if (e != null) { wm.removeView(e); e.destroy() }
        } catch (e: Exception) {}
        root = null
        engine = null
        super.onDestroy()
    }
}
'''


F[KT + 'BootReceiver.kt'] = r'''package com.lutfullo.edi

import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import android.provider.Settings

class BootReceiver : BroadcastReceiver() {
    override fun onReceive(c: Context, i: Intent) {
        try {
            val sp = c.getSharedPreferences("edi", Context.MODE_PRIVATE)
            if (!sp.getBoolean("bubble_on", false)) return
            if (!Settings.canDrawOverlays(c)) return
            c.startForegroundService(Intent(c, BubbleService::class.java))
        } catch (e: Exception) {
        }
    }
}
'''

F[KT + 'InstallReceiver.kt'] = r'''package com.lutfullo.edi

import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import android.content.pm.PackageInstaller
import android.widget.Toast

// O'rnatish natijasini qabul qiladi (yangilash uchun)
class InstallReceiver : BroadcastReceiver() {
    @Suppress("DEPRECATION")
    override fun onReceive(c: Context, i: Intent) {
        val st = i.getIntExtra(PackageInstaller.EXTRA_STATUS, -1)
        if (st == PackageInstaller.STATUS_PENDING_USER_ACTION) {
            val a = i.getParcelableExtra<Intent>(Intent.EXTRA_INTENT)
            if (a != null) {
                a.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
                try { c.startActivity(a) } catch (e: Exception) {}
            }
        } else if (st != PackageInstaller.STATUS_SUCCESS) {
            val m = i.getStringExtra(PackageInstaller.EXTRA_STATUS_MESSAGE) ?: st.toString()
            Toast.makeText(c, "❌ O'rnatilmadi: " + m, Toast.LENGTH_LONG).show()
        }
    }
}
'''


def write(path, content):
    full = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, 'w', encoding='utf-8') as f:
        f.write(content)


def pick(patterns, exact):
    if os.path.exists(exact):
        return exact
    for p in patterns:
        m = sorted(glob.glob(p))
        if m:
            return m[0]
    return None


def main():
    if os.path.isdir(ROOT):
        shutil.rmtree(ROOT)
    for p, c in F.items():
        write(p, c)

    html = pick(['index*.html'], 'index.html')
    if not html:
        sys.exit('XATO: index.html topilmadi')
    os.makedirs(os.path.join(ROOT, 'app/src/main/assets'), exist_ok=True)
    shutil.copy(html, os.path.join(ROOT, 'app/src/main/assets/index.html'))

    ks = pick(['edi*.keystore'], 'edi.keystore')
    if ks:
        shutil.copy(ks, os.path.join(ROOT, 'edi.keystore'))
        print('Keystore:', ks)
    else:
        print('OGOHLANTIRISH: keystore yoq, debug kalit ishlatiladi (yangilash uchun eski ilovani ochirish kerak boladi)')
    print('Tayyor:', len(F), 'fayl +', html)


if __name__ == '__main__':
    main()
