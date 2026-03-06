from rest_framework.response import Response


def success(data=None, message='Success.', status_code=200):
    return Response(
        {
            'success': True,
            'code': status_code,
            'message': message,
            'data': data,
        },
        status=status_code,
    )


def paginated_success(pagination, data):
    page = pagination.page
    paginator = page.paginator
    return Response({
        'success': True,
        'code': 200,
        'message': 'Success.',
        'data': data,
        'meta': {
            'total': paginator.count,
            'page': page.number,
            'limit': paginator.per_page,
            'totalPages': paginator.num_pages,
            'hasNext': page.has_next(),
            'hasPrev': page.has_previous(),
        },
    })
