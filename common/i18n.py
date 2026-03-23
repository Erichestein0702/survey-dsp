"""
Internationalization (i18n) Manager
Supports dynamic language switching between Chinese and English
"""

import json
import os
from pathlib import Path
from typing import Dict, Optional, Callable, List
from PyQt6.QtCore import QTranslator, QLocale, QLibraryInfo, QObject, pyqtSignal


class I18nManager(QObject):
    """
    Internationalization Manager
    Manages language switching and translation loading
    """
    
    language_changed = pyqtSignal(str)
    
    SUPPORTED_LANGUAGES = {
        'en_US': 'English',
        'zh_CN': '中文',
    }
    
    DEFAULT_LANGUAGE = 'en_US'
    
    _instance: Optional['I18nManager'] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if hasattr(self, '_initialized') and self._initialized:
            return
        super().__init__()
        self._initialized = True
        self._current_language = self.DEFAULT_LANGUAGE
        self._translations: Dict[str, Dict[str, str]] = {}
        self._translator: Optional[QTranslator] = None
        self._app = None
        self._callbacks: List[Callable] = []
        self._load_translations()
    
    def _get_locale_dir(self) -> Path:
        """Get locale directory path"""
        return Path(__file__).parent.parent / 'locale'
    
    def _load_translations(self):
        """Load all translation files"""
        locale_dir = self._get_locale_dir()
        
        for lang_code in self.SUPPORTED_LANGUAGES:
            trans_file = locale_dir / f'{lang_code}.json'
            if trans_file.exists():
                with open(trans_file, 'r', encoding='utf-8') as f:
                    self._translations[lang_code] = json.load(f)
            else:
                self._translations[lang_code] = {}
    
    def set_app(self, app):
        """Set QApplication instance"""
        self._app = app
    
    def get_current_language(self) -> str:
        """Get current language code"""
        return self._current_language
    
    def get_language_name(self, lang_code: str) -> str:
        """Get display name for language code"""
        return self.SUPPORTED_LANGUAGES.get(lang_code, lang_code)
    
    def get_supported_languages(self) -> Dict[str, str]:
        """Get all supported languages"""
        return self.SUPPORTED_LANGUAGES.copy()
    
    def set_language(self, lang_code: str) -> bool:
        """
        Set current language
        Returns True if successful
        """
        if lang_code not in self.SUPPORTED_LANGUAGES:
            return False
        
        if lang_code == self._current_language:
            return True
        
        self._current_language = lang_code
        self.language_changed.emit(lang_code)
        
        for callback in self._callbacks:
            callback()
        
        return True
    
    def tr(self, text: str, context: str = '') -> str:
        """
        Translate text to current language
        If translation not found, returns original text
        """
        translations = self._translations.get(self._current_language, {})
        
        if context:
            key = f"{context}.{text}"
            if key in translations:
                return translations[key]
        
        if text in translations:
            return translations[text]
        
        return text
    
    def register_callback(self, callback: Callable):
        """Register a callback to be called when language changes"""
        if callback not in self._callbacks:
            self._callbacks.append(callback)
    
    def unregister_callback(self, callback: Callable):
        """Unregister a callback"""
        if callback in self._callbacks:
            self._callbacks.remove(callback)
    
    def save_preference(self, lang_code: str):
        """Save language preference to config file"""
        config_file = Path(__file__).parent.parent / 'language_config.json'
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump({'language': lang_code}, f)
    
    def load_preference(self) -> str:
        """Load language preference from config file"""
        config_file = Path(__file__).parent.parent / 'language_config.json'
        if config_file.exists():
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                return config.get('language', self.DEFAULT_LANGUAGE)
        return self.DEFAULT_LANGUAGE


def tr(text: str, context: str = '') -> str:
    """
    Global translation function
    Usage: tr("Hello World") or tr("Hello", "greeting")
    """
    return I18nManager().tr(text, context)


def get_i18n_manager() -> I18nManager:
    """Get the singleton I18nManager instance"""
    return I18nManager()
