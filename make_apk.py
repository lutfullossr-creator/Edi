#!/usr/bin/env python3
"""Edi - to'liq Android loyihasini android/ papkasiga yaratadi.

Ishlatish:  python make_apk.py
"""
import shutil
from pathlib import Path

URL = "https://lutfullossr-creator.github.io/Edi/"
ROOT = Path("android")
BASE = "app/src/main"
KT = BASE + "/kotlin/com/lutfullo/edi"

FILES = {}

# ----------------------------------------------------------------- Gradle
FILES["settings.gradle.kts"] = r"""
pluginManagement {
    repositories {
        google()
        mavenCentral()
        gradlePluginPortal()
    }
}
dependencyResolutionManagement {
    repositories {
        google()
        mavenCentral()
    }
}
rootProject.name = "Edi"
include(":app")
"""

FILES["build.gradle.kts"] = r"""
plugins {
    id("com.android.application") version "8.5.2" apply false
    id("org.jetbrains.kotlin.android") version "1.9.24" apply false
}
"""

FILES["gradle.properties"] = r"""
org.gradle.jvmargs=-Xmx2g -Dfile.encoding=UTF-8
android.useAndroidX=true
kotlin.code.style=official
"""

FILES["app/build.gradle.kts"] = r"""
plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
}

android {
    namespace = "com.lutfullo.edi"
    compileSdk = 34

    defaultConfig {
        applicationId = "com.lutfullo.edi"
        minSdk = 26
        targetSdk = 34
        versionCode = 1
        versionName = "1.0"
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }

    kotlinOptions {
        jvmTarget = "17"
    }
}
"""

# -------------------------------------------------------------- Manifest
FILES[BASE + "/AndroidManifest.xml"] = r"""<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android">

    <uses-permission android:name="android.permission.INTERNET" />
    <uses-permission android:name="android.permission.CAMERA" />
    <uses-permission android:name="android.permission.RECORD_AUDIO" />
    <uses-permission android:name="android.permission.MODIFY_AUDIO_SETTINGS" />
    <uses-permission android:name="android.permission.CALL_PHONE" />
    <uses-permission android:name="android.permission.SEND_SMS" />
    <uses-permission android:name="android.permission.READ_CONTACTS" />
    <uses-permission android:name="android.permission.ACCESS_FINE_LOCATION" />
    <uses-permission android:name="android.permission.ACCESS_COARSE_LOCATION" />
    <uses-permission android:name="android.permission.POST_NOTIFICATIONS" />
    <uses-permission android:name="android.permission.FOREGROUND_SERVICE" />
    <uses-permission android:name="android.permission.FOREGROUND_SERVICE_MICROPHONE" />
    <uses-permission android:name="android.permission.VIBRATE" />
    <uses-permission android:name="android.permission.SET_ALARM" />
    <uses-permission android:name="android.permission.ACCESS_NOTIFICATION_POLICY" />
    <uses-permission android:name="android.permission.WRITE_SETTINGS" />

    <uses-feature android:name="android.hardware.camera" android:required="false" />
    <uses-feature android:name="android.hardware.microphone" android:required="false" />
    <uses-feature android:name="android.hardware.telephony" android:required="false" />

    <queries>
        <intent>
            <action android:name="android.intent.action.MAIN" />
            <category android:name="android.intent.category.LAUNCHER" />
        </intent>
        <intent>
            <action android:name="android.speech.RecognitionService" />
        </intent>
        <intent>
            <action android:name="android.intent.action.TTS_SERVICE" />
        </intent>
    </queries>

    <application
        android:label="Edi"
        android:icon="@android:drawable/sym_def_app_icon"
        android:allowBackup="true"
        android:theme="@android:style/Theme.DeviceDefault.NoActionBar">

        <activity
            android:name=".MainActivity"
            android:exported="true"
            android:configChanges="orientation|screenSize|keyboardHidden"
            android:windowSoftInputMode="adjustResize">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>

        <service
            android:name=".ListenService"
            android:exported="false"
            android:foregroundServiceType="microphone" />

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
    </application>
</manifest>
"""

FILES[BASE + "/res/xml/edi_access.xml"] = r"""<?xml version="1.0" encoding="utf-8"?>
<accessibility-service xmlns:android="http://schemas.android.com/apk/res/android"
    android:accessibilityEventTypes="typeWindowStateChanged"
    android:accessibilityFeedbackType="feedbackGeneric"
    android:canRetrieveWindowContent="false"
    android:description="@string/access_desc"
    android:notificationTimeout="100" />
"""

FILES[BASE + "/res/values/strings.xml"] = r"""<?xml version="1.0" encoding="utf-8"?>
<resources>
    <string name="app_name">Edi</string>
    <string name="access_desc">Edi: orqaga, uy, so\'nggi ilovalar, ekranni qulflash va skrinshot buyruqlarini bajaradi.</string>
</resources>
"""

# ----------------------------------------------------------------- Kotlin
FILES[KT + "/Hub.kt"] = r"""
package com.lutfullo.edi

import android.content.Context
import android.content.Intent
import android.os.Handler
import android.os.Looper
import android.speech.RecognizerIntent
import android.webkit.WebView
import org.json.JSONObject
import java.util.Locale

object Hub {
    @Volatile
    var web: WebView? = null

    private val main = Handler(Looper.getMainLooper())

    // Veb-sahifaga hodisa yuboradi: window.onEdiSpeech(text) / window.onEdiWake(text)
    // va 'edi-speech' / 'edi-wake' CustomEvent
    fun emit(kind: String, text: String) {
        val w = web ?: return
        val fn = "onEdi" + kind.replaceFirstChar { it.uppercase() }
        val js = "(function(t){try{window.dispatchEvent(new CustomEvent('edi-" + kind +
            "',{detail:t}));if(typeof window." + fn + "==='function')window." + fn +
            "(t);}catch(e){}})(" + JSONObject.quote(text) + ")"
        main.post { w.evaluateJavascript(js, null) }
    }

    fun lang(ctx: Context): String =
        ctx.getSharedPreferences("edi", Context.MODE_PRIVATE).getString("lang", "uz") ?: "uz"

    fun tag(ctx: Context): String = when (lang(ctx)) {
        "uz" -> "uz-UZ"
        "ru" -> "ru-RU"
        "en" -> "en-US"
        else -> Locale.getDefault().toLanguageTag()
    }

    fun locale(ctx: Context): Locale = Locale.forLanguageTag(tag(ctx))

    fun recIntent(ctx: Context): Intent =
        Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH)
            .putExtra(RecognizerIntent.EXTRA_LANGUAGE_MODEL, RecognizerIntent.LANGUAGE_MODEL_FREE_FORM)
            .putExtra(RecognizerIntent.EXTRA_LANGUAGE, tag(ctx))
            .putExtra(RecognizerIntent.EXTRA_CALLING_PACKAGE, ctx.packageName)
}
"""

FILES[KT + "/MainActivity.kt"] = r"""
package com.lutfullo.edi

import android.Manifest
import android.annotation.SuppressLint
import android.app.Activity
import android.content.Intent
import android.content.pm.PackageManager
import android.net.Uri
import android.os.Build
import android.os.Bundle
import android.webkit.PermissionRequest
import android.webkit.ValueCallback
import android.webkit.WebChromeClient
import android.webkit.WebResourceRequest
import android.webkit.WebView
import android.webkit.WebViewClient

class MainActivity : Activity() {

    private lateinit var web: WebView
    private var fileCb: ValueCallback<Array<Uri>>? = null
    private val host = "lutfullossr-creator.github.io"

    @SuppressLint("SetJavaScriptEnabled")
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        askPermissions()

        web = WebView(this)
        setContentView(web)
        Hub.web = web

        val s = web.settings
        s.javaScriptEnabled = true
        s.domStorageEnabled = true
        s.mediaPlaybackRequiresUserGesture = false
        s.allowFileAccess = false

        // Veb-sahifa shu obyekt orqali telefon buyruqlarini chaqiradi
        val bridge = Bridge(applicationContext)
        for (n in arrayOf("Android", "Edi", "EdiBridge", "Bridge", "AndroidBridge")) {
            web.addJavascriptInterface(bridge, n)
        }

        web.webViewClient = object : WebViewClient() {
            override fun shouldOverrideUrlLoading(view: WebView?, request: WebResourceRequest?): Boolean {
                val u = request?.url ?: return false
                if (u.host == host) return false
                try {
                    startActivity(Intent(Intent.ACTION_VIEW, u))
                } catch (e: Exception) {
                }
                return true
            }
        }

        web.webChromeClient = object : WebChromeClient() {
            override fun onPermissionRequest(request: PermissionRequest) {
                runOnUiThread { request.grant(request.resources) }
            }

            override fun onShowFileChooser(
                w: WebView?,
                cb: ValueCallback<Array<Uri>>?,
                p: WebChromeClient.FileChooserParams?
            ): Boolean {
                fileCb?.onReceiveValue(null)
                fileCb = cb
                val i = Intent(Intent.ACTION_GET_CONTENT)
                i.addCategory(Intent.CATEGORY_OPENABLE)
                i.type = "*/*"
                try {
                    startActivityForResult(Intent.createChooser(i, "Fayl"), 7)
                } catch (e: Exception) {
                    fileCb = null
                    return false
                }
                return true
            }
        }

        web.loadUrl("__URL__")
    }

    private fun askPermissions() {
        val want = arrayListOf(
            Manifest.permission.CAMERA,
            Manifest.permission.RECORD_AUDIO,
            Manifest.permission.CALL_PHONE,
            Manifest.permission.SEND_SMS,
            Manifest.permission.READ_CONTACTS,
            Manifest.permission.ACCESS_FINE_LOCATION
        )
        if (Build.VERSION.SDK_INT >= 33) want.add(Manifest.permission.POST_NOTIFICATIONS)
        val need = want.filter { checkSelfPermission(it) != PackageManager.PERMISSION_GRANTED }
        if (need.isNotEmpty()) requestPermissions(need.toTypedArray(), 1)
    }

    @Deprecated("Deprecated in Java")
    override fun onActivityResult(requestCode: Int, resultCode: Int, data: Intent?) {
        super.onActivityResult(requestCode, resultCode, data)
        if (requestCode == 7) {
            val r: Array<Uri>? = if (resultCode == RESULT_OK && data != null)
                WebChromeClient.FileChooserParams.parseResult(resultCode, data) else null
            fileCb?.onReceiveValue(r)
            fileCb = null
        }
    }

    @Deprecated("Deprecated in Java")
    override fun onBackPressed() {
        if (web.canGoBack()) web.goBack() else super.onBackPressed()
    }

    override fun onDestroy() {
        Hub.web = null
        web.destroy()
        super.onDestroy()
    }
}
"""

FILES[KT + "/Bridge.kt"] = r"""
package com.lutfullo.edi

import android.Manifest
import android.app.NotificationManager
import android.content.Context
import android.content.Intent
import android.content.IntentFilter
import android.content.pm.PackageManager
import android.hardware.camera2.CameraCharacteristics
import android.hardware.camera2.CameraManager
import android.location.Location
import android.location.LocationManager
import android.media.AudioManager
import android.net.Uri
import android.os.BatteryManager
import android.os.Build
import android.os.Bundle
import android.os.Handler
import android.os.Looper
import android.os.VibrationEffect
import android.os.Vibrator
import android.provider.AlarmClock
import android.provider.ContactsContract
import android.provider.ContactsContract.CommonDataKinds.Phone
import android.provider.Settings
import android.speech.RecognitionListener
import android.speech.SpeechRecognizer
import android.speech.tts.TextToSpeech
import android.telephony.SmsManager
import android.view.KeyEvent
import android.webkit.JavascriptInterface
import java.util.Locale

// JS tomondan chaqiriladi:  Android.cmd("flash:on")  (Edi / EdiBridge / Bridge nomlari ham ishlaydi)
class Bridge(private val ctx: Context) {

    private val main = Handler(Looper.getMainLooper())
    private val audio = ctx.getSystemService(Context.AUDIO_SERVICE) as AudioManager
    private val prefs = ctx.getSharedPreferences("edi", Context.MODE_PRIVATE)
    private var torchOn = false
    private var tts: TextToSpeech? = null
    private var ttsReady = false
    private val pending = ArrayList<String>()
    private var recognizer: SpeechRecognizer? = null

    // ---------------------------------------------------- JS kirish nuqtalari
    @JavascriptInterface
    fun cmd(c: String?): String = handle(c)

    @JavascriptInterface
    fun run(c: String?): String = handle(c)

    @JavascriptInterface
    fun exec(c: String?): String = handle(c)

    @JavascriptInterface
    fun send(c: String?): String = handle(c)

    @JavascriptInterface
    fun command(c: String?): String = handle(c)

    @JavascriptInterface
    fun ping(): String = "edi-ok"

    // ----------------------------------------------------------- Dispatcher
    private fun handle(raw: String?): String {
        val c = (raw ?: "").trim()
        if (c.isEmpty()) return "bo'sh buyruq"
        val name = c.substringBefore(":").trim().lowercase()
        val arg = if (c.contains(":")) c.substringAfter(":").trim() else ""
        return try {
            when (name) {
                "ping" -> "edi-ok"
                "help" -> help()
                "flash", "torch" -> doFlash(arg)
                "vol", "volume" -> doVol(arg)
                "music" -> doMusic(arg)
                "call" -> doCall(arg)
                "sms" -> doSms(arg)
                "contact" -> doContact(arg)
                "open" -> doOpen(arg)
                "shot" -> access("skrinshot") { it.shot() }
                "lock" -> access("ekran qulfi") { it.lock() }
                "back" -> access("orqaga") { it.back() }
                "home" -> access("bosh ekran") { it.home() }
                "recents" -> access("so'nggi ilovalar") { it.recents() }
                "panel" -> access("bildirishnoma paneli") { it.shade() }
                "quick" -> access("tezkor sozlamalar") { it.quick() }
                "battery" -> doBattery()
                "bright" -> doBright(arg)
                "dnd" -> doDnd(arg)
                "alarm" -> doAlarm(arg)
                "timer" -> doTimer(arg)
                "nav" -> doNav(arg)
                "notifs" -> doNotifs()
                "speak" -> doSpeak(arg)
                "stop" -> doStop()
                "listen" -> doListen()
                "loop" -> doLoop(arg)
                "lang" -> doLang(arg)
                "vibrate" -> doVibrate(arg)
                "loc" -> doLoc()
                "url" -> doUrl(arg)
                else -> "noma'lum buyruq: " + name
            }
        } catch (e: SecurityException) {
            "ruxsat yo'q: " + (e.message ?: "")
        } catch (e: Exception) {
            "xato: " + (e.message ?: e.toString())
        }
    }

    private fun help(): String =
        "flash:on|off  vol:up|down|set:50|mute  music:play|pause|next|prev  call:<ism|raqam>  " +
            "sms:<ism|raqam>:<matn>  contact:<ism>  open:<ilova>  shot  lock  back  home  recents  panel  " +
            "battery  bright:up|down|set:50  dnd:on|off  alarm:SS:DD  timer:<soniya|5m>  nav:<manzil>  " +
            "notifs  speak:<matn>  stop  listen  loop:true|false  lang:uz|ru|en  vibrate:300  loc  url:<havola>"

    private fun go(i: Intent) {
        i.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
        ctx.startActivity(i)
    }

    // --------------------------------------------------------------- Fonar
    private fun doFlash(arg: String): String {
        val cm = ctx.getSystemService(Context.CAMERA_SERVICE) as CameraManager
        var id: String? = null
        for (i in cm.cameraIdList) {
            val ch = cm.getCameraCharacteristics(i)
            val has = ch.get(CameraCharacteristics.FLASH_INFO_AVAILABLE) == true
            val back = ch.get(CameraCharacteristics.LENS_FACING) == CameraCharacteristics.LENS_FACING_BACK
            if (has && back) {
                id = i
                break
            }
        }
        if (id == null) return "fonar topilmadi"
        val want = when (arg.lowercase()) {
            "on" -> true
            "off" -> false
            else -> !torchOn
        }
        cm.setTorchMode(id, want)
        torchOn = want
        return if (want) "fonar yoqildi" else "fonar o'chirildi"
    }

    // ---------------------------------------------------------------- Ovoz
    private fun doVol(arg: String): String {
        val st = AudioManager.STREAM_MUSIC
        val max = audio.getStreamMaxVolume(st)
        when {
            arg == "up" -> audio.adjustStreamVolume(st, AudioManager.ADJUST_RAISE, AudioManager.FLAG_SHOW_UI)
            arg == "down" -> audio.adjustStreamVolume(st, AudioManager.ADJUST_LOWER, AudioManager.FLAG_SHOW_UI)
            arg == "mute" -> audio.adjustStreamVolume(st, AudioManager.ADJUST_MUTE, AudioManager.FLAG_SHOW_UI)
            arg.startsWith("set") -> {
                val p = arg.substringAfter(":", "").trim().toIntOrNull() ?: return "vol:set:50"
                audio.setStreamVolume(st, max * p.coerceIn(0, 100) / 100, AudioManager.FLAG_SHOW_UI)
            }
            else -> return "vol:up|down|set:50|mute"
        }
        val cur = audio.getStreamVolume(st)
        return "ovoz: " + (if (max > 0) cur * 100 / max else 0) + "%"
    }

    // -------------------------------------------------------------- Musiqa
    private fun key(code: Int) {
        audio.dispatchMediaKeyEvent(KeyEvent(KeyEvent.ACTION_DOWN, code))
        audio.dispatchMediaKeyEvent(KeyEvent(KeyEvent.ACTION_UP, code))
    }

    private fun doMusic(arg: String): String {
        val code = when (arg.lowercase()) {
            "play" -> KeyEvent.KEYCODE_MEDIA_PLAY
            "pause" -> KeyEvent.KEYCODE_MEDIA_PAUSE
            "toggle" -> KeyEvent.KEYCODE_MEDIA_PLAY_PAUSE
            "next" -> KeyEvent.KEYCODE_MEDIA_NEXT
            "prev" -> KeyEvent.KEYCODE_MEDIA_PREVIOUS
            "stop" -> KeyEvent.KEYCODE_MEDIA_STOP
            else -> return "music:play|pause|next|prev"
        }
        key(code)
        return "musiqa: " + arg
    }

    // ------------------------------------------------- Aloqa (call/sms/kontakt)
    private fun findNumber(q: String): String? {
        val query = q.trim()
        if (query.isEmpty()) return null
        val digits = query.filter { it.isDigit() || it == '+' }
        val onlyPhone = query.all { it.isDigit() || it == '+' || it == ' ' || it == '-' || it == '(' || it == ')' }
        if (digits.length >= 3 && onlyPhone) return digits
        val cur = ctx.contentResolver.query(
            Phone.CONTENT_URI,
            arrayOf(Phone.DISPLAY_NAME, Phone.NUMBER),
            Phone.DISPLAY_NAME + " LIKE ?",
            arrayOf("%" + query + "%"),
            null
        )
        if (cur != null) {
            cur.use {
                if (it.moveToFirst()) return it.getString(1)
            }
        }
        return null
    }

    private fun doCall(arg: String): String {
        val n = findNumber(arg) ?: return "kontakt topilmadi: " + arg
        go(Intent(Intent.ACTION_CALL, Uri.parse("tel:" + Uri.encode(n))))
        return "qo'ng'iroq: " + n
    }

    @Suppress("DEPRECATION")
    private fun smsManager(): SmsManager =
        if (Build.VERSION.SDK_INT >= 31) ctx.getSystemService(SmsManager::class.java) else SmsManager.getDefault()

    private fun doSms(arg: String): String {
        val to = arg.substringBefore(":").trim()
        val text = arg.substringAfter(":", "").trim()
        if (to.isEmpty() || text.isEmpty()) return "sms:<ism|raqam>:<matn>"
        val n = findNumber(to) ?: return "kontakt topilmadi: " + to
        val sm = smsManager()
        sm.sendMultipartTextMessage(n, null, sm.divideMessage(text), null, null)
        return "SMS yuborildi: " + n
    }

    private fun doContact(arg: String): String {
        val n = findNumber(arg) ?: return "kontakt topilmadi: " + arg
        return arg + ": " + n
    }

    // ---------------------------------------------------------- Ilova ochish
    private fun doOpen(arg: String): String {
        if (arg.isEmpty()) return "open:<ilova nomi>"
        val alias = mapOf(
            "kamera" to "camera", "sozlamalar" to "settings", "sozlama" to "settings",
            "kalkulyator" to "calculator", "galereya" to "gallery", "soat" to "clock",
            "kontaktlar" to "contacts", "telefon" to "phone", "xarita" to "maps", "pochta" to "mail"
        )
        val q = alias[arg.lowercase()] ?: arg.lowercase()
        val pm = ctx.packageManager
        val list = pm.queryIntentActivities(Intent(Intent.ACTION_MAIN).addCategory(Intent.CATEGORY_LAUNCHER), 0)
        var pkg: String? = null
        var label = ""
        for (r in list) {
            val l = r.loadLabel(pm).toString()
            val ll = l.lowercase()
            if (ll == q) {
                pkg = r.activityInfo.packageName
                label = l
                break
            }
            if (pkg == null && (ll.contains(q) || r.activityInfo.packageName.lowercase().contains(q))) {
                pkg = r.activityInfo.packageName
                label = l
            }
        }
        if (pkg == null) return "ilova topilmadi: " + arg
        val i = pm.getLaunchIntentForPackage(pkg) ?: return "ilova ochilmadi: " + label
        go(i)
        return "ochildi: " + label
    }

    // ------------------------------------------- Tizim tugmalari (Accessibility)
    private fun goSettings(action: String) {
        go(Intent(action))
    }

    private fun access(label: String, f: (EdiAccessibility) -> Boolean): String {
        val s = EdiAccessibility.instance
        if (s == null) {
            goSettings(Settings.ACTION_ACCESSIBILITY_SETTINGS)
            return "Maxsus imkoniyatlarda Edi xizmatini yoqing"
        }
        return if (f(s)) label + " bajarildi" else label + " bajarilmadi"
    }

    // --------------------------------------------------------------- Batareya
    private fun doBattery(): String {
        val i = ctx.registerReceiver(null, IntentFilter(Intent.ACTION_BATTERY_CHANGED))
        val level = i?.getIntExtra(BatteryManager.EXTRA_LEVEL, -1) ?: -1
        val scale = i?.getIntExtra(BatteryManager.EXTRA_SCALE, 100) ?: 100
        val st = i?.getIntExtra(BatteryManager.EXTRA_STATUS, -1) ?: -1
        val charging = st == BatteryManager.BATTERY_STATUS_CHARGING || st == BatteryManager.BATTERY_STATUS_FULL
        val pct = if (level >= 0 && scale > 0) level * 100 / scale else -1
        return "batareya: " + pct + "%" + (if (charging) " (zaryadlanmoqda)" else "")
    }

    // -------------------------------------------------------------- Yorqinlik
    private fun doBright(arg: String): String {
        if (!Settings.System.canWrite(ctx)) {
            go(Intent(Settings.ACTION_MANAGE_WRITE_SETTINGS, Uri.parse("package:" + ctx.packageName)))
            return "Tizim sozlamalarini o'zgartirish ruxsatini bering"
        }
        val cr = ctx.contentResolver
        Settings.System.putInt(
            cr, Settings.System.SCREEN_BRIGHTNESS_MODE, Settings.System.SCREEN_BRIGHTNESS_MODE_MANUAL
        )
        var cur = Settings.System.getInt(cr, Settings.System.SCREEN_BRIGHTNESS, 128)
        cur = when {
            arg == "up" -> cur + 40
            arg == "down" -> cur - 40
            arg.startsWith("set") -> {
                val p = arg.substringAfter(":", "").trim().toIntOrNull() ?: return "bright:set:50"
                p.coerceIn(0, 100) * 255 / 100
            }
            else -> return "bright:up|down|set:50"
        }
        cur = cur.coerceIn(5, 255)
        Settings.System.putInt(cr, Settings.System.SCREEN_BRIGHTNESS, cur)
        return "yorqinlik: " + (cur * 100 / 255) + "%"
    }

    // ------------------------------------------------------ Bezovta qilmang
    private fun doDnd(arg: String): String {
        val nm = ctx.getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager
        if (!nm.isNotificationPolicyAccessGranted) {
            goSettings(Settings.ACTION_NOTIFICATION_POLICY_ACCESS_SETTINGS)
            return "Bezovta qilmang rejimiga ruxsat bering"
        }
        val on = arg.lowercase() == "on"
        nm.setInterruptionFilter(
            if (on) NotificationManager.INTERRUPTION_FILTER_NONE else NotificationManager.INTERRUPTION_FILTER_ALL
        )
        return if (on) "bezovta qilmang: yoqildi" else "bezovta qilmang: o'chirildi"
    }

    // ------------------------------------------------------- Alarm va taymer
    private fun doAlarm(arg: String): String {
        val p = arg.split(":")
        val h = p.getOrNull(0)?.trim()?.toIntOrNull()
        val m = p.getOrNull(1)?.trim()?.toIntOrNull() ?: 0
        if (h == null || h < 0 || h > 23 || m < 0 || m > 59) return "alarm:SS:DD"
        val i = Intent(AlarmClock.ACTION_SET_ALARM)
            .putExtra(AlarmClock.EXTRA_HOUR, h)
            .putExtra(AlarmClock.EXTRA_MINUTES, m)
            .putExtra(AlarmClock.EXTRA_MESSAGE, "Edi")
            .putExtra(AlarmClock.EXTRA_SKIP_UI, true)
        go(i)
        return "alarm: " + h + ":" + (if (m < 10) "0" else "") + m
    }

    private fun doTimer(arg: String): String {
        val t = arg.lowercase().trim()
        val secs: Int? = when {
            t.endsWith("m") -> t.dropLast(1).toIntOrNull()?.times(60)
            t.endsWith("s") -> t.dropLast(1).toIntOrNull()
            else -> t.toIntOrNull()
        }
        if (secs == null || secs <= 0) return "timer:<soniya|5m>"
        val i = Intent(AlarmClock.ACTION_SET_TIMER)
            .putExtra(AlarmClock.EXTRA_LENGTH, secs)
            .putExtra(AlarmClock.EXTRA_MESSAGE, "Edi")
            .putExtra(AlarmClock.EXTRA_SKIP_UI, true)
        go(i)
        return "taymer: " + secs + " soniya"
    }

    // ------------------------------------------------------------ Navigatsiya
    private fun doNav(arg: String): String {
        if (arg.isEmpty()) return "nav:<manzil>"
        try {
            go(Intent(Intent.ACTION_VIEW, Uri.parse("google.navigation:q=" + Uri.encode(arg))))
        } catch (e: Exception) {
            go(Intent(Intent.ACTION_VIEW, Uri.parse("geo:0,0?q=" + Uri.encode(arg))))
        }
        return "navigatsiya: " + arg
    }

    // ---------------------------------------------------------- Bildirishnoma
    private fun listenerEnabled(): Boolean {
        val s = Settings.Secure.getString(ctx.contentResolver, "enabled_notification_listeners") ?: return false
        return s.contains(ctx.packageName)
    }

    private fun doNotifs(): String {
        if (!listenerEnabled()) {
            goSettings(Settings.ACTION_NOTIFICATION_LISTENER_SETTINGS)
            return "Bildirishnomalarni o'qishga Edi'ga ruxsat bering"
        }
        val l = EdiNotifListener.recent
        if (l.isEmpty()) return "bildirishnoma yo'q"
        return l.takeLast(10).joinToString("\n")
    }

    // ------------------------------------------------------------- Gapirish
    private fun applyTtsLang() {
        val t = tts ?: return
        val r = t.setLanguage(Hub.locale(ctx))
        if (r == TextToSpeech.LANG_MISSING_DATA || r == TextToSpeech.LANG_NOT_SUPPORTED) {
            t.setLanguage(Locale.getDefault())
        }
    }

    private fun doSpeak(arg: String): String {
        if (arg.isEmpty()) return "speak:<matn>"
        main.post {
            if (tts == null) {
                tts = TextToSpeech(ctx, TextToSpeech.OnInitListener { status ->
                    if (status == TextToSpeech.SUCCESS) {
                        ttsReady = true
                        applyTtsLang()
                        for (t in pending) tts?.speak(t, TextToSpeech.QUEUE_ADD, null, "edi")
                        pending.clear()
                    }
                })
            }
            if (ttsReady) tts?.speak(arg, TextToSpeech.QUEUE_FLUSH, null, "edi") else pending.add(arg)
        }
        return "gapiryapman"
    }

    private fun doStop(): String {
        main.post {
            tts?.stop()
            pending.clear()
        }
        return "to'xtatildi"
    }

    // ------------------------------------------------------------ Tinglash
    private fun doListen(): String {
        if (!SpeechRecognizer.isRecognitionAvailable(ctx)) return "ovoz tanish xizmati yo'q"
        if (ctx.checkSelfPermission(Manifest.permission.RECORD_AUDIO) != PackageManager.PERMISSION_GRANTED) {
            return "mikrofon ruxsati kerak"
        }
        main.post {
            recognizer?.destroy()
            val r = SpeechRecognizer.createSpeechRecognizer(ctx)
            recognizer = r
            r.setRecognitionListener(object : RecognitionListener {
                override fun onReadyForSpeech(params: Bundle?) {}
                override fun onBeginningOfSpeech() {}
                override fun onRmsChanged(rmsdB: Float) {}
                override fun onBufferReceived(buffer: ByteArray?) {}
                override fun onEndOfSpeech() {}
                override fun onError(error: Int) {
                    Hub.emit("speech", "")
                }

                override fun onResults(results: Bundle?) {
                    val t = results?.getStringArrayList(SpeechRecognizer.RESULTS_RECOGNITION)?.firstOrNull() ?: ""
                    Hub.emit("speech", t)
                }

                override fun onPartialResults(partialResults: Bundle?) {}
                override fun onEvent(eventType: Int, params: Bundle?) {}
            })
            r.startListening(Hub.recIntent(ctx))
        }
        return "tinglayapman"
    }

    private fun doLoop(arg: String): String {
        val i = Intent(ctx, ListenService::class.java)
        val on = arg.lowercase() == "true" || arg.lowercase() == "on"
        if (on) {
            if (ctx.checkSelfPermission(Manifest.permission.RECORD_AUDIO) != PackageManager.PERMISSION_GRANTED) {
                return "mikrofon ruxsati kerak"
            }
            ctx.startForegroundService(i)
            return "doimiy tinglash yoqildi (Edi, ... deng)"
        }
        ctx.stopService(i)
        return "doimiy tinglash o'chirildi"
    }

    private fun doLang(arg: String): String {
        val a = arg.lowercase()
        if (a != "uz" && a != "ru" && a != "en") return "lang:uz|ru|en"
        prefs.edit().putString("lang", a).apply()
        main.post { applyTtsLang() }
        return "til: " + a
    }

    // ------------------------------------------------------------ Boshqalar
    private fun doVibrate(arg: String): String {
        val ms = (arg.toLongOrNull() ?: 300L).coerceIn(10L, 3000L)
        val v = ctx.getSystemService(Context.VIBRATOR_SERVICE) as Vibrator
        v.vibrate(VibrationEffect.createOneShot(ms, VibrationEffect.DEFAULT_AMPLITUDE))
        return "tebranish: " + ms + " ms"
    }

    private fun doLoc(): String {
        val lm = ctx.getSystemService(Context.LOCATION_SERVICE) as LocationManager
        var best: Location? = null
        for (p in lm.getProviders(true)) {
            val l = lm.getLastKnownLocation(p) ?: continue
            if (best == null || l.accuracy < best.accuracy) best = l
        }
        return if (best == null) "joylashuv noma'lum" else best.latitude.toString() + "," + best.longitude.toString()
    }

    private fun doUrl(arg: String): String {
        if (arg.isEmpty()) return "url:<havola>"
        val u = if (arg.startsWith("http")) arg else "https://" + arg
        go(Intent(Intent.ACTION_VIEW, Uri.parse(u)))
        return "ochildi: " + u
    }
}
"""

FILES[KT + "/EdiAccessibility.kt"] = r"""
package com.lutfullo.edi

import android.accessibilityservice.AccessibilityService
import android.content.Intent
import android.os.Build
import android.view.accessibility.AccessibilityEvent

class EdiAccessibility : AccessibilityService() {

    companion object {
        @Volatile
        var instance: EdiAccessibility? = null
    }

    override fun onServiceConnected() {
        super.onServiceConnected()
        instance = this
    }

    override fun onAccessibilityEvent(event: AccessibilityEvent?) {}

    override fun onInterrupt() {}

    override fun onUnbind(intent: Intent?): Boolean {
        instance = null
        return super.onUnbind(intent)
    }

    override fun onDestroy() {
        instance = null
        super.onDestroy()
    }

    fun back(): Boolean = performGlobalAction(GLOBAL_ACTION_BACK)
    fun home(): Boolean = performGlobalAction(GLOBAL_ACTION_HOME)
    fun recents(): Boolean = performGlobalAction(GLOBAL_ACTION_RECENTS)
    fun shade(): Boolean = performGlobalAction(GLOBAL_ACTION_NOTIFICATIONS)
    fun quick(): Boolean = performGlobalAction(GLOBAL_ACTION_QUICK_SETTINGS)
    fun lock(): Boolean = Build.VERSION.SDK_INT >= 28 && performGlobalAction(GLOBAL_ACTION_LOCK_SCREEN)
    fun shot(): Boolean = Build.VERSION.SDK_INT >= 28 && performGlobalAction(GLOBAL_ACTION_TAKE_SCREENSHOT)
}
"""

FILES[KT + "/EdiNotifListener.kt"] = r"""
package com.lutfullo.edi

import android.app.Notification
import android.service.notification.NotificationListenerService
import android.service.notification.StatusBarNotification
import java.util.concurrent.CopyOnWriteArrayList

class EdiNotifListener : NotificationListenerService() {

    companion object {
        val recent = CopyOnWriteArrayList<String>()
    }

    private fun fmt(sbn: StatusBarNotification): String? {
        if (sbn.packageName == packageName) return null
        val e = sbn.notification.extras
        val title = e.getCharSequence(Notification.EXTRA_TITLE)?.toString() ?: ""
        val text = e.getCharSequence(Notification.EXTRA_TEXT)?.toString() ?: ""
        if (title.isEmpty() && text.isEmpty()) return null
        return sbn.packageName + ": " + title + " - " + text
    }

    private fun add(s: String) {
        recent.add(s)
        while (recent.size > 30) recent.removeAt(0)
    }

    override fun onNotificationPosted(sbn: StatusBarNotification?) {
        if (sbn == null) return
        val s = fmt(sbn) ?: return
        add(s)
    }

    override fun onListenerConnected() {
        try {
            for (n in activeNotifications) {
                val s = fmt(n)
                if (s != null) add(s)
            }
        } catch (e: Exception) {
        }
    }
}
"""

FILES[KT + "/ListenService.kt"] = r"""
package com.lutfullo.edi

import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.app.Service
import android.content.Context
import android.content.Intent
import android.content.pm.ServiceInfo
import android.os.Build
import android.os.Bundle
import android.os.Handler
import android.os.IBinder
import android.os.Looper
import android.speech.RecognitionListener
import android.speech.SpeechRecognizer

// "Edi, ..." deb aytilganda buyruqni tinglaydi va veb-sahifaga yuboradi
class ListenService : Service() {

    private val main = Handler(Looper.getMainLooper())
    private var rec: SpeechRecognizer? = null
    private var running = false
    private val wake = Regex("(^|\\s)(edi|эди|eddy|eddie|edy)[,\\s]+(.+)")

    override fun onBind(intent: Intent?): IBinder? = null

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        startFg()
        if (!running) {
            running = true
            main.post { listen() }
        }
        return START_STICKY
    }

    private fun startFg() {
        val nm = getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager
        nm.createNotificationChannel(
            NotificationChannel("edi_listen", "Edi tinglash", NotificationManager.IMPORTANCE_LOW)
        )
        val pi = PendingIntent.getActivity(
            this, 0, Intent(this, MainActivity::class.java), PendingIntent.FLAG_IMMUTABLE
        )
        val n = Notification.Builder(this, "edi_listen")
            .setContentTitle("Edi")
            .setContentText("Edi, ... deb ayting")
            .setSmallIcon(android.R.drawable.ic_btn_speak_now)
            .setContentIntent(pi)
            .setOngoing(true)
            .build()
        if (Build.VERSION.SDK_INT >= 29) {
            startForeground(1, n, ServiceInfo.FOREGROUND_SERVICE_TYPE_MICROPHONE)
        } else {
            startForeground(1, n)
        }
    }

    private fun listen() {
        if (!running) return
        if (!SpeechRecognizer.isRecognitionAvailable(this)) {
            stopSelf()
            return
        }
        rec?.destroy()
        val r = SpeechRecognizer.createSpeechRecognizer(this)
        rec = r
        r.setRecognitionListener(object : RecognitionListener {
            override fun onReadyForSpeech(params: Bundle?) {}
            override fun onBeginningOfSpeech() {}
            override fun onRmsChanged(rmsdB: Float) {}
            override fun onBufferReceived(buffer: ByteArray?) {}
            override fun onEndOfSpeech() {}
            override fun onError(error: Int) {
                restart(1200)
            }

            override fun onResults(results: Bundle?) {
                val t = results?.getStringArrayList(SpeechRecognizer.RESULTS_RECOGNITION)?.firstOrNull() ?: ""
                handleText(t)
                restart(300)
            }

            override fun onPartialResults(partialResults: Bundle?) {}
            override fun onEvent(eventType: Int, params: Bundle?) {}
        })
        r.startListening(Hub.recIntent(this))
    }

    private fun restart(ms: Long) {
        if (running) main.postDelayed({ listen() }, ms)
    }

    private fun handleText(t: String) {
        val m = wake.find(t.lowercase()) ?: return
        val cmd = m.groupValues[3].trim()
        if (cmd.isNotEmpty()) Hub.emit("wake", cmd)
    }

    override fun onDestroy() {
        running = false
        main.removeCallbacksAndMessages(null)
        rec?.destroy()
        rec = null
        super.onDestroy()
    }
}
"""


def main():
    if ROOT.exists():
        shutil.rmtree(ROOT)
    for rel, content in FILES.items():
        path = ROOT / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content.lstrip("\n").replace("__URL__", URL), encoding="utf-8")
        print("yozildi:", path)

    # index.html ham ilova ichiga nusxalanadi (zaxira sifatida)
    idx = Path("index.html")
    if idx.exists():
        assets = ROOT / BASE / "assets"
        assets.mkdir(parents=True, exist_ok=True)
        shutil.copy(idx, assets / "index.html")
        print("index.html ko'chirildi")

    print("Tayyor: android/ papkasi yaratildi")


if __name__ == "__main__":
    main()
