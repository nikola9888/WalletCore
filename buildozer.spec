[app]

title = WalletCore

package.name = walletcore
package.domain = com.develop4world

source.dir = .

source.include_exts = py,png,jpg,jpeg,kv,json,atlas,ttf

version = 1.0.0

requirements = python3,kivy

orientation = portrait
fullscreen = 0

icon.filename = assets/icon.png

presplash.filename =

android.api = 35
android.minapi = 24

android.ndk = 25b

android.archs = arm64-v8a

android.enable_androidx = True

android.private_storage = True

android.allow_backup = True

android.permissions = INTERNET

android.accept_sdk_license = True

log_level = 2

warn_on_root = 0

build_dir = .buildozer

p4a.branch = master

# ------------------------------------
# Buildozer defaults
# ------------------------------------

package.version =

package.version.regex =

package.version.filename =

source.exclude_exts = spec

source.exclude_dirs = tests,.git,__pycache__

source.exclude_patterns =

version.regex =

version.filename =

icon.adaptive_foreground.filename =

icon.adaptive_background.filename =

presplash.color =

presplash.lottie =

android.entrypoint = org.kivy.android.PythonActivity

android.activity_class_name = org.kivy.android.PythonActivity

android.extra_manifest_xml =

android.extra_manifest_application_arguments =

android.gradle_dependencies =

android.add_src =

android.add_aars =

android.add_assets =

android.add_resources =

android.add_jars =

android.add_activities =

android.add_services =

android.add_receivers =

android.add_libs_armeabi =

android.add_libs_arm64_v8a =

android.add_libs_x86 =

android.add_libs_x86_64 =

android.copy_libs = 1

android.release_artifact = apk

android.debug_symbols = 0

android.numeric_version = 100

android.manifest.intent_filters =

android.manifest.launch_mode = singleTask

android.wakelock = False

android.meta_data =

android.library_references =

services =

ios.kivy_ios_url = https://github.com/kivy/kivy-ios

ios.kivy_ios_branch = master
