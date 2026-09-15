[app]

title = WalletCore

package.name = walletcore
package.domain = com.develop4world

source.dir = .

source.include_exts = py,png,jpg,jpeg,kv,json,atlas,ttf

version = 1.1.4
android.numeric_version = 102410107

requirements = python3,kivy,reportlab

# Python for Android
# API 36 / Google Play builds use the current p4a development branch.
p4a.branch = develop
p4a.python_version = 3.14

orientation = portrait

fullscreen = 1

icon.filename = assets/icon.png

# Android / Google Play
android.api = 36
android.minapi = 24
android.build_tools_version = 36.0.0
android.accept_sdk_license = True
android.ndk = 29
android.archs = arm64-v8a
android.release_artifact = aab

android.enable_androidx = True
android.gradle_dependencies = androidx.core:core:1.13.1
android.res_xml = android_res/file_paths.xml
android.extra_manifest_application_xml = android_res/fileprovider.xml
android.private_storage = True
android.allow_backup = True

# Permissions (dodaj po potrebi)
# android.permissions = INTERNET

[buildozer]
log_level = 2
warn_on_root = 0
