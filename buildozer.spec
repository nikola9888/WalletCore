[app]

title = WalletCore

package.name = walletcore
package.domain = com.develop4world

source.dir = .

source.include_exts = py,png,jpg,jpeg,kv,json,atlas,ttf

version = 1.0.0

icon.filename = assets/icon.png

orientation = portrait

fullscreen = 0


# Python + Kivy
requirements = python3,kivy


# Android
android.api = 35

android.minapi = 24

android.sdk_path = /usr/local/lib/android/sdk

android.ndk_path = /usr/local/lib/android/sdk/ndk/25.2.9519653

android.ndk = 25.2.9519653

android.archs = arm64-v8a

android.build_tools_version = 35.0.0


# Permissions
android.permissions = INTERNET


# AndroidX
android.enable_androidx = True


# Storage
android.private_storage = True

android.allow_backup = True


# Build settings
android.accept_sdk_license = True

android.add_src = .


# Logs
log_level = 2

warn_on_root = 0
