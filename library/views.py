"""Страницы музыкальных коллекций пользователей."""
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from main import load_data
from models.albums import MAX_RATING, get_rating_stars
from models.collection import (
    find_collection_by_id,
    get_collection_recommendation,
)


def collections(request: HttpRequest) -> HttpResponse:
    """Список коллекций всех пользователей."""
    _, _, _, collections_list = load_data()
    context = {
        "collections": collections_list,
    }
    return render(request, "library/collection_list.html", context)


def collection_detail(
    request: HttpRequest,
    collection_id: int,
) -> HttpResponse:
    """Коллекция: статистика и альбомы; при отсутствии — код 404."""
    _, _, _, collections_list = load_data()
    collection = find_collection_by_id(collections_list, collection_id)
    context = {
        "collection": collection,
        "max_rating": MAX_RATING,
    }
    if collection is not None:
        average = collection.average_rating
        context["average"] = average
        if average is not None:
            context["average_stars"] = get_rating_stars(round(average))
        context["recommendation"] = get_collection_recommendation(collection)
    return render(
        request,
        "library/collection_detail.html",
        context,
        status=404 if collection is None else 200,
    )
