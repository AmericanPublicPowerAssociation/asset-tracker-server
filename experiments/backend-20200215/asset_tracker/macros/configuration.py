def parse_list(x):
    # Adapted from invisibleroads-macros
    if isinstance(x, str):
        x = x.split()
    return x
