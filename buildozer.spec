[app]

title = WalletCore

package.name = walletcore
package.domain = com.develop4world

source.dir = .
source.include_exts = py,kv,png,jpg,jpeg,json,db,ttf,atlas

version = 1.0.0

requirements = python3,kivy

orientation = portrait
fullscreen = 0

icon.filename = assets/icon.png

android.api = 35
android.minapi = 24
android.archs = arm64-v8a

android.enable_androidx = True
android.allow_backup = True
android.private_storage = True

# ostavi prazno
android.permissions =

# Build
log_level = 2
warn_on_root = 0
