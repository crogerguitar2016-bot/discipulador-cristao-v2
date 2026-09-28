[app]

title = Discipulador Cristão V2

package.name = discipuladorcristaov2
package.domain = com.croger

source.dir = .

source.include_exts = py,png,jpg,jpeg,kv,atlas,txt,json,java,xml

source.exclude_dirs = .git,.buildozer,bin,__pycache__

version = 1.0.0

requirements = python3,kivy,pyjnius

orientation = portrait

fullscreen = 0

icon.filename = %(source.dir)s/icon.png


# ==========================================================
# ANDROID
# ==========================================================

android.api = 36
android.minapi = 24

android.ndk = 29

android.archs = arm64-v8a

android.permissions = READ_CONTACTS,SYSTEM_ALERT_WINDOW

android.accept_sdk_license = True

android.add_src = android_src
android.extra_manifest_application_arguments = android_res/extra_application.xml

p4a.branch = develop
p4a.source_dir = /home/runner/p4a


[buildozer]

log_level = 2

warn_on_root = 1
