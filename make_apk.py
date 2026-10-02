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
    <uses-permission android:name="android.permission.FOREGROUND_SERVICE" />
    <uses-permission android:name="android.permission.FOREGROUND_SERVICE_MICROPHONE" />

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
    android:canRetrieveWindowContent="false"
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
import android.content.Intent
import android.view.accessibility.AccessibilityEvent

class EdiAccessibility : AccessibilityService() {
    companion object {
        @Volatile var inst: EdiAccessibility? = null
    }

    override fun onServiceConnected() { inst = this }
    override fun onAccessibilityEvent(e: AccessibilityEvent?) {}
    override fun onInterrupt() {}
    override fun onUnbind(i: Intent?): Boolean { inst = null; return super.onUnbind(i) }
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
    private val wake = Regex("^\\s*(?:(?:hey|hay|ey|ok|okay)\\s+)?(?:edi|eddi|eddy|edy|эди)\\b[\\s,.:!-]*", RegexOption.IGNORE_CASE)

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
                val t = res?.getStringArrayList(SpeechRecognizer.RESULTS_RECOGNITION)?.firstOrNull()
                if (t != null) handle(t)
                again(300L)
            }
        })
        val it = Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH)
            .putExtra(RecognizerIntent.EXTRA_LANGUAGE_MODEL, RecognizerIntent.LANGUAGE_MODEL_FREE_FORM)
            .putExtra(RecognizerIntent.EXTRA_LANGUAGE, "uz-UZ")
            .putExtra(RecognizerIntent.EXTRA_PARTIAL_RESULTS, false)
        try { r.startListening(it) } catch (e: Exception) { again(1500L) }
    }

    private fun again(ms: Long) { if (on) h.postDelayed({ begin() }, ms) }

    // Faqat "Edi, ..." bilan boshlangan gaplar buyruq sifatida yuboriladi
    private fun handle(t: String) {
        val m = wake.find(t) ?: return
        val cmd = t.substring(m.range.last + 1).trim()
        if (cmd.isEmpty()) return
        val w = MainActivity.web ?: return
        w.post { w.evaluateJavascript("window.ediVoice&&window.ediVoice(" + JSONObject.quote(cmd) + ")", null) }
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

        // Blob yuklab olishni ushlab, native saqlashga yo'naltiradi
        const val DL_JS = """(function(){if(window.__ediDl)return;window.__ediDl=1;var o=HTMLAnchorElement.prototype.click;HTMLAnchorElement.prototype.click=function(){var a=this;if(a.download&&a.href&&a.href.indexOf('blob:')===0&&window.Android&&window.Android.saveFile){fetch(a.href).then(function(r){return r.blob()}).then(function(b){var f=new FileReader();f.onloadend=function(){window.Android.saveFile(a.download,b.type||'application/octet-stream',String(f.result).split(',')[1])};f.readAsDataURL(b)});return}return o.apply(this,arguments)}})();"""

        // Orqaga tugmasi: ochiq oynalarni yopadi
        const val CLOSE_JS = """(function(){var m=document.querySelector('.prev-mod.on')||document.querySelector('.modal.on')||document.querySelector('.ocr-mod.on');if(!m)return 0;var b=m.querySelector('.cl,.close,[data-close]');if(b){b.click();return 1}m.classList.remove('on');return 1})()"""
    }

    private lateinit var bridge: Bridge
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

        bridge = Bridge(this, w)
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
            override fun onPageFinished(v: WebView?, url: String?) { v?.evaluateJavascript(DL_JS, null) }

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
        val w = web ?: return
        if ((w.url ?: "").startsWith("file:") && online()) w.loadUrl(URL)
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
import android.content.ContentUris
import android.content.ContentValues
import android.content.Context
import android.content.Intent
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
import android.view.KeyEvent
import android.webkit.JavascriptInterface
import android.webkit.WebView
import android.widget.Toast
import org.json.JSONObject
import java.io.File
import java.util.Locale
import java.util.concurrent.CountDownLatch
import java.util.concurrent.TimeUnit
import java.util.concurrent.atomic.AtomicBoolean

class Bridge(private val activity: MainActivity, private val web: WebView) {
    private val ctx: Context = activity.applicationContext
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
                AlertDialog.Builder(activity).setMessage(msg)
                    .setPositiveButton("Ha") { _, _ -> ok.set(true); latch.countDown() }
                    .setNegativeButton("Yo'q") { _, _ -> latch.countDown() }
                    .setOnCancelListener { latch.countDown() }
                    .show()
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
                    activity.startActivity(i)
                } else {
                    val p = rt[id]
                    if (p == null) {
                        permJs(id, true, false)
                    } else {
                        val c = nextCode++
                        codes[c] = id
                        activity.requestPermissions(arrayOf(p), c)
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
            activity.startActivity(i)
        }
    }

    fun permResult(code: Int, res: IntArray) {
        val id = codes.remove(code) ?: return
        val ok = res.isNotEmpty() && res[0] == PackageManager.PERMISSION_GRANTED
        val p = rt[id]
        val blocked = !ok && p != null && !activity.shouldShowRequestPermissionRationale(p)
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
            try { activity.startActivity(Intent(MediaStore.ACTION_IMAGE_CAPTURE)) }
            catch (e: Exception) { toast("❌ Kamera ochilmadi") }
        }
    }

    @JavascriptInterface
    fun overlay() {
        ui.post {
            val i = Intent(Settings.ACTION_MANAGE_OVERLAY_PERMISSION, Uri.parse("package:" + ctx.packageName))
            activity.startActivity(i)
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
    fun listen() { ui.post { activity.startListen() } }

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
        }
        return "❓ Noma'lum buyruq: " + n
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
