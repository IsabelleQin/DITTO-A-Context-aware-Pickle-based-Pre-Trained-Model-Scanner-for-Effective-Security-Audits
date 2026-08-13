import logging

def set_handler(logger, path, mode, formatter="%(asctime)s - %(name)s - %(levelname)s - %(message)s"):
    handler = logging.FileHandler(path, mode=mode)
    handler.setFormatter(logging.Formatter(formatter))
    # Handler swap, redirect the stream
    for h in logger.handlers[:]:
        if isinstance(h, logging.FileHandler):
            h.close()
            logger.removeHandler(h)
    logger.addHandler(handler)
    
def get_paths(all_file_names):
    try:
        with open(all_file_names, 'r', encoding='utf-8') as file:
            paths = [line.strip() for line in file.readlines()]
    except FileNotFoundError:
        raise FileNotFoundError
    return paths