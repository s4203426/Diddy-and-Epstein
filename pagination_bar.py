def get_page_numbers(current, total):
    if total <= 7:
        return list(range(1, total + 1))
    pages = sorted({1, total, current,
                    max(1, current - 1), min(total, current + 1)})
    result = []
    prev = 0
    for p in pages:
        if p - prev > 1:
            result.append('...')
        result.append(p)
        prev = p
    return result

def get_pagination_bar(sel_page, total_pages, page_base_url):
    if total_pages <= 1:
        return ''
    page_nums = get_page_numbers(sel_page, total_pages)
    prev_url  = page_base_url + str(max(1, sel_page - 1))
    next_url  = page_base_url + str(min(total_pages, sel_page + 1))

    html  = '<div class="pagination">'
    html += f'<span class="pagination-info">Showing {sel_page} of {total_pages} pages</span>'
    html += '<div class="pagination-controls">'
    html += '<a class="page-btn ' + ('page-btn-disabled' if sel_page == 1 else '') + '" href="' + prev_url + '">&#8249;</a>'
    for p in page_nums:
        if p == '...':
            html += '<span class="page-ellipsis">...</span>'
        else:
            active = 'page-btn-active' if p == sel_page else ''
            html += '<a class="page-btn ' + active + '" href="' + page_base_url + str(p) + '">' + str(p) + '</a>'
    html += '<a class="page-btn ' + ('page-btn-disabled' if sel_page == total_pages else '') + '" href="' + next_url + '">&#8250;</a>'
    html += '</div></div>'
    return html
