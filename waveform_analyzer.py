import customtkinter as ctk
from tkinter import filedialog, messagebox
import subprocess
import os
import sys
import threading
import concurrent.futures
import webbrowser
from PIL import Image, ImageTk
import shutil
import tempfile
import wave
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import json
import urllib.request
import urllib.error
import pyloudnorm as pyln
import scipy.signal


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)


APP_NAME = "MO Audio Waveform Analyzer"
APP_VERSION = "1.0"
DEVELOPER_NAME = "Murat Ogras"
WEBSITE_URL = "https://www.mrtogras.com"
GITHUB_URL = "https://github.com/MrTOgRaS/"
SUPPORT_EMAIL = "destek@mrtogras.com"
SUPPORT_URL = "https://mrtogras.com/support/"

UPDATE_CHECK_URL = "https://www.mrtogras.com/moaudiowaveformanalyzer/version.json"
UPDATE_CHECK_TIMEOUT = 6

MIT_LICENSE_TEXT = """MIT License

Copyright (c) 2026 Murat Ogras (MrTOgRaS)

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

ICON_PATH = resource_path(os.path.join("assets", "app_icon.ico"))
LOGO_PATH = resource_path(os.path.join("assets", "logo.png"))

LANG_DISPLAY_NAMES = {"en": "English", "tr": "Türkçe", "de": "Deutsch"}
LANG_CODES_BY_DISPLAY = {v: k for k, v in LANG_DISPLAY_NAMES.items()}

CHANNEL_KEYS = [1, 2, 6, 8]
MODE_KEYS = ["overlay", "stacked", "separate", "spectrogram"]
LUFS_MODE_KEYS = ["fast", "full"]

SPECTROGRAM_SR = 16000
SPECTROGRAM_NFFT = 2048
SPECTROGRAM_COLUMNS = 1200

LUFS_MAX_DURATION_SECONDS = 1200

CHANNEL_NAME_MAP = {
    "tr": {
        2: ["Sol (L)", "Sağ (R)"],
        6: ["Sol (FL)", "Sağ (FR)", "Merkez (FC)", "LFE (Sub)", "Arka Sol (BL)", "Arka Sağ (BR)"],
        8: ["Sol (FL)", "Sağ (FR)", "Merkez (FC)", "LFE (Sub)", "Arka Sol (BL)", "Arka Sağ (BR)", "Yan Sol (SL)", "Yan Sağ (SR)"],
    },
    "en": {
        2: ["Left (L)", "Right (R)"],
        6: ["Left (FL)", "Right (FR)", "Center (FC)", "LFE (Sub)", "Rear Left (BL)", "Rear Right (BR)"],
        8: ["Left (FL)", "Right (FR)", "Center (FC)", "LFE (Sub)", "Rear Left (BL)", "Rear Right (BR)", "Side Left (SL)", "Side Right (SR)"],
    },
    "de": {
        2: ["Links (L)", "Rechts (R)"],
        6: ["Links (FL)", "Rechts (FR)", "Mitte (FC)", "LFE (Sub)", "Hinten Links (BL)", "Hinten Rechts (BR)"],
        8: ["Links (FL)", "Rechts (FR)", "Mitte (FC)", "LFE (Sub)", "Hinten Links (BL)", "Hinten Rechts (BR)", "Seite Links (SL)", "Seite Rechts (SR)"],
    },
}

TRANSLATIONS = {
    "tr": {
        "app_short_name": "MO Audio Waveform Analyzer",
        "window_title": "MO Audio Waveform Analyzer - İstatistiksel Karşılaştırma",
        "btn_file1": "1. Ses Dosyasını Seç",
        "lbl_file1_empty": "Dosya 1: Seçilmedi",
        "lbl_file1_selected": "Dosya 1: {name}",
        "btn_file2": "2. Ses Dosyasını Seç (Kıyaslama İçin)",
        "lbl_file2_empty": "Dosya 2: Seçilmedi",
        "lbl_file2_selected": "Dosya 2: {name}",
        "lbl_channel_output": "Kanal Çıktısı:",
        "channel_opt_1": "1 Kanal (Mono)",
        "channel_opt_2": "2 Kanal (Stereo)",
        "channel_opt_6": "6 Kanal (5.1)",
        "channel_opt_8": "8 Kanal (7.1)",
        "lbl_view_mode": "Görünüm Modu:",
        "mode_opt_overlay": "Üst Üste Bindir (Kıyasla)",
        "mode_opt_stacked": "Alt Alta Çiz (Kıyasla)",
        "mode_opt_separate": "Kanalları Ayır (Sadece Dosya 1)",
        "mode_opt_spectrogram": "Spektrogram (Frekans Analizi)",
        "lufs_mode_label": "LUFS Ölçümü:",
        "lufs_mode_opt_fast": "Hızlı (Kesit)",
        "lufs_mode_opt_full": "Tam (Tüm Dosya)",
        "btn_analyze": "ANALİZ ET VE RAPORLA",
        "btn_analyzing": "ANALİZ EDİLİYOR...",
        "btn_save": "PNG Kaydet",
        "placeholder_report": "Bilgisayar Analizi: Dosyalar seçildikten sonra teknik istatistikler burada belirecektir.\n",
        "lbl_img_placeholder": "Ayarları yapın ve analizi başlatın.",
        "processing_text": "Gelişmiş veri analizi yapılıyor (LUFS ölçümü uzun dosyalarda bir dakikaya kadar sürebilir)...",
        "processing_report_text": "Veriler işleniyor, matematiksel analiz yapılıyor...",
        "warn_title": "Uyarı",
        "warn_no_file": "Lütfen en az 1. Ses Dosyasını seçin!",
        "error_img_prefix": "Analiz sırasında hata oluştu:\n{err}",
        "error_report_prefix": "Hata: {err}",
        "save_dialog_title": "Raporu Kaydet",
        "save_success_title": "Başarılı",
        "save_success_msg": "Rapor başarıyla kaydedildi!",
        "save_error_title": "Hata",
        "save_error_msg": "Kaydedilemedi:\n{err}",
        "no_report_yet": "Kaydedilecek bir rapor bulunamadı. Önce analiz yapın.",
        "unknown": "Bilinmiyor",
        "report_file1": "[DOSYA 1 - {name}]\nFormat: {codec} | Bitrate: {br} kbps | Peak: {peak:.2f} dB | RMS (Gürlük): {rms:.2f} dB | Dinamik Aralık: {dr:.2f} dB\n",
        "report_file2": "[DOSYA 2 - {name}]\nFormat: {codec} | Bitrate: {br} kbps | Peak: {peak:.2f} dB | RMS (Gürlük): {rms:.2f} dB | Dinamik Aralık: {dr:.2f} dB\n",
        "report_lufs_line": "Bütünleşik Gürlük: {i:.2f} LUFS | True Peak: {tp:.2f} dBTP{note}\n",
        "lufs_excerpt_note": " (ortadan {mins} dk'lık kesitten ölçüldü)",
        "ai_lufs_similar": ">> EBU R128 bütünleşik gürlük değerleri neredeyse aynı (yayın standardına göre).\n",
        "ai_lufs_file1_louder": ">> EBU R128 standardına göre Dosya 1, Dosya 2'den {diff:.1f} LU daha gürültülü.\n",
        "ai_lufs_file2_louder": ">> EBU R128 standardına göre Dosya 2, Dosya 1'den {diff:.1f} LU daha gürültülü.\n",
        "chart_spectrogram_title": "Spektrogram: {name}",
        "chart_spectrogram_freq_axis": "Frekans (Hz)",
        "chart_spectrogram_mono_note": "(Mono İndirgeme, {sr} Hz)",
        "ai_header": "[YAPAY ZEKA YORUMU]:\n",
        "ai_almost_identical": ">> İki dosya dinamik olarak neredeyse aynı. Her iki dijital platform da muhtemelen aynı stüdyo miksini (Master) kullanmış.\n",
        "ai_file1_slightly_louder": ">> Not: Dosya 1 (Peak: {peak:.2f}), Dosya 2'ye göre çok hafif daha yüksek bir volume seviyesiyle kodlanmış.",
        "ai_file2_slightly_louder": ">> Not: Dosya 2 (Peak: {peak:.2f}), Dosya 1'e göre çok hafif daha yüksek bir volume seviyesiyle kodlanmış.",
        "ai_file1_wider_dr": ">> Dosya 1'in Dinamik Aralığı daha geniş. (Daha az sıkıştırılmış, sinematik patlamalar daha vurucu olabilir).\n",
        "ai_file2_wider_dr": ">> Dosya 2'nin Dinamik Aralığı daha geniş. (Daha az sıkıştırılmış, sinematik patlamalar daha vurucu olabilir).\n",
        "ai_file1_louder": ">> Dosya 1 bariz şekilde daha gürültülü (louder). Platform özel bir 'Night Mode/DRC' uygulamış olabilir.",
        "ai_file2_louder": ">> Dosya 2 bariz şekilde daha gürültülü (louder). Platform özel bir 'Night Mode/DRC' uygulamış olabilir.",
        "chart_channel_title": "Kanal Analizi: {name}",
        "chart_channel_generic": "Kanal {i}",
        "chart_time_axis": "Zaman (Saat:Dakika:Saniye)",
        "chart_time_axis_short": "Zaman",
        "chart_general_title": "Genel Karışım Analizi | Çıktı: {ch}",
        "chart_amplitude": "Genlik",
        "file1_label": "Dosya 1",
        "file2_label": "Dosya 2",
        "about_btn": "ℹ️ Hakkında",
        "about_title": "Hakkında",
        "about_version": "Versiyon {v} — MrTOgRaS",
        "about_developer": "👤 Geliştirici: {dev}",
        "about_website": "🌐 Web Sitesi",
        "about_github": "🐙 GitHub Page",
        "about_email": "📧 E-Posta",
        "about_support": "❤ Destek Ol",
        "about_close": "Kapat",
        "about_check_updates": "🔄 Güncellemeleri Kontrol Et",
        "about_license": "📄 MIT Lisansı",
        "license_window_title": "MIT Lisansı",
        "about_checking_updates": "Kontrol ediliyor...",
        "update_available_title": "Güncelleme Mevcut",
        "update_available_msg": "Yeni bir sürüm mevcut: {version}\n\nİndirme sayfasını açmak ister misiniz?",
        "update_uptodate_title": "Güncel",
        "update_uptodate_msg": "En güncel sürümü kullanıyorsunuz ({version}).",
        "update_check_failed_title": "Güncelleme Kontrolü Başarısız",
        "update_check_failed_msg": "Güncellemeler kontrol edilemedi:\n{err}",
        "lang_label": "🌐 Dil:",
        "link_open_error": "Bağlantı açılamadı:\n{err}",
    },
    "en": {
        "app_short_name": "MO Audio Waveform Analyzer",
        "window_title": "MO Audio Waveform Analyzer - Statistical Comparison",
        "btn_file1": "1. Select Audio File",
        "lbl_file1_empty": "File 1: Not selected",
        "lbl_file1_selected": "File 1: {name}",
        "btn_file2": "2. Select Audio File (for comparison)",
        "lbl_file2_empty": "File 2: Not selected",
        "lbl_file2_selected": "File 2: {name}",
        "lbl_channel_output": "Channel Output:",
        "channel_opt_1": "1 Channel (Mono)",
        "channel_opt_2": "2 Channels (Stereo)",
        "channel_opt_6": "6 Channels (5.1)",
        "channel_opt_8": "8 Channels (7.1)",
        "lbl_view_mode": "View Mode:",
        "mode_opt_overlay": "Overlay (Compare)",
        "mode_opt_stacked": "Stacked (Compare)",
        "mode_opt_separate": "Separate Channels (File 1 only)",
        "mode_opt_spectrogram": "Spectrogram (Frequency Analysis)",
        "lufs_mode_label": "LUFS Measurement:",
        "lufs_mode_opt_fast": "Fast (Excerpt)",
        "lufs_mode_opt_full": "Full (Entire File)",
        "btn_analyze": "ANALYZE & REPORT",
        "btn_analyzing": "ANALYZING...",
        "btn_save": "Save PNG",
        "placeholder_report": "Computer Analysis: Technical statistics will appear here once files are selected.\n",
        "lbl_img_placeholder": "Adjust the settings and start the analysis.",
        "processing_text": "Performing advanced analysis (LUFS measurement can take up to a minute for long files)...",
        "processing_report_text": "Processing data, running mathematical analysis...",
        "warn_title": "Warning",
        "warn_no_file": "Please select at least File 1!",
        "error_img_prefix": "An error occurred during analysis:\n{err}",
        "error_report_prefix": "Error: {err}",
        "save_dialog_title": "Save Report",
        "save_success_title": "Success",
        "save_success_msg": "Report saved successfully!",
        "save_error_title": "Error",
        "save_error_msg": "Could not save:\n{err}",
        "no_report_yet": "No report to save yet. Run an analysis first.",
        "unknown": "Unknown",
        "report_file1": "[FILE 1 - {name}]\nFormat: {codec} | Bitrate: {br} kbps | Peak: {peak:.2f} dB | RMS (Loudness): {rms:.2f} dB | Dynamic Range: {dr:.2f} dB\n",
        "report_file2": "[FILE 2 - {name}]\nFormat: {codec} | Bitrate: {br} kbps | Peak: {peak:.2f} dB | RMS (Loudness): {rms:.2f} dB | Dynamic Range: {dr:.2f} dB\n",
        "report_lufs_line": "Integrated Loudness: {i:.2f} LUFS | True Peak: {tp:.2f} dBTP{note}\n",
        "lufs_excerpt_note": " (measured from a centered {mins}-min excerpt)",
        "ai_lufs_similar": ">> EBU R128 integrated loudness values are nearly identical (broadcast-standard comparison).\n",
        "ai_lufs_file1_louder": ">> By EBU R128 standard, File 1 is {diff:.1f} LU louder than File 2.\n",
        "ai_lufs_file2_louder": ">> By EBU R128 standard, File 2 is {diff:.1f} LU louder than File 1.\n",
        "chart_spectrogram_title": "Spectrogram: {name}",
        "chart_spectrogram_freq_axis": "Frequency (Hz)",
        "chart_spectrogram_mono_note": "(Mono Downmix, {sr} Hz)",
        "ai_header": "[AI ANALYSIS]:\n",
        "ai_almost_identical": ">> The two files are dynamically almost identical. Both digital platforms likely used the same studio mix (master).\n",
        "ai_file1_slightly_louder": ">> Note: File 1 (Peak: {peak:.2f}) was encoded at a slightly higher volume level than File 2.",
        "ai_file2_slightly_louder": ">> Note: File 2 (Peak: {peak:.2f}) was encoded at a slightly higher volume level than File 1.",
        "ai_file1_wider_dr": ">> File 1 has a wider Dynamic Range. (Less compressed, cinematic peaks may hit harder).\n",
        "ai_file2_wider_dr": ">> File 2 has a wider Dynamic Range. (Less compressed, cinematic peaks may hit harder).\n",
        "ai_file1_louder": ">> File 1 is noticeably louder. The platform may have applied a 'Night Mode/DRC'.",
        "ai_file2_louder": ">> File 2 is noticeably louder. The platform may have applied a 'Night Mode/DRC'.",
        "chart_channel_title": "Channel Analysis: {name}",
        "chart_channel_generic": "Channel {i}",
        "chart_time_axis": "Time (H:M:S)",
        "chart_time_axis_short": "Time",
        "chart_general_title": "General Mix Analysis | Output: {ch}",
        "chart_amplitude": "Amplitude",
        "file1_label": "File 1",
        "file2_label": "File 2",
        "about_btn": "ℹ️ About",
        "about_title": "About",
        "about_version": "Version {v} — MrTOgRaS",
        "about_developer": "👤 Developer: {dev}",
        "about_website": "🌐 Website",
        "about_github": "🐙 GitHub Page",
        "about_email": "📧 Email",
        "about_support": "❤ Support Us",
        "about_close": "Close",
        "about_check_updates": "🔄 Check for Updates",
        "about_license": "📄 MIT License",
        "license_window_title": "MIT License",
        "about_checking_updates": "Checking...",
        "update_available_title": "Update Available",
        "update_available_msg": "A new version is available: {version}\n\nWould you like to open the download page?",
        "update_uptodate_title": "Up to Date",
        "update_uptodate_msg": "You are using the latest version ({version}).",
        "update_check_failed_title": "Update Check Failed",
        "update_check_failed_msg": "Could not check for updates:\n{err}",
        "lang_label": "🌐 Language:",
        "link_open_error": "Could not open link:\n{err}",
    },
    "de": {
        "app_short_name": "MO Audio Waveform Analyzer",
        "window_title": "MO Audio Waveform Analyzer - Statistischer Vergleich",
        "btn_file1": "1. Audiodatei auswählen",
        "lbl_file1_empty": "Datei 1: Nicht ausgewählt",
        "lbl_file1_selected": "Datei 1: {name}",
        "btn_file2": "2. Audiodatei auswählen (zum Vergleich)",
        "lbl_file2_empty": "Datei 2: Nicht ausgewählt",
        "lbl_file2_selected": "Datei 2: {name}",
        "lbl_channel_output": "Kanalausgabe:",
        "channel_opt_1": "1 Kanal (Mono)",
        "channel_opt_2": "2 Kanäle (Stereo)",
        "channel_opt_6": "6 Kanäle (5.1)",
        "channel_opt_8": "8 Kanäle (7.1)",
        "lbl_view_mode": "Ansichtsmodus:",
        "mode_opt_overlay": "Überlagern (Vergleichen)",
        "mode_opt_stacked": "Untereinander (Vergleichen)",
        "mode_opt_separate": "Kanäle trennen (Nur Datei 1)",
        "mode_opt_spectrogram": "Spektrogramm (Frequenzanalyse)",
        "lufs_mode_label": "LUFS-Messung:",
        "lufs_mode_opt_fast": "Schnell (Ausschnitt)",
        "lufs_mode_opt_full": "Vollständig (Gesamte Datei)",
        "btn_analyze": "ANALYSIEREN & BERICHT",
        "btn_analyzing": "ANALYSIERE...",
        "btn_save": "PNG speichern",
        "placeholder_report": "Computeranalyse: Technische Statistiken erscheinen hier, sobald Dateien ausgewählt wurden.\n",
        "lbl_img_placeholder": "Einstellungen anpassen und Analyse starten.",
        "processing_text": "Erweiterte Analyse läuft (LUFS-Messung kann bei langen Dateien bis zu einer Minute dauern)...",
        "processing_report_text": "Daten werden verarbeitet, mathematische Analyse läuft...",
        "warn_title": "Warnung",
        "warn_no_file": "Bitte wählen Sie mindestens Datei 1 aus!",
        "error_img_prefix": "Bei der Analyse ist ein Fehler aufgetreten:\n{err}",
        "error_report_prefix": "Fehler: {err}",
        "save_dialog_title": "Bericht speichern",
        "save_success_title": "Erfolg",
        "save_success_msg": "Bericht erfolgreich gespeichert!",
        "save_error_title": "Fehler",
        "save_error_msg": "Konnte nicht gespeichert werden:\n{err}",
        "no_report_yet": "Noch kein Bericht zum Speichern vorhanden. Führen Sie zuerst eine Analyse durch.",
        "unknown": "Unbekannt",
        "report_file1": "[DATEI 1 - {name}]\nFormat: {codec} | Bitrate: {br} kbps | Peak: {peak:.2f} dB | RMS (Lautheit): {rms:.2f} dB | Dynamikumfang: {dr:.2f} dB\n",
        "report_file2": "[DATEI 2 - {name}]\nFormat: {codec} | Bitrate: {br} kbps | Peak: {peak:.2f} dB | RMS (Lautheit): {rms:.2f} dB | Dynamikumfang: {dr:.2f} dB\n",
        "report_lufs_line": "Integrierte Lautheit: {i:.2f} LUFS | True Peak: {tp:.2f} dBTP{note}\n",
        "lufs_excerpt_note": " (aus einem zentrierten {mins}-Min-Ausschnitt gemessen)",
        "ai_lufs_similar": ">> Die integrierten EBU-R128-Lautheitswerte sind nahezu identisch (Broadcast-Standard-Vergleich).\n",
        "ai_lufs_file1_louder": ">> Nach EBU-R128-Standard ist Datei 1 um {diff:.1f} LU lauter als Datei 2.\n",
        "ai_lufs_file2_louder": ">> Nach EBU-R128-Standard ist Datei 2 um {diff:.1f} LU lauter als Datei 1.\n",
        "chart_spectrogram_title": "Spektrogramm: {name}",
        "chart_spectrogram_freq_axis": "Frequenz (Hz)",
        "chart_spectrogram_mono_note": "(Mono-Abmischung, {sr} Hz)",
        "ai_header": "[KI-ANALYSE]:\n",
        "ai_almost_identical": ">> Die beiden Dateien sind dynamisch nahezu identisch. Beide digitalen Plattformen haben wahrscheinlich denselben Studiomix (Master) verwendet.\n",
        "ai_file1_slightly_louder": ">> Hinweis: Datei 1 (Peak: {peak:.2f}) wurde mit einer etwas höheren Lautstärke als Datei 2 kodiert.",
        "ai_file2_slightly_louder": ">> Hinweis: Datei 2 (Peak: {peak:.2f}) wurde mit einer etwas höheren Lautstärke als Datei 1 kodiert.",
        "ai_file1_wider_dr": ">> Datei 1 hat einen größeren Dynamikumfang. (Weniger komprimiert, filmische Höhepunkte können stärker wirken).\n",
        "ai_file2_wider_dr": ">> Datei 2 hat einen größeren Dynamikumfang. (Weniger komprimiert, filmische Höhepunkte können stärker wirken).\n",
        "ai_file1_louder": ">> Datei 1 ist deutlich lauter. Die Plattform hat möglicherweise einen 'Nachtmodus/DRC' angewendet.",
        "ai_file2_louder": ">> Datei 2 ist deutlich lauter. Die Plattform hat möglicherweise einen 'Nachtmodus/DRC' angewendet.",
        "chart_channel_title": "Kanalanalyse: {name}",
        "chart_channel_generic": "Kanal {i}",
        "chart_time_axis": "Zeit (Std:Min:Sek)",
        "chart_time_axis_short": "Zeit",
        "chart_general_title": "Allgemeine Mix-Analyse | Ausgabe: {ch}",
        "chart_amplitude": "Amplitude",
        "file1_label": "Datei 1",
        "file2_label": "Datei 2",
        "about_btn": "ℹ️ Über",
        "about_title": "Über",
        "about_version": "Version {v} — MrTOgRaS",
        "about_developer": "👤 Entwickler: {dev}",
        "about_website": "🌐 Webseite",
        "about_github": "🐙 GitHub-Seite",
        "about_email": "📧 E-Mail",
        "about_support": "❤ Unterstützen",
        "about_close": "Schließen",
        "about_check_updates": "🔄 Nach Updates suchen",
        "about_license": "📄 MIT-Lizenz",
        "license_window_title": "MIT-Lizenz",
        "about_checking_updates": "Wird geprüft...",
        "update_available_title": "Update verfügbar",
        "update_available_msg": "Eine neue Version ist verfügbar: {version}\n\nMöchten Sie die Download-Seite öffnen?",
        "update_uptodate_title": "Aktuell",
        "update_uptodate_msg": "Sie verwenden die neueste Version ({version}).",
        "update_check_failed_title": "Update-Prüfung fehlgeschlagen",
        "update_check_failed_msg": "Updates konnten nicht überprüft werden:\n{err}",
        "lang_label": "🌐 Sprache:",
        "link_open_error": "Link konnte nicht geöffnet werden:\n{err}",
    },
}

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


class AudioAnalyzerApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.lang = "en"
        self.file1_path = None
        self.file2_path = None
        self.is_analyzing = False
        self.has_result = False
        self._checking_updates = False

        self.current_channel_key = CHANNEL_KEYS[2]
        self.current_mode_key = MODE_KEYS[2]
        self.current_lufs_mode_key = LUFS_MODE_KEYS[0]

        self.temp_wav1 = os.path.join(tempfile.gettempdir(), "temp_audio_1.wav")
        self.temp_wav2 = os.path.join(tempfile.gettempdir(), "temp_audio_2.wav")
        self.temp_wav_spec1 = os.path.join(tempfile.gettempdir(), "temp_audio_spec_1.wav")
        self.temp_wav_spec2 = os.path.join(tempfile.gettempdir(), "temp_audio_spec_2.wav")
        self.temp_wav_lufs1 = os.path.join(tempfile.gettempdir(), "temp_audio_lufs_1.wav")
        self.temp_wav_lufs2 = os.path.join(tempfile.gettempdir(), "temp_audio_lufs_2.wav")
        self.temp_img_path = os.path.join(tempfile.gettempdir(), "waveform_plot_output.png")

        self.geometry("1100x880")
        self.minsize(950, 820)

        self._apply_window_icon(self)
        self._build_ui()
        self.apply_language(self.lang)

    def _apply_window_icon(self, window):
        try:
            if os.path.exists(ICON_PATH):
                window.iconbitmap(ICON_PATH)
                return
        except Exception:
            pass
        try:
            if os.path.exists(LOGO_PATH):
                icon_img = ImageTk.PhotoImage(Image.open(LOGO_PATH))
                window.iconphoto(True, icon_img)
                if not hasattr(window, "_icon_keepalive"):
                    window._icon_keepalive = []
                window._icon_keepalive.append(icon_img)
        except Exception:
            pass

    def t(self, key, **kwargs):
        text = TRANSLATIONS[self.lang].get(key, key)
        return text.format(**kwargs) if kwargs else text

    def get_channel_display_values(self):
        return [self.t(f"channel_opt_{k}") for k in CHANNEL_KEYS]

    def get_mode_display_values(self):
        return [self.t(f"mode_opt_{k}") for k in MODE_KEYS]

    def get_lufs_mode_display_values(self):
        return [self.t(f"lufs_mode_opt_{k}") for k in LUFS_MODE_KEYS]

    def _build_ui(self):
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.pack(pady=(10, 0), padx=10, fill="x")
        self.header_frame.grid_columnconfigure(0, weight=1)

        self.lbl_lang = ctk.CTkLabel(self.header_frame, text="")
        self.lbl_lang.grid(row=0, column=1, padx=(0, 5))

        self.lang_menu = ctk.CTkOptionMenu(
            self.header_frame,
            values=list(LANG_DISPLAY_NAMES.values()),
            width=110,
            command=self._on_language_selected,
        )
        self.lang_menu.grid(row=0, column=2, padx=(0, 10))

        self.btn_about = ctk.CTkButton(
            self.header_frame, text="", width=120, fg_color="#5a6268", hover_color="#454d55",
            command=self.show_about_window,
        )
        self.btn_about.grid(row=0, column=3)

        self.top_frame = ctk.CTkFrame(self)
        self.top_frame.pack(pady=10, padx=10, fill="x")

        self.btn_file1 = ctk.CTkButton(self.top_frame, text="", command=lambda: self.select_file(1), width=150)
        self.btn_file1.grid(row=0, column=0, padx=10, pady=10)
        self.lbl_file1 = ctk.CTkLabel(self.top_frame, text="", text_color="gray")
        self.lbl_file1.grid(row=0, column=1, sticky="w")

        self.btn_file2 = ctk.CTkButton(self.top_frame, text="", command=lambda: self.select_file(2), width=150, fg_color="#5a6268", hover_color="#454d55")
        self.btn_file2.grid(row=1, column=0, padx=10, pady=10)
        self.lbl_file2 = ctk.CTkLabel(self.top_frame, text="", text_color="gray")
        self.lbl_file2.grid(row=1, column=1, sticky="w")

        self.settings_frame = ctk.CTkFrame(self)
        self.settings_frame.pack(pady=5, padx=10, fill="x")

        self.lbl_channel = ctk.CTkLabel(self.settings_frame, text="")
        self.lbl_channel.grid(row=0, column=0, padx=10, pady=10)
        self.channel_combo = ctk.CTkComboBox(self.settings_frame, values=self.get_channel_display_values(), width=140, command=self._on_channel_selected)
        self.channel_combo.grid(row=0, column=1, padx=5)

        self.lbl_mode = ctk.CTkLabel(self.settings_frame, text="")
        self.lbl_mode.grid(row=0, column=2, padx=10, pady=10)
        self.mode_combo = ctk.CTkComboBox(self.settings_frame, values=self.get_mode_display_values(), width=260, command=self._on_mode_selected)
        self.mode_combo.grid(row=0, column=3, padx=5)

        self.btn_analyze = ctk.CTkButton(self.settings_frame, text="", command=self.start_analysis, font=("Roboto", 13, "bold"), fg_color="#007bff", height=35)
        self.btn_analyze.grid(row=0, column=4, padx=20, pady=10)

        self.btn_save = ctk.CTkButton(self.settings_frame, text="", command=self.save_image, font=("Roboto", 13, "bold"), fg_color="#28a745", hover_color="#218838", state="disabled", width=100, height=35)
        self.btn_save.grid(row=0, column=5, padx=5)

        self.lbl_lufs_mode = ctk.CTkLabel(self.settings_frame, text="")
        self.lbl_lufs_mode.grid(row=1, column=0, padx=10, pady=(0, 10))
        self.lufs_mode_combo = ctk.CTkComboBox(self.settings_frame, values=self.get_lufs_mode_display_values(), width=200, command=self._on_lufs_mode_selected)
        self.lufs_mode_combo.grid(row=1, column=1, padx=5, pady=(0, 10), sticky="w")

        self.progress_bar = ctk.CTkProgressBar(self, mode="indeterminate")

        self.txt_report = ctk.CTkTextbox(self, height=130, font=("Consolas", 13))
        self.txt_report.pack(pady=5, padx=10, fill="x")

        self.img_frame = ctk.CTkFrame(self)
        self.img_frame.pack(pady=10, padx=10, fill="both", expand=True)
        self.lbl_img = ctk.CTkLabel(self.img_frame, text="", font=("Roboto", 14))
        self.lbl_img.pack(pady=20, expand=True)

    def apply_language(self, lang_code):
        self.lang = lang_code
        self.title(self.t("window_title"))

        self.lbl_lang.configure(text=self.t("lang_label"))
        self.lang_menu.set(LANG_DISPLAY_NAMES[lang_code])
        self.btn_about.configure(text=self.t("about_btn"))

        self.btn_file1.configure(text=self.t("btn_file1"))
        self._refresh_file_label(1)
        self.btn_file2.configure(text=self.t("btn_file2"))
        self._refresh_file_label(2)

        self.lbl_channel.configure(text=self.t("lbl_channel_output"))
        channel_values = self.get_channel_display_values()
        self.channel_combo.configure(values=channel_values)
        self.channel_combo.set(channel_values[CHANNEL_KEYS.index(self.current_channel_key)])

        self.lbl_mode.configure(text=self.t("lbl_view_mode"))
        mode_values = self.get_mode_display_values()
        self.mode_combo.configure(values=mode_values)
        self.mode_combo.set(mode_values[MODE_KEYS.index(self.current_mode_key)])

        self.lbl_lufs_mode.configure(text=self.t("lufs_mode_label"))
        lufs_mode_values = self.get_lufs_mode_display_values()
        self.lufs_mode_combo.configure(values=lufs_mode_values)
        self.lufs_mode_combo.set(lufs_mode_values[LUFS_MODE_KEYS.index(self.current_lufs_mode_key)])

        self.btn_analyze.configure(text=self.t("btn_analyzing") if self.is_analyzing else self.t("btn_analyze"))
        self.btn_save.configure(text=self.t("btn_save"))

        if not self.has_result and not self.is_analyzing:
            self.write_report(self.t("placeholder_report"))
            self.lbl_img.configure(text=self.t("lbl_img_placeholder"))

    def _refresh_file_label(self, file_num):
        if file_num == 1:
            if self.file1_path:
                self.lbl_file1.configure(text=self.t("lbl_file1_selected", name=os.path.basename(self.file1_path)), text_color="white")
            else:
                self.lbl_file1.configure(text=self.t("lbl_file1_empty"), text_color="gray")
        else:
            if self.file2_path:
                self.lbl_file2.configure(text=self.t("lbl_file2_selected", name=os.path.basename(self.file2_path)), text_color="white")
            else:
                self.lbl_file2.configure(text=self.t("lbl_file2_empty"), text_color="gray")

    def _on_language_selected(self, display_value):
        code = LANG_CODES_BY_DISPLAY.get(display_value, "tr")
        self.apply_language(code)

    def _on_channel_selected(self, display_value):
        values = self.get_channel_display_values()
        if display_value in values:
            self.current_channel_key = CHANNEL_KEYS[values.index(display_value)]

    def _on_mode_selected(self, display_value):
        values = self.get_mode_display_values()
        if display_value in values:
            self.current_mode_key = MODE_KEYS[values.index(display_value)]

    def _on_lufs_mode_selected(self, display_value):
        values = self.get_lufs_mode_display_values()
        if display_value in values:
            self.current_lufs_mode_key = LUFS_MODE_KEYS[values.index(display_value)]

    def select_file(self, file_num):
        path = filedialog.askopenfilename(
            title=self.t("btn_file1") if file_num == 1 else self.t("btn_file2"),
            filetypes=[("Media Files", "*.ac3 *.eac3 *.aac *.mp3 *.flac *.wav *.mkv *.mp4")],
        )
        if path:
            if file_num == 1:
                self.file1_path = path
            else:
                self.file2_path = path
            self._refresh_file_label(file_num)

    def format_time(self, x, pos):
        mins = int(x // 60)
        secs = int(x % 60)
        if mins >= 60:
            return f"{int(mins // 60)}:{int(mins % 60):02d}:{secs:02d}"
        return f"{mins}:{secs:02d}"

    def get_metadata(self, filepath, lang=None):
        lang = lang or self.lang
        unknown_text = TRANSLATIONS.get(lang, TRANSLATIONS["tr"]).get("unknown", "Unknown")
        cmd = ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", "-show_streams", "-select_streams", "a:0", filepath]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True, timeout=15)
            info = json.loads(result.stdout)
            stream = info.get('streams', [{}])[0]
            codec = stream.get('codec_name', unknown_text).upper()

            bitrate = stream.get('bit_rate')
            if bitrate:
                bitrate = int(bitrate) // 1000
            else:
                tags = stream.get('tags', {})
                bitrate = int(tags.get('BPS', 0)) // 1000

            try:
                duration = float(info.get('format', {}).get('duration'))
            except (TypeError, ValueError):
                duration = None

            return codec, (bitrate if bitrate > 0 else unknown_text), duration
        except Exception:
            return unknown_text, unknown_text, None

    def calculate_stats(self, data):
        data_float = data.astype(np.float64)
        max_amp = np.max(np.abs(data_float))

        peak_db = 20 * np.log10(max_amp / 32768.0) if max_amp > 0 else -99.9
        rms_val = np.sqrt(np.mean(data_float ** 2))
        rms_db = 20 * np.log10(rms_val / 32768.0) if rms_val > 0 else -99.9

        dr = peak_db - rms_db
        return peak_db, rms_db, dr

    def _probe_duration(self, filepath):
        cmd = ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_entries", "format=duration", filepath]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True, timeout=15)
            info = json.loads(result.stdout)
            return float(info["format"]["duration"])
        except Exception:
            return None

    def measure_loudness_ebur128(self, filepath, temp_wav_path, full_measurement=False, known_duration=None):
        try:
            duration = known_duration
            if not full_measurement and duration is None:
                duration = self._probe_duration(filepath)

            seeked = (not full_measurement) and bool(duration) and duration > LUFS_MAX_DURATION_SECONDS
            if seeked:
                start = max(0.0, (duration - LUFS_MAX_DURATION_SECONDS) / 2)
                cmd = ["ffmpeg", "-y", "-ss", f"{start:.3f}", "-i", filepath,
                       "-t", str(LUFS_MAX_DURATION_SECONDS), "-ar", "48000", "-c:a", "pcm_s16le", temp_wav_path]
            else:
                cmd = ["ffmpeg", "-y", "-i", filepath, "-ar", "48000", "-c:a", "pcm_s16le", temp_wav_path]

            subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=180)

            with wave.open(temp_wav_path, 'rb') as wf:
                sr = wf.getframerate()
                n_ch = wf.getnchannels()
                n_total = wf.getnframes()

                max_frames = LUFS_MAX_DURATION_SECONDS * sr
                needs_trim = (not full_measurement) and n_total > max_frames
                if needs_trim:
                    start_frame = (n_total - max_frames) // 2
                    wf.setpos(int(start_frame))
                    n_read = max_frames
                else:
                    n_read = n_total
                raw = wf.readframes(int(n_read))

            truncated = seeked or needs_trim

            pcm = np.frombuffer(raw, dtype=np.int16)
            if n_ch > 1:
                pcm = pcm.reshape(-1, n_ch)

            peak_db, rms_db, dr_db = self.calculate_stats(pcm)
            result = {"peak_db": peak_db, "rms_db": rms_db, "dr_db": dr_db, "lufs": None}

            try:
                data = pcm.astype(np.float32) / 32768.0
                if n_ch in (1, 2):
                    meter_input = data
                elif n_ch in (6, 8):
                    meter_input = data[:, [0, 1, 2, 4, 5]]
                else:
                    meter_input = data[:, :min(2, n_ch)] if data.ndim > 1 else data

                meter = pyln.Meter(sr)
                lufs = meter.integrated_loudness(meter_input)

                peak_data = data if data.ndim > 1 else data.reshape(-1, 1)
                oversampled = scipy.signal.resample_poly(peak_data, 2, 1, axis=0)
                true_peak_lin = float(np.max(np.abs(oversampled))) if oversampled.size else 0.0
                true_peak_db = 20 * np.log10(true_peak_lin) if true_peak_lin > 0 else -99.9

                result["lufs"] = {"i": float(lufs), "tp": true_peak_db, "truncated": truncated}
            except Exception:
                pass

            return result
        except Exception:
            return None
        finally:
            if os.path.exists(temp_wav_path):
                try:
                    os.remove(temp_wav_path)
                except OSError:
                    pass

    def extract_wav(self, input_path, output_wav, channels):
        cmd = ["ffmpeg", "-y", "-i", input_path, "-ac", str(channels), "-ar", "200", "-c:a", "pcm_s16le", output_wav]
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    def extract_wav_mono_for_spectrogram(self, input_path, output_wav):
        cmd = ["ffmpeg", "-y", "-i", input_path, "-ac", "1", "-ar", str(SPECTROGRAM_SR), "-c:a", "pcm_s16le", output_wav]
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    @staticmethod
    def compute_spectrogram_from_wav(wav_path, target_columns=SPECTROGRAM_COLUMNS, nfft=SPECTROGRAM_NFFT):
        with wave.open(wav_path, 'rb') as wf:
            sr = wf.getframerate()
            n_total = wf.getnframes()
            nfft = min(nfft, max(2, n_total))
            n_windows = min(target_columns, max(1, n_total // nfft)) if n_total > nfft else 1
            if n_windows <= 1:
                starts = [0]
            else:
                step = (n_total - nfft) / (n_windows - 1)
                starts = [int(i * step) for i in range(n_windows)]

            window = np.hanning(nfft)
            freqs = np.fft.rfftfreq(nfft, d=1.0 / sr)
            spec = np.empty((len(freqs), len(starts)))
            for i, s in enumerate(starts):
                wf.setpos(min(s, max(0, n_total - nfft)))
                raw = wf.readframes(nfft)
                seg = np.frombuffer(raw, dtype=np.int16).astype(np.float64)
                if len(seg) < nfft:
                    seg = np.pad(seg, (0, nfft - len(seg)))
                mag = np.abs(np.fft.rfft(seg * window))
                spec[:, i] = 20 * np.log10(mag + 1e-6)

        times = np.array(starts) / sr
        return freqs, times, spec, sr

    def read_wav(self, wav_path):
        with wave.open(wav_path, 'rb') as wf:
            fs = wf.getframerate()
            n_ch = wf.getnchannels()
            frames = wf.readframes(-1)
            data = np.frombuffer(frames, dtype=np.int16)
            if n_ch > 1:
                data = data.reshape(-1, n_ch)
        return fs, n_ch, data

    @staticmethod
    def downsample_for_plot(time_arr, data_arr, max_points=15000):
        n = len(time_arr)
        if n <= max_points:
            return time_arr, data_arr

        factor = int(np.ceil(n / max_points))
        trimmed = (n // factor) * factor
        if trimmed == 0:
            return time_arr, data_arr

        t_blocks = time_arr[:trimmed].reshape(-1, factor)
        t_out = np.repeat(t_blocks.mean(axis=1), 2)

        if data_arr.ndim == 1:
            d_blocks = data_arr[:trimmed].reshape(-1, factor)
            d_min = d_blocks.min(axis=1)
            d_max = d_blocks.max(axis=1)
            out = np.empty(d_min.size * 2, dtype=data_arr.dtype)
            out[0::2] = d_min
            out[1::2] = d_max
        else:
            ch = data_arr.shape[1]
            d_blocks = data_arr[:trimmed].reshape(-1, factor, ch)
            d_min = d_blocks.min(axis=1)
            d_max = d_blocks.max(axis=1)
            out = np.empty((d_min.shape[0] * 2, ch), dtype=data_arr.dtype)
            out[0::2] = d_min
            out[1::2] = d_max

        return t_out, out

    def write_report(self, text):
        self.txt_report.configure(state="normal")
        self.txt_report.delete("0.0", "end")
        self.txt_report.insert("0.0", text)
        self.txt_report.configure(state="disabled")

    def start_analysis(self):
        if not self.file1_path:
            messagebox.showwarning(self.t("warn_title"), self.t("warn_no_file"))
            return
        if self.is_analyzing:
            return

        self.is_analyzing = True
        self.btn_analyze.configure(state="disabled", text=self.t("btn_analyzing"))
        self.btn_save.configure(state="disabled")
        self.lang_menu.configure(state="disabled")
        self.lbl_img.configure(image="", text=self.t("processing_text"))
        self.write_report(self.t("processing_report_text"))

        self.progress_bar.pack(pady=(0, 5), padx=10, fill="x", before=self.txt_report)
        self.progress_bar.start()

        params = dict(
            file1=self.file1_path,
            file2=self.file2_path,
            target_ch=self.current_channel_key,
            mode_key=self.current_mode_key,
            lufs_mode_key=self.current_lufs_mode_key,
            lang=self.lang,
        )
        thread = threading.Thread(target=self._analysis_worker, kwargs=params, daemon=True)
        thread.start()

    def _safe_after(self, callback):
        try:
            self.after(0, callback)
        except Exception:
            pass

    def _cleanup_temp_wavs(self):
        for w in (self.temp_wav1, self.temp_wav2, self.temp_wav_spec1, self.temp_wav_spec2,
                  self.temp_wav_lufs1, self.temp_wav_lufs2):
            if os.path.exists(w):
                try:
                    os.remove(w)
                except OSError:
                    pass

    def _process_single_file(self, filepath, temp_wav_path, temp_wav_lufs_path, target_ch, lufs_full, lang):
        codec, bitrate, duration = self.get_metadata(filepath, lang)
        self.extract_wav(filepath, temp_wav_path, target_ch)
        fs, n_ch, data = self.read_wav(temp_wav_path)
        time_arr = np.linspace(0, len(data) / fs, num=len(data))

        stats = self.measure_loudness_ebur128(filepath, temp_wav_lufs_path, full_measurement=lufs_full, known_duration=duration)
        if stats:
            peak_db, rms_db, dr_db, lufs = stats["peak_db"], stats["rms_db"], stats["dr_db"], stats["lufs"]
        else:
            peak_db, rms_db, dr_db = self.calculate_stats(data)
            lufs = None

        return {
            "codec": codec, "bitrate": bitrate, "fs": fs, "n_ch": n_ch, "data": data, "time": time_arr,
            "peak_db": peak_db, "rms_db": rms_db, "dr_db": dr_db, "lufs": lufs,
        }

    def _analysis_worker(self, file1, file2, target_ch, mode_key, lufs_mode_key, lang):
        try:
            report_text = self._perform_analysis(file1, file2, target_ch, mode_key, lufs_mode_key, lang)
            self._safe_after(lambda: self._on_analysis_done(report_text))
        except Exception as e:
            err = str(e)
            self._safe_after(lambda: self._on_analysis_error(err))
        finally:
            self._cleanup_temp_wavs()

    def _perform_analysis(self, file1, file2, target_ch, mode_key, lufs_mode_key, lang):
        T = TRANSLATIONS[lang]

        def tt(key, **kwargs):
            text = T.get(key, key)
            return text.format(**kwargs) if kwargs else text

        two_files = bool(file1 and file2) and mode_key != "separate"
        lufs_full = (lufs_mode_key == "full")

        if two_files:
            with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
                fut1 = pool.submit(self._process_single_file, file1, self.temp_wav1, self.temp_wav_lufs1, target_ch, lufs_full, lang)
                fut2 = pool.submit(self._process_single_file, file2, self.temp_wav2, self.temp_wav_lufs2, target_ch, lufs_full, lang)
                res1, res2 = fut1.result(), fut2.result()
        else:
            res1 = self._process_single_file(file1, self.temp_wav1, self.temp_wav_lufs1, target_ch, lufs_full, lang)
            res2 = None

        codec1, br1, ch1, data1, time1 = res1["codec"], res1["bitrate"], res1["n_ch"], res1["data"], res1["time"]
        p1, r1, dr1 = res1["peak_db"], res1["rms_db"], res1["dr_db"]
        lufs1 = res1["lufs"]
        name1 = os.path.basename(file1)

        report_text = tt("report_file1", name=name1, codec=codec1, br=br1, peak=p1, rms=r1, dr=dr1)
        if lufs1:
            note1 = tt("lufs_excerpt_note", mins=LUFS_MAX_DURATION_SECONDS // 60) if lufs1["truncated"] else ""
            report_text += tt("report_lufs_line", i=lufs1["i"], tp=lufs1["tp"], note=note1)

        ch2 = data2 = time2 = None
        name2 = os.path.basename(file2) if file2 else None
        lufs2 = None
        if two_files:
            codec2, br2, ch2, data2, time2 = res2["codec"], res2["bitrate"], res2["n_ch"], res2["data"], res2["time"]
            p2, r2, dr2 = res2["peak_db"], res2["rms_db"], res2["dr_db"]
            lufs2 = res2["lufs"]

            report_text += tt("report_file2", name=name2, codec=codec2, br=br2, peak=p2, rms=r2, dr=dr2)
            if lufs2:
                note2 = tt("lufs_excerpt_note", mins=LUFS_MAX_DURATION_SECONDS // 60) if lufs2["truncated"] else ""
                report_text += tt("report_lufs_line", i=lufs2["i"], tp=lufs2["tp"], note=note2)
            report_text += "-" * 85 + "\n"
            report_text += tt("ai_header")

            dr_diff = abs(dr1 - dr2)
            rms_diff = abs(r1 - r2)

            if dr_diff <= 0.4 and rms_diff <= 1.5:
                report_text += tt("ai_almost_identical")
                if r1 > r2 + 0.3:
                    report_text += tt("ai_file1_slightly_louder", peak=p1)
                elif r2 > r1 + 0.3:
                    report_text += tt("ai_file2_slightly_louder", peak=p2)
            else:
                if dr1 > dr2 + 0.5:
                    report_text += tt("ai_file1_wider_dr")
                elif dr2 > dr1 + 0.5:
                    report_text += tt("ai_file2_wider_dr")

                if r1 > r2 + 1.5:
                    report_text += tt("ai_file1_louder")
                elif r2 > r1 + 1.5:
                    report_text += tt("ai_file2_louder")

            if lufs1 and lufs2:
                if not report_text.endswith("\n"):
                    report_text += "\n"
                lufs_diff = abs(lufs1["i"] - lufs2["i"])
                if lufs_diff <= 0.5:
                    report_text += tt("ai_lufs_similar")
                elif lufs1["i"] > lufs2["i"]:
                    report_text += tt("ai_lufs_file1_louder", diff=lufs_diff)
                else:
                    report_text += tt("ai_lufs_file2_louder", diff=lufs_diff)

        plt.style.use('default')
        fig = None
        try:
            if mode_key == "separate":
                fig_height = max(5, 1.5 * target_ch)
                fig, axes = plt.subplots(target_ch, 1, figsize=(14, fig_height), sharex=True, dpi=120)
                fig.patch.set_facecolor('#ffffff')
                if target_ch == 1:
                    axes = [axes]

                names = CHANNEL_NAME_MAP.get(lang, CHANNEL_NAME_MAP["tr"]).get(
                    target_ch, [tt("chart_channel_generic", i=i + 1) for i in range(target_ch)]
                )

                for i, ax in enumerate(axes):
                    ax.set_facecolor('#f4f5f9')
                    ch_data = data1[:, i] if target_ch > 1 else data1
                    t_plot, d_plot = self.downsample_for_plot(time1, ch_data)
                    ax.plot(t_plot, d_plot, color='#4169e1', linewidth=0.6)
                    ax.grid(True, which='major', color='#d3d3d3', linestyle='-', linewidth=1)
                    ax.minorticks_on()
                    ax.set_ylabel(names[i], fontsize=9, weight='bold', rotation=0, labelpad=40, ha='center', va='center')
                    if i == 0:
                        ax.set_title(tt("chart_channel_title", name=os.path.basename(file1)), fontweight='bold', pad=15)
                    if i == len(axes) - 1:
                        ax.xaxis.set_major_formatter(FuncFormatter(self.format_time))
                        ax.set_xlabel(tt("chart_time_axis"), fontsize=10, weight='bold')

            elif mode_key == "spectrogram":
                def _spec_for(path, out_wav):
                    self.extract_wav_mono_for_spectrogram(path, out_wav)
                    return self.compute_spectrogram_from_wav(out_wav)

                if two_files:
                    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
                        f1 = pool.submit(_spec_for, file1, self.temp_wav_spec1)
                        f2 = pool.submit(_spec_for, file2, self.temp_wav_spec2)
                        freqs1, times1, spec1, sr1 = f1.result()
                        freqs2, times2, spec2, sr2 = f2.result()
                    fig, axes = plt.subplots(2, 1, figsize=(14, 8), dpi=120)
                    ax1, ax2 = axes
                else:
                    freqs1, times1, spec1, sr1 = _spec_for(file1, self.temp_wav_spec1)
                    fig, ax1 = plt.subplots(figsize=(14, 6), dpi=120)
                    ax2 = None

                fig.patch.set_facecolor('#ffffff')

                def plot_spectrogram(ax, freqs, times, spec, sr, title):
                    ax.set_facecolor('#000000')
                    mesh = ax.pcolormesh(times, freqs, spec, shading='auto', cmap='inferno')
                    ax.set_ylim(0, sr / 2)
                    ax.xaxis.set_major_formatter(FuncFormatter(self.format_time))
                    ax.set_ylabel(tt("chart_spectrogram_freq_axis"), fontsize=9, weight='bold')
                    ax.set_title(f"{title}\n{tt('chart_spectrogram_mono_note', sr=sr)}", fontweight='bold', fontsize=11)
                    fig.colorbar(mesh, ax=ax, label="dB")

                plot_spectrogram(ax1, freqs1, times1, spec1, sr1, tt("chart_spectrogram_title", name=name1))
                if two_files:
                    plot_spectrogram(ax2, freqs2, times2, spec2, sr2, tt("chart_spectrogram_title", name=name2))
                    ax2.set_xlabel(tt("chart_time_axis_short"), weight='bold')

                ax1.set_xlabel(tt("chart_time_axis_short"), weight='bold')

            else:
                is_overlay = mode_key == "overlay"
                if two_files and not is_overlay:
                    fig, axes = plt.subplots(2, 1, figsize=(14, 7), dpi=120)
                    ax1, ax2 = axes
                else:
                    fig, ax1 = plt.subplots(figsize=(14, 6), dpi=120)
                    ax2 = ax1

                fig.patch.set_facecolor('#ffffff')

                def plot_data(ax, time_arr, data_arr, channels, title, color_map, alpha_val):
                    ax.set_facecolor('#f4f5f9')
                    t_plot, d_plot = self.downsample_for_plot(time_arr, data_arr)
                    if channels == 1:
                        ax.plot(t_plot, d_plot, color=color_map(0), linewidth=0.6, alpha=alpha_val, label=f'{title}')
                    else:
                        for i in range(channels):
                            ax.plot(t_plot, d_plot[:, i], color=color_map(i % 10), linewidth=0.6, alpha=alpha_val, label=f'{title} - K{i + 1}')

                    ax.grid(True, which='major', color='#d3d3d3', linestyle='-', linewidth=1)
                    ax.xaxis.set_major_formatter(FuncFormatter(self.format_time))
                    ax.set_ylabel(tt("chart_amplitude"), fontsize=9, weight='bold')
                    ax.legend(loc='upper right', fontsize=8)

                cmap1 = plt.cm.tab10
                cmap2 = plt.cm.Set1
                ch_display = T.get(f"channel_opt_{target_ch}", str(target_ch))

                plot_data(ax1, time1, data1, ch1, tt("file1_label"), cmap1, alpha_val=0.8)

                if two_files:
                    plot_data(ax2, time2, data2, ch2, tt("file2_label"), cmap2 if is_overlay else cmap1, alpha_val=0.6 if is_overlay else 0.8)
                    if not is_overlay:
                        ax2.set_xlabel(tt("chart_time_axis_short"), weight='bold')

                if two_files and not is_overlay:
                    ax1.set_title(f"{tt('chart_general_title', ch=ch_display)}\n{tt('file1_label')}: {name1}", fontweight='bold', fontsize=11)
                    ax2.set_title(f"{tt('file2_label')}: {name2}", fontweight='bold', fontsize=11)
                else:
                    title_lines = [tt("chart_general_title", ch=ch_display), f"{tt('file1_label')}: {name1}"]
                    if two_files:
                        title_lines.append(f"{tt('file2_label')}: {name2}")
                    ax1.set_title("\n".join(title_lines), fontweight='bold', fontsize=11)

                ax1.set_xlabel(tt("chart_time_axis_short"), weight='bold')

            plt.tight_layout()
            plt.savefig(self.temp_img_path)
        finally:
            if fig is not None:
                plt.close(fig)

        return report_text

    def _on_analysis_done(self, report_text):
        self.progress_bar.stop()
        self.progress_bar.pack_forget()
        self.write_report(report_text)
        self.display_image(self.temp_img_path)
        self.has_result = True
        self.btn_analyze.configure(state="normal", text=self.t("btn_analyze"))
        self.btn_save.configure(state="normal")
        self.lang_menu.configure(state="normal")
        self.is_analyzing = False

    def _on_analysis_error(self, err_msg):
        self.progress_bar.stop()
        self.progress_bar.pack_forget()
        self.lbl_img.configure(text=self.t("error_img_prefix", err=err_msg), text_color="red")
        self.write_report(self.t("error_report_prefix", err=err_msg))
        self.btn_analyze.configure(state="normal", text=self.t("btn_analyze"))
        self.lang_menu.configure(state="normal")
        self.is_analyzing = False

    def display_image(self, img_path):
        if os.path.exists(img_path):
            with Image.open(img_path) as img:
                img_data = img.copy()
            width, height = img_data.size
            ratio = 1000 / width
            new_h = int(height * ratio)
            ctk_img = ctk.CTkImage(light_image=img_data, dark_image=img_data, size=(1000, min(new_h, 500)))
            self.lbl_img.configure(image=ctk_img, text="")
            self.lbl_img.image = ctk_img

    def save_image(self):
        if not (self.has_result and os.path.exists(self.temp_img_path)):
            messagebox.showinfo(self.t("warn_title"), self.t("no_report_yet"))
            return
        save_path = filedialog.asksaveasfilename(title=self.t("save_dialog_title"), defaultextension=".png", filetypes=[("PNG", "*.png")])
        if save_path:
            try:
                shutil.copy(self.temp_img_path, save_path)
                messagebox.showinfo(self.t("save_success_title"), self.t("save_success_msg"))
            except Exception as e:
                messagebox.showerror(self.t("save_error_title"), self.t("save_error_msg", err=str(e)))

    def show_about_window(self):
        win = ctk.CTkToplevel(self)
        win.title(self.t("about_title"))
        win.geometry("420x630")
        win.resizable(False, False)
        win.transient(self)
        win.grab_set()
        self._apply_window_icon(win)

        if os.path.exists(LOGO_PATH):
            with Image.open(LOGO_PATH) as im:
                logo_ctk_img = ctk.CTkImage(light_image=im.copy(), dark_image=im.copy(), size=(140, 140))
            logo_label = ctk.CTkLabel(win, image=logo_ctk_img, text="")
            logo_label.image = logo_ctk_img
            logo_label.pack(pady=(20, 10))
        else:
            ctk.CTkLabel(win, text=f"🎵 {self.t('app_short_name')}", font=("Roboto", 20, "bold")).pack(pady=(20, 2))

        ctk.CTkLabel(win, text=self.t("about_version", v=APP_VERSION), text_color="gray").pack(pady=(0, 15))

        ctk.CTkFrame(win, height=1, fg_color="#3a3a3a").pack(fill="x", padx=20, pady=(0, 15))

        ctk.CTkLabel(win, text=self.t("about_developer", dev=DEVELOPER_NAME)).pack(pady=(0, 15))

        def make_link_row(text, url):
            btn = ctk.CTkButton(
                win, text=text, anchor="w", fg_color="#2b2b2b", hover_color="#3a3a3a",
                text_color="#5b9bd5", height=40,
                command=lambda: self._open_link(url),
            )
            btn.pack(fill="x", padx=20, pady=4)
            return btn

        make_link_row(self.t("about_website"), WEBSITE_URL)
        make_link_row(self.t("about_github"), GITHUB_URL)
        make_link_row(self.t("about_email"), f"mailto:{SUPPORT_EMAIL}")

        ctk.CTkButton(
            win, text=self.t("about_license"), anchor="w", fg_color="#2b2b2b", hover_color="#3a3a3a",
            text_color="#5b9bd5", height=40,
            command=self.show_license_window,
        ).pack(fill="x", padx=20, pady=4)

        checking_now = getattr(self, "_checking_updates", False)
        self.btn_check_updates = ctk.CTkButton(
            win,
            text=self.t("about_checking_updates") if checking_now else self.t("about_check_updates"),
            anchor="w", fg_color="#2b2b2b", hover_color="#3a3a3a",
            text_color="#5b9bd5", height=40,
            state="disabled" if checking_now else "normal",
            command=self.check_for_updates,
        )
        self.btn_check_updates.pack(fill="x", padx=20, pady=4)

        ctk.CTkButton(
            win, text=self.t("about_support"), fg_color="#e0405a", hover_color="#c03348", height=40,
            command=lambda: self._open_link(SUPPORT_URL),
        ).pack(fill="x", padx=20, pady=(15, 5))

        ctk.CTkButton(win, text=self.t("about_close"), fg_color="#5a6268", hover_color="#454d55", command=win.destroy).pack(pady=(10, 20))

    def _open_link(self, url):
        try:
            webbrowser.open(url)
        except Exception as e:
            messagebox.showerror(self.t("save_error_title"), self.t("link_open_error", err=str(e)))

    def show_license_window(self):
        win = ctk.CTkToplevel(self)
        win.title(self.t("license_window_title"))
        win.geometry("560x480")
        win.resizable(False, False)
        win.transient(self)
        win.grab_set()
        self._apply_window_icon(win)

        ctk.CTkLabel(win, text=self.t("license_window_title"), font=("Roboto", 16, "bold")).pack(pady=(15, 10))

        box = ctk.CTkTextbox(win, wrap="word", font=("Consolas", 12))
        box.pack(fill="both", expand=True, padx=15, pady=(0, 10))
        box.insert("0.0", MIT_LICENSE_TEXT)
        box.configure(state="disabled")

        ctk.CTkButton(win, text=self.t("about_close"), fg_color="#5a6268", hover_color="#454d55", command=win.destroy).pack(pady=(0, 15))

    @staticmethod
    def _version_tuple(v):
        parts = []
        for p in str(v).strip().split('.'):
            digits = ''.join(ch for ch in p if ch.isdigit())
            parts.append(int(digits) if digits else 0)
        return tuple(parts) if parts else (0,)

    def _is_newer_version(self, remote, local):
        return self._version_tuple(remote) > self._version_tuple(local)

    def check_for_updates(self):
        if getattr(self, "_checking_updates", False):
            return
        self._checking_updates = True
        self._set_check_updates_button(state="disabled", text=self.t("about_checking_updates"))
        threading.Thread(target=self._check_updates_worker, daemon=True).start()

    def _set_check_updates_button(self, **kwargs):
        btn = getattr(self, "btn_check_updates", None)
        if btn is None:
            return
        try:
            if btn.winfo_exists():
                btn.configure(**kwargs)
        except Exception:
            pass

    def _check_updates_worker(self):
        try:
            req = urllib.request.Request(
                UPDATE_CHECK_URL,
                headers={"User-Agent": f"{APP_NAME}/{APP_VERSION}"},
            )
            with urllib.request.urlopen(req, timeout=UPDATE_CHECK_TIMEOUT) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            remote_version = str(data.get("version", "")).strip()
            download_url = data.get("url") or WEBSITE_URL
            self._safe_after(lambda: self._on_update_check_done(remote_version, download_url))
        except Exception as e:
            err = str(e)
            self._safe_after(lambda: self._on_update_check_error(err))

    def _on_update_check_done(self, remote_version, download_url):
        self._checking_updates = False
        self._set_check_updates_button(state="normal", text=self.t("about_check_updates"))
        if remote_version and self._is_newer_version(remote_version, APP_VERSION):
            if messagebox.askyesno(self.t("update_available_title"), self.t("update_available_msg", version=remote_version)):
                self._open_link(download_url)
        else:
            messagebox.showinfo(self.t("update_uptodate_title"), self.t("update_uptodate_msg", version=APP_VERSION))

    def _on_update_check_error(self, err_msg):
        self._checking_updates = False
        self._set_check_updates_button(state="normal", text=self.t("about_check_updates"))
        messagebox.showerror(self.t("update_check_failed_title"), self.t("update_check_failed_msg", err=err_msg))


if __name__ == "__main__":
    if sys.platform == "win32":
        try:
            import ctypes
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
                "MrTOgRaS.MOAudioWaveformAnalyzer.1_0"
            )
        except Exception:
            pass

    app = AudioAnalyzerApp()
    app.mainloop()
