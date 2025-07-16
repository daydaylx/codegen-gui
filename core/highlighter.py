from PySide6.QtGui import QSyntaxHighlighter, QTextCharFormat, QFont, QColor
from PySide6.QtCore import QRegularExpression
from pygments import highlight
from pygments.lexers import get_lexer_by_name, get_lexer_for_filename, get_all_lexers
from pygments.styles import get_style_by_name

class PygmentsHighlighter(QSyntaxHighlighter):
    def __init__(self, document):
        super().__init__(document)
        self.formats = {}
        self.lexer = get_lexer_by_name("python") # Standard-Lexer ist Python
        self.style = get_style_by_name("default") # Standard-Stil
        self._setup_formats()

    def _setup_formats(self):
        """Richtet Textformate basierend auf dem Pygments-Stil ein."""
        for token_type, style_def in self.style:
            text_format = QTextCharFormat()
            if style_def['color']:
                text_format.setForeground(QColor(f"#{style_def['color']}"))
            if style_def['bgcolor']:
                text_format.setBackground(QColor(f"#{style_def['bgcolor']}"))
            if style_def['bold']:
                text_format.setFontWeight(QFont.Bold)
            if style_def['italic']:
                text_format.setFontItalic(True)
            if style_def['underline']:
                text_format.setFontUnderline(True)
            self.formats[token_type] = text_format

    def highlightBlock(self, text):
        """Highlightet einen einzelnen Textblock."""
        # Pygments benötigt den gesamten Text für genaue Hervorhebung.
        # Dies ist eine Vereinfachung für Block-Highlighting, idealerweise sollte
        # Pygments auf dem gesamten Dokument ausgeführt werden, wenn der Text stabil ist.
        # Für inkrementelles Highlighten bei der Eingabe ist dies komplexer.
        # Hier wird nur der aktuelle Block hervorgehoben.

        try:
            # Tokenize the current block and apply formats
            # This is a simplification; Pygments usually works on full text
            # For real-time typing, consider a more advanced approach.
            tokens = list(self.lexer.get_tokens(text))
            offset = 0
            for ttype, value in tokens:
                length = len(value)
                if ttype in self.formats:
                    self.setFormat(offset, length, self.formats[ttype])
                offset += length
        except Exception as e:
            # Fallback, wenn Lexer-Fehler auftreten
            pass

    def set_lexer_by_filename(self, filename: str):
        """Setzt den Lexer basierend auf dem Dateinamen."""
        try:
            self.lexer = get_lexer_for_filename(filename, stripall=True)
            self.rehighlight()
        except Exception:
            # Fallback auf Python, wenn kein spezifischer Lexer gefunden wird
            self.lexer = get_lexer_by_name("python")
            self.rehighlight()

    def set_lexer_by_mimetype(self, mimetype: str):
        """Setzt den Lexer basierend auf dem MIME-Typ."""
        try:
            self.lexer = get_lexer_by_name(mimetype, stripall=True)
            self.rehighlight()
        except Exception:
            self.lexer = get_lexer_by_name("python")
            self.rehighlight()

    def set_lexer_by_name(self, name: str):
        """Setzt den Lexer basierend auf einem Lexer-Namen (z.B. 'python', 'java')."""
        try:
            self.lexer = get_lexer_by_name(name, stripall=True)
            self.rehighlight()
        except Exception:
            self.lexer = get_lexer_by_name("python")
            self.rehighlight()

    # Optional: Stiländerung bei Bedarf
    def set_style(self, style_name: str):
        try:
            self.style = get_style_by_name(style_name)
            self._setup_formats()
            self.rehighlight()
        except Exception:
            self.style = get_style_by_name("default")
            self._setup_formats()
            self.rehighlight()

