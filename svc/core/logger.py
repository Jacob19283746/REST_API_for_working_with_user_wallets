import logging


def configure_logger() -> None:
    """
    Настраивает кастомный логгер для приложения.

    Создает логгер с выводом в консоль, форматирует сообщения
    и отключает избыточное логирование от внешних библиотек.
    """
    logger = logging.getLogger("fnano")
    logger.setLevel(logging.INFO)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    console_handler.setFormatter(formatter)

    if not logger.hasHandlers():
        logger.addHandler(console_handler)

    logger.propagate = False

    logging.getLogger("passlib").setLevel(logging.ERROR)
