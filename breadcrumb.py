def get_breadcrumb(items):
    """
    items: list of (label, url) tuples.
    Last item is the current page (no link, just text).
    """
    parts = ""
    for i, (label, href) in enumerate(items):
        is_last = (i == len(items) - 1)
        if is_last:
            parts += f'<li class="bc-item bc-current" aria-current="page">{label}</li>'
        else:
            parts += (f'<li class="bc-item">'
                      f'<a class="bc-link" href="{href}">{label}</a>'
                      f'<span class="bc-sep" aria-hidden="true">&#8250;</span>'
                      f'</li>')
    return f'<nav class="breadcrumb" aria-label="Breadcrumb"><ol class="bc-list">{parts}</ol></nav>'
