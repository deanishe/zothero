# encoding: utf-8
#
# Copyright (c) 2017 Dean Jackson <deanishe@deanishe.net>
#
# MIT Licence. See http://opensource.org/licenses/MIT
#
# Created on 2017-12-22
#

"""CSL locales."""

from __future__ import print_function, absolute_import


import os

LOCALE_DIR = os.path.dirname(__file__)


class Locale(object):
    """A locale understood by CSL."""

    def __init__(self, code):
        """Create a new `Locale` for abbreviation ``code``.

        Args:
            code (str): Abbreviation of locale, e.g. 'en' or 'en-GB'.

        Raises:
            KeyError: Raised if ``code`` is an unknown locale.
        """
        self._code = LOCALE_MAP[code.lower()]
        self._name = None
        self._path = None

    @property
    def code(self):
        """Canonical locale code.

        Returns:
            unicode: Code for locale.
        """
        return self._code

    @property
    def name(self):
        """Name of locale in local language and English.

        Returns:
            unicode: Locale name.
        """
        if not self._name:
            self._name = LOCALE_NAME[self.code]

        return self._name

    @property
    def path(self):
        """Path to CSL locale definition file.

        Returns:
            str: Path to XML locale file.
        """
        return os.path.join(LOCALE_DIR, 'locales-%s.xml' % self.code)


def all():
    """Return all locales.

    Returns:
        list: Sequence of `Locale` objects for all supported locales.
    """
    return sorted([Locale(code) for code in LOCALE_NAME], key=lambda l: l.name)


def lookup(code):
    """Return canonical Locale for string ``code``.

    Args:
        code (str): Locale code.

    Returns:
        Locale: Locale for code or ``None`` if it's unknown.
    """
    try:
        return Locale(code)
    except KeyError:
        return None


# Map language/locale to CSL locales, including default dialects.
LOCALE_MAP = {
    u'af': u'af-ZA',
    u'af-za': u'af-ZA',
    u'ar': u'ar',
    u'bg': u'bg-BG',
    u'bg-bg': u'bg-BG',
    u'ca': u'ca-AD',
    u'ca-ad': u'ca-AD',
    u'cs': u'cs-CZ',
    u'cs-cz': u'cs-CZ',
    u'cy': u'cy-GB',
    u'cy-gb': u'cy-GB',
    u'da': u'da-DK',
    u'da-dk': u'da-DK',
    u'de': u'de-DE',
    u'de-at': u'de-AT',
    u'de-ch': u'de-CH',
    u'de-de': u'de-DE',
    u'el': u'el-GR',
    u'el-gr': u'el-GR',
    u'en': u'en-US',
    u'en-gb': u'en-GB',
    u'en-us': u'en-US',
    u'es': u'es-ES',
    u'es-cl': u'es-CL',
    u'es-es': u'es-ES',
    u'es-mx': u'es-MX',
    u'et': u'et-EE',
    u'et-ee': u'et-EE',
    u'eu': u'eu',
    u'fa': u'fa-IR',
    u'fa-ir': u'fa-IR',
    u'fi': u'fi-FI',
    u'fi-fi': u'fi-FI',
    u'fr': u'fr-FR',
    u'fr-ca': u'fr-CA',
    u'fr-fr': u'fr-FR',
    u'he': u'he-IL',
    u'he-il': u'he-IL',
    u'hr': u'hr-HR',
    u'hr-hr': u'hr-HR',
    u'hu': u'hu-HU',
    u'hu-hu': u'hu-HU',
    u'id': u'id-ID',
    u'id-id': u'id-ID',
    u'is': u'is-IS',
    u'is-is': u'is-IS',
    u'it': u'it-IT',
    u'it-it': u'it-IT',
    u'ja': u'ja-JP',
    u'ja-jp': u'ja-JP',
    u'km': u'km-KH',
    u'km-kh': u'km-KH',
    u'ko': u'ko-KR',
    u'ko-kr': u'ko-KR',
    u'lt': u'lt-LT',
    u'lt-lt': u'lt-LT',
    u'lv': u'lv-LV',
    u'lv-lv': u'lv-LV',
    u'mn': u'mn-MN',
    u'mn-mn': u'mn-MN',
    u'nb': u'nb-NO',
    u'nb-no': u'nb-NO',
    u'nl': u'nl-NL',
    u'nl-nl': u'nl-NL',
    u'nn': u'nn-NO',
    u'nn-no': u'nn-NO',
    u'pl': u'pl-PL',
    u'pl-pl': u'pl-PL',
    u'pt': u'pt-PT',
    u'pt-br': u'pt-BR',
    u'pt-pt': u'pt-PT',
    u'ro': u'ro-RO',
    u'ro-ro': u'ro-RO',
    u'ru': u'ru-RU',
    u'ru-ru': u'ru-RU',
    u'sk': u'sk-SK',
    u'sk-sk': u'sk-SK',
    u'sl': u'sl-SI',
    u'sl-si': u'sl-SI',
    u'sr': u'sr-RS',
    u'sr-rs': u'sr-RS',
    u'sv': u'sv-SE',
    u'sv-se': u'sv-SE',
    u'th': u'th-TH',
    u'th-th': u'th-TH',
    u'tr': u'tr-TR',
    u'tr-tr': u'tr-TR',
    u'uk': u'uk-UA',
    u'uk-ua': u'uk-UA',
    u'vi': u'vi-VN',
    u'vi-vn': u'vi-VN',
    u'zh': u'zh-CN',
    u'zh-cn': u'zh-CN',
    u'zh-tw': u'zh-TW',
}

# Locale name -> code
NAME_LOCALE = {
    u'Afrikaans': u'af-ZA',
    u'Bahasa Indonesia / Indonesian': u'id-ID',
    u'Catal\xe0 / Catalan': u'ca-AD',
    u'Cymraeg / Welsh': u'cy-GB',
    u'Dansk / Danish': u'da-DK',
    u'Deutsch (Deutschland) / German (Germany)': u'de-DE',
    u'Deutsch (Schweiz) / German (Switzerland)': u'de-CH',
    u'Deutsch (\xd6sterreich) / German (Austria)': u'de-AT',
    u'Eesti / Estonian': u'et-EE',
    u'English (UK)': u'en-GB',
    u'English (US)': u'en-US',
    u'Espa\xf1ol (Chile) / Spanish (Chile)': u'es-CL',
    u'Espa\xf1ol (Espa\xf1a) / Spanish (Spain)': u'es-ES',
    u'Espa\xf1ol (M\xe9xico) / Spanish (Mexico)': u'es-MX',
    u'Euskara / Basque': u'eu',
    u'Fran\xe7ais (Canada) / French (Canada)': u'fr-CA',
    u'Fran\xe7ais (France) / French (France)': u'fr-FR',
    u'Hrvatski / Croatian': u'hr-HR',
    u'Italiano / Italian': u'it-IT',
    u'Latvie\u0161u / Latvian': u'lv-LV',
    u'Lietuvi\u0173 / Lithuanian': u'lt-LT',
    u'Magyar / Hungarian': u'hu-HU',
    u'Nederlands / Dutch': u'nl-NL',
    u'Norsk bokm\xe5l / Norwegian (Bokm\xe5l)': u'nb-NO',
    u'Norsk nynorsk / Norwegian (Nynorsk)': u'nn-NO',
    u'Polski / Polish': u'pl-PL',
    u'Portugu\xeas (Brasil) / Portuguese (Brazil)': u'pt-BR',
    u'Portugu\xeas (Portugal) / Portuguese (Portugal)': u'pt-PT',
    u'Rom\xe2n\u0103 / Romanian': u'ro-RO',
    u'Sloven\u010dina / Slovak': u'sk-SK',
    u'Sloven\u0161\u010dina / Slovenian': u'sl-SI',
    u'Suomi / Finnish': u'fi-FI',
    u'Svenska / Swedish': u'sv-SE',
    u'Ti\u1ebfng Vi\u1ec7t / Vietnamese': u'vi-VN',
    u'T\xfcrk\xe7e / Turkish': u'tr-TR',
    u'\xcdslenska / Icelandic': u'is-IS',
    u'\u010ce\u0161tina / Czech': u'cs-CZ',
    u'\u0395\u03bb\u03bb\u03b7\u03bd\u03b9\u03ba\u03ac / Greek': u'el-GR',
    u'\u0411\u044a\u043b\u0433\u0430\u0440\u0441\u043a\u0438 / Bulgarian': u'bg-BG',
    u'\u041c\u043e\u043d\u0433\u043e\u043b / Mongolian': u'mn-MN',
    u'\u0420\u0443\u0441\u0441\u043a\u0438\u0439 / Russian': u'ru-RU',
    u'\u0421\u0440\u043f\u0441\u043a\u0438 / Srpski / Serbian': u'sr-RS',
    u'\u0423\u043a\u0440\u0430\u0457\u043d\u0441\u044c\u043a\u0430 / Ukrainian': u'uk-UA',
    u'\u05e2\u05d1\u05e8\u05d9\u05ea / Hebrew': u'he-IL',
    u'\u0627\u0644\u0639\u0631\u0628\u064a\u0629 / Arabic': u'ar',
    u'\u0641\u0627\u0631\u0633\u06cc / Persian': u'fa-IR',
    u'\u0e44\u0e17\u0e22 / Thai': u'th-TH',
    u'\u1797\u17b6\u179f\u17b6\u1781\u17d2\u1798\u17c2\u179a / Khmer': u'km-KH',
    u'\u4e2d\u6587 (\u4e2d\u56fd\u5927\u9646) / Chinese (PRC)': u'zh-CN',
    u'\u4e2d\u6587 (\u53f0\u7063) / Chinese (Taiwan)': u'zh-TW',
    u'\u65e5\u672c\u8a9e / Japanese': u'ja-JP',
    u'\ud55c\uad6d\uc5b4 / Korean': u'ko-KR',
}

# Locale code -> name
LOCALE_NAME = {
    u'af-ZA': u'Afrikaans',
    u'ar': u'\u0627\u0644\u0639\u0631\u0628\u064a\u0629 / Arabic',
    u'bg-BG': u'\u0411\u044a\u043b\u0433\u0430\u0440\u0441\u043a\u0438 / Bulgarian',
    u'ca-AD': u'Catal\xe0 / Catalan',
    u'cs-CZ': u'\u010ce\u0161tina / Czech',
    u'cy-GB': u'Cymraeg / Welsh',
    u'da-DK': u'Dansk / Danish',
    u'de-AT': u'Deutsch (\xd6sterreich) / German (Austria)',
    u'de-CH': u'Deutsch (Schweiz) / German (Switzerland)',
    u'de-DE': u'Deutsch (Deutschland) / German (Germany)',
    u'el-GR': u'\u0395\u03bb\u03bb\u03b7\u03bd\u03b9\u03ba\u03ac / Greek',
    u'en-GB': u'English (UK)',
    u'en-US': u'English (US)',
    u'es-CL': u'Espa\xf1ol (Chile) / Spanish (Chile)',
    u'es-ES': u'Espa\xf1ol (Espa\xf1a) / Spanish (Spain)',
    u'es-MX': u'Espa\xf1ol (M\xe9xico) / Spanish (Mexico)',
    u'et-EE': u'Eesti / Estonian',
    u'eu': u'Euskara / Basque',
    u'fa-IR': u'\u0641\u0627\u0631\u0633\u06cc / Persian',
    u'fi-FI': u'Suomi / Finnish',
    u'fr-CA': u'Fran\xe7ais (Canada) / French (Canada)',
    u'fr-FR': u'Fran\xe7ais (France) / French (France)',
    u'he-IL': u'\u05e2\u05d1\u05e8\u05d9\u05ea / Hebrew',
    u'hr-HR': u'Hrvatski / Croatian',
    u'hu-HU': u'Magyar / Hungarian',
    u'id-ID': u'Bahasa Indonesia / Indonesian',
    u'is-IS': u'\xcdslenska / Icelandic',
    u'it-IT': u'Italiano / Italian',
    u'ja-JP': u'\u65e5\u672c\u8a9e / Japanese',
    u'km-KH': u'\u1797\u17b6\u179f\u17b6\u1781\u17d2\u1798\u17c2\u179a / Khmer',
    u'ko-KR': u'\ud55c\uad6d\uc5b4 / Korean',
    u'lt-LT': u'Lietuvi\u0173 / Lithuanian',
    u'lv-LV': u'Latvie\u0161u / Latvian',
    u'mn-MN': u'\u041c\u043e\u043d\u0433\u043e\u043b / Mongolian',
    u'nb-NO': u'Norsk bokm\xe5l / Norwegian (Bokm\xe5l)',
    u'nl-NL': u'Nederlands / Dutch',
    u'nn-NO': u'Norsk nynorsk / Norwegian (Nynorsk)',
    u'pl-PL': u'Polski / Polish',
    u'pt-BR': u'Portugu\xeas (Brasil) / Portuguese (Brazil)',
    u'pt-PT': u'Portugu\xeas (Portugal) / Portuguese (Portugal)',
    u'ro-RO': u'Rom\xe2n\u0103 / Romanian',
    u'ru-RU': u'\u0420\u0443\u0441\u0441\u043a\u0438\u0439 / Russian',
    u'sk-SK': u'Sloven\u010dina / Slovak',
    u'sl-SI': u'Sloven\u0161\u010dina / Slovenian',
    u'sr-RS': u'\u0421\u0440\u043f\u0441\u043a\u0438 / Srpski / Serbian',
    u'sv-SE': u'Svenska / Swedish',
    u'th-TH': u'\u0e44\u0e17\u0e22 / Thai',
    u'tr-TR': u'T\xfcrk\xe7e / Turkish',
    u'uk-UA': u'\u0423\u043a\u0440\u0430\u0457\u043d\u0441\u044c\u043a\u0430 / Ukrainian',
    u'vi-VN': u'Ti\u1ebfng Vi\u1ec7t / Vietnamese',
    u'zh-CN': u'\u4e2d\u6587 (\u4e2d\u56fd\u5927\u9646) / Chinese (PRC)',
    u'zh-TW': u'\u4e2d\u6587 (\u53f0\u7063) / Chinese (Taiwan)',
}
