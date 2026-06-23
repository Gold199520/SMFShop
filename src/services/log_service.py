import logging

class LogService:
    """Сервис структурированного логирования для SFMShop"""

    def __init__(self, log_file: str = "app.log"):
        self.logger = logging.getLogger("SFMShop")
        self.logger.setLevel(logging.DEBUG)

        # Формат логов
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )

        # Запись в файл
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)

        # Вывод в консоль
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)

        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

    def debug(self, message: str):
        self.logger.debug(message)

    def info(self, message: str):
        self.logger.info(message)

    def warning(self, message: str):
        self.logger.warning(message)

    def error(self, message: str):
        self.logger.error(message)

    def critical(self, message: str):
        self.logger.critical(message)

    def setup_sentry(self, dsn: str = None):
        """Интеграция с Sentry для мониторинга ошибок (базово)"""
        if dsn:
            try:
                import sentry_sdk
                sentry_sdk.init(
                    dsn=dsn,
                    traces_sample_rate=1.0
                )
                self.logger.info("Sentry мониторинг активирован")
            except ImportError:
                self.logger.warning("Sentry не установлен. Установите: pip install sentry-sdk")
        else:
            self.logger.info("Sentry DSN не указан, мониторинг отключен")

log_service = LogService()