from django.contrib.auth import get_user_model


User = get_user_model()


ROLE_CODES_BY_ACCESS_LEVEL = {
    'ACADEMIE': ['ADMIN', 'RESP_FIN', 'RESP_INFO', 'RESP_AUTO'],
    'DP': ['DP_RESP_FIN', 'DP_RESP_INFO', 'DP_RESP_AUTO'],
    'ETABLISSEMENT': ['ETAB_RESP_CONSO'],
}


def get_selected_access_level(request):
    return request.session.get('selected_access_level') or (request.user.niveau_acces if request.user.is_authenticated else None)


def get_selected_role(request):
    return request.session.get('selected_role') or (request.user.role if request.user.is_authenticated else None)


def get_allowed_role_codes_for_access_level(access_level):
    return ROLE_CODES_BY_ACCESS_LEVEL.get(access_level, [])


def get_scope_filter_kwargs(request, relation_prefix='etablissement'):
    access_level = get_selected_access_level(request)

    if not request.user.is_authenticated:
        return {}

    if access_level == 'ETABLISSEMENT' and request.user.etablissement_id:
        return {f'{relation_prefix}__id': request.user.etablissement_id}

    if access_level == 'DP' and request.user.direction_provinciale_id:
        return {f'{relation_prefix}__direction_provinciale_id': request.user.direction_provinciale_id}

    if access_level == 'ACADEMIE' and request.user.academie_id:
        return {f'{relation_prefix}__academie_id': request.user.academie_id}

    return {}


def scope_queryset(queryset, request, relation_prefix='etablissement'):
    scope_kwargs = get_scope_filter_kwargs(request, relation_prefix=relation_prefix)
    if scope_kwargs:
        return queryset.filter(**scope_kwargs)
    return queryset


def scope_etablissements_queryset(queryset, request):
    access_level = get_selected_access_level(request)

    if not request.user.is_authenticated:
        return queryset.none()

    if access_level == 'ETABLISSEMENT' and request.user.etablissement_id:
        return queryset.filter(id=request.user.etablissement_id)

    if access_level == 'DP' and request.user.direction_provinciale_id:
        return queryset.filter(direction_provinciale_id=request.user.direction_provinciale_id)

    if access_level == 'ACADEMIE' and request.user.academie_id:
        return queryset.filter(academie_id=request.user.academie_id)

    return queryset