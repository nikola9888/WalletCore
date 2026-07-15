[app]

# (str) Title of your application
title = WalletCore

# (str) Package name
package.name = walletcore

# (str) Package domain
package.domain = com.develop4world

# (str) Source code directory
source.dir = .

# (list) Source files to include
source.include_exts = py,png,jpg,jpeg,kv,atlas,json

# (str) Application version
version = 1.0.0


# (str) Icon
icon.filename = assets/icon.png


# (str) Supported orientation
orientation = portrait


# (bool) Fullscreen mode
fullscreen = 0


# (str) Requirements
requirements = python3,kivy


# (str) Presplash
# presplash.filename = %(source.dir)s/assets/presplash.png


# (list) Permissions
android.permissions = WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE


# (int) Android API
android.api = 35

# (int) Minimum Android API
android.minapi = 24


# (str) Android NDK version
android.ndk = 25b


# (list) Architectures
android.archs = arm64-v8a,armeabi-v7a


# (bool) Backup app data
android.allow_backup = True

# =========================================================
# Android configuration
# =========================================================

# (str) Android activity
# android.entrypoint = org.kivy.android.PythonActivity


# (str) Android private storage
android.private_storage = True


# (bool) Use AndroidX
android.enable_androidx = True


# (bool) Use legacy support
android.enable_legacy = False


# (str) Android permissions
# dodatne dozvole dodaj ovde ako budu potrebne
# android.permissions = INTERNET,CAMERA


# =========================================================
# Build configuration
# =========================================================

[buildozer]

# (int) Log level
log_level = 2


# (bool) Warn when running as root
warn_on_root = 1


# =========================================================
# Python-for-Android settings
# =========================================================

# (str) Branch of python-for-android
# p4a.branch = master


# (str) Android bootstrap
# p4a.bootstrap = sdl2


# =========================================================
# iOS settings (nije potrebno za Android)
# =========================================================

[buildozer:ios]

# iOS configuration placeholder

# =========================================================
# Advanced Android options
# =========================================================

# (str) Android SDK path
# android.sdk_path =


# (str) Android NDK path
# android.ndk_path =


# (str) Android build tools
# ostavljamo prazno da Buildozer sam izabere kompatibilnu verziju
# android.build_tools_version =


# (int) Android SDK target
android.api = 35


# (int) Minimum Android version
android.minapi = 24


# =========================================================
# Packaging options
# =========================================================

# Copy libraries into APK
android.copy_libs = 1


# Enable debug symbols during development
android.debug_artifact = apk


# =========================================================
# Gradle options
# =========================================================

# Use modern Gradle
# android.gradle_dependencies =


# =========================================================
# Application metadata
# =========================================================

# (str) Application name
presplash.color = #0B3B66


# =========================================================
# Exclude unnecessary files
# =========================================================

# Do not include these folders in APK
exclude_dirs = .git,.github,__pycache__,.buildozer


# =========================================================
# Backup
# =========================================================

android.allow_backup = True

# (str) List of service to include
# services = NAME:ENTRYPOINT_TO_PY

# (str) Presplash of the application
#presplash.filename = %(source.dir)s/data/presplash.png

# (str) Icon of the application
#icon.filename = %(source.dir)s/assets/icon.png


[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug)
log_level = 2

# (bool) Warn users if a newer version of buildozer is available
warn_on_root = 1


# Android build settings

android.accept_sdk_license = True

android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

android.archs = arm64-v8a,armeabi-v7a

# Use AndroidX
android.enable_androidx = True


# Gradle
android.gradle_dependencies =


# Copy assets
android.add_src = assets


# Keystore (later for Play Store)
# android.release_artifact = .keystore
