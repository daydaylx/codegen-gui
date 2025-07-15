# highlighter.py – Pygments-basierte Syntax-Hervorhebung

from pygments import highlight
from pygments.lexers import PythonLexer, BashLexer, HtmlLexer, get_lexer_by_name
from pygments.formatters import HtmlFormatter

def highlight_code(code: str, language: str = "python") -> str:
    """
    Wandelt Code in HTML um mit Syntaxhighlighting für QTextBrowser o.Ä.
    """
    try:
        lexer = get_lexer_by_name(language)
    except Exception:
        lexer = PythonLexer()

    formatter = HtmlFormatter(full=False, style="monokai", noclasses=True)
    return highlight(code, lexer, formatter)
