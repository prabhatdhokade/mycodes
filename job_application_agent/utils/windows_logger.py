"""
Windows-Compatible Logger
Handles Unicode and emoji characters properly on Windows systems
"""

import logging
import sys
import os
from datetime import datetime
from typing import Optional

# Fix Windows console encoding
if sys.platform == "win32":
    # Try to set UTF-8 encoding for Windows console
    try:
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.detach())
    except:
        pass
    
    # Alternative: Set console code page to UTF-8
    try:
        os.system('chcp 65001 > nul')
    except:
        pass

class WindowsCompatibleFormatter(logging.Formatter):
    """Formatter that handles Unicode characters gracefully on Windows"""
    
    # Emoji fallbacks for Windows
    EMOJI_FALLBACKS = {
        '🎯': '[TARGET]',
        '✅': '[SUCCESS]',
        '❌': '[ERROR]',
        '⚠️': '[WARNING]',
        '🔍': '[SEARCH]',
        '📊': '[STATUS]',
        '🤖': '[AI]',
        '🌐': '[WEB]',
        '📝': '[FORM]',
        '💼': '[JOB]',
        '🚀': '[START]',
        '⏸️': '[PAUSE]',
        '🛑': '[STOP]',
        '🔧': '[CONFIG]',
        '📈': '[STATS]',
        '🎉': '[CELEBRATE]',
        '⏰': '[TIME]',
        '📅': '[DATE]',
        '👤': '[USER]',
        '📧': '[EMAIL]',
        '💰': '[SALARY]',
        '📍': '[LOCATION]',
        '🛠️': '[SKILLS]',
        '🛡️': '[SAFETY]'
    }
    
    def __init__(self, fmt=None, datefmt=None, use_emoji=True):
        super().__init__(fmt, datefmt)
        self.use_emoji = use_emoji and self._supports_unicode()
    
    def _supports_unicode(self) -> bool:
        """Check if the console supports Unicode characters"""
        try:
            # Test if we can encode emoji
            test_emoji = '🎯'
            test_emoji.encode(sys.stdout.encoding or 'utf-8')
            return True
        except (UnicodeEncodeError, AttributeError):
            return False
    
    def format(self, record):
        # Format the record normally first
        formatted = super().format(record)
        
        # Replace emojis with fallbacks if needed
        if not self.use_emoji:
            for emoji, fallback in self.EMOJI_FALLBACKS.items():
                formatted = formatted.replace(emoji, fallback)
        
        return formatted

def setup_windows_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """Setup a Windows-compatible logger"""
    
    logger = logging.getLogger(name)
    
    # Avoid adding multiple handlers
    if logger.handlers:
        return logger
    
    logger.setLevel(level)
    
    # Create logs directory if it doesn't exist
    log_dir = os.path.join(os.path.dirname(__file__), '..', 'logs')
    os.makedirs(log_dir, exist_ok=True)
    
    # Console handler with Windows compatibility
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    
    # Use Windows-compatible formatter
    console_formatter = WindowsCompatibleFormatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(console_formatter)
    
    # File handler (always use UTF-8 for files)
    log_file = os.path.join(log_dir, f'{name.lower().replace(".", "_")}.log')
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    
    # File formatter can use emojis since we're using UTF-8
    file_formatter = WindowsCompatibleFormatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        use_emoji=True  # Always use emojis in files
    )
    file_handler.setFormatter(file_formatter)
    
    # Add handlers to logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    return logger

def get_windows_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """Get a Windows-compatible logger instance"""
    return setup_windows_logger(name, level)

# Convenience functions for logging common events
def log_application_sent_win(job_title: str, company: str, platform: str):
    """Log successful application with Windows compatibility"""
    logger = get_windows_logger('Applications')
    if supports_unicode():
        logger.info(f"✅ Applied to {job_title} at {company} on {platform}")
    else:
        logger.info(f"[SUCCESS] Applied to {job_title} at {company} on {platform}")

def log_application_failed_win(job_title: str, company: str, platform: str, reason: str):
    """Log failed application with Windows compatibility"""
    logger = get_windows_logger('Applications')
    if supports_unicode():
        logger.error(f"❌ Failed to apply to {job_title} at {company} on {platform}: {reason}")
    else:
        logger.error(f"[ERROR] Failed to apply to {job_title} at {company} on {platform}: {reason}")

def log_scraping_session_win(platform: str, jobs_found: int, applications_sent: int, duration: float):
    """Log scraping session with Windows compatibility"""
    logger = get_windows_logger('Sessions')
    if supports_unicode():
        logger.info(f"🔍 {platform} session: {jobs_found} jobs found, {applications_sent} applications sent in {duration:.1f}s")
    else:
        logger.info(f"[SEARCH] {platform} session: {jobs_found} jobs found, {applications_sent} applications sent in {duration:.1f}s")

def supports_unicode() -> bool:
    """Check if the current console supports Unicode"""
    try:
        test_emoji = '🎯'
        test_emoji.encode(sys.stdout.encoding or 'utf-8')
        return True
    except (UnicodeEncodeError, AttributeError):
        return False

def safe_print(message: str, fallback_message: str = None):
    """Print message with Unicode fallback for Windows"""
    try:
        print(message)
    except UnicodeEncodeError:
        if fallback_message:
            print(fallback_message)
        else:
            # Remove emojis and special characters
            safe_message = message
            for emoji, fallback in WindowsCompatibleFormatter.EMOJI_FALLBACKS.items():
                safe_message = safe_message.replace(emoji, fallback)
            print(safe_message)