from collections import Counter
import requests
from django.http import JsonResponse
from rest_framework import status
from rest_framework.decorators import api_view
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework import generics, permissions
from movie_app.models import Collection
from movie_app.serializers import (
    CollectionSerializer,
    LoginSerializer,
    RegistrationSerializer,
)


@api_view(["GET"])
def movie_list(request):
    url = "http://demo.credy.in/api/v1/maya/movies/"
    host_url = request.build_absolute_uri("/")
    movies_url = f"{host_url}movies/"
    retry_limit = request.GET.get("retry_limit", 3)
    while retry_limit > 0:
        try:
            page = request.GET.get("page", 1)
            url = f"{url}?page={page}"
            response = requests.get(url)
            data = response.json()

            if response.status_code == status.HTTP_200_OK:
                if "next" in data:
                    if "?page=" in data["next"] and data["next"]:
                        if "?page=" in data["next"]:
                            data["next"] = f"{movies_url}?page={data['next'][-1]}"
                        else:
                            data["next"] = movies_url
                if "previous" in data and data["previous"]:
                    print(data["previous"], "previous")
                    if "?page=" in data["previous"]:
                        print(data["previous"], "previous")
                        data["previous"] = f"{movies_url}?page={data['previous'][-1]}"
                    else:
                        data["previous"] = movies_url

                if "results" in data:
                    data["data"] = data["results"]
                    del data["results"]
                return JsonResponse(data)
            else:
                retry_limit -= 1
                print("retrying")

        except requests.RequestException:
            retry_limit -= 1

    return JsonResponse({"error": "Failed to fetch data"})


class RegistrationView(generics.CreateAPIView):
    serializer_class = RegistrationSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Generate JWT token
        refresh = RefreshToken.for_user(user)
        token_data = {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }

        return Response(token_data, status=status.HTTP_201_CREATED)


class LoginView(generics.CreateAPIView):
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Get the authenticated user
        user = serializer.validated_data["user"]
        print(user, "USER")

        # Generate JWT token
        refresh = RefreshToken.for_user(user)
        token_data = {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }
        print(token_data, "token_data")

        return Response(token_data, status=status.HTTP_200_OK)



class CollectionListView(generics.ListCreateAPIView):
    serializer_class = CollectionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Collection.objects.filter(user=user)

    def perform_create(self, serializer):
        user = self.request.user
        serializer.save(user=user)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        
        # Extracting top 3 genres based on movies in collections
        all_genres = [genre for collection in queryset for movie in collection.movies.all() for genre in movie.genres.split(',')]
        top_genres = [genre[0] for genre in Counter(all_genres).most_common(3)]
        # i want to del the movies from collections
        
        collections = []
        for collection in serializer.data:
            del collection['movies']
            collections.append(collection)
        
       

        response_data = {
            'is_success': True,
            'data': {
                'collections': collections,
                'favourite_genres': ', '.join(top_genres),
            }
        }

        return Response(response_data, status=status.HTTP_200_OK)



# class CollectionDetailView(generics.RetrieveUpdateDestroyAPIView):
#     queryset = MovieCollection.objects.all()
#     serializer_class = MovieCollectionSerializer
#     permission_classes = [permissions.IsAuthenticated]

#     def update(self, request, *args, **kwargs):
#         partial = kwargs.pop("partial", False)
#         instance = self.get_object()
#         serializer = self.get_serializer(instance, data=request.data, partial=partial)
#         serializer.is_valid(raise_exception=True)
#         self.perform_update(serializer)
#         return Response(serializer.data)


# class CollectionMoviesView(generics.RetrieveAPIView):
#     queryset = MovieCollection.objects.all()
#     serializer_class = MovieCollectionSerializer
#     permission_classes = [permissions.IsAuthenticated]

#     def retrieve(self, request, *args, **kwargs):
#         instance = self.get_object()
#         serializer = self.get_serializer(instance)
#         return Response(serializer.data["movies"])

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.movies.all().delete()  # Deleting all movies related to the collection
        return Response(status=status.HTTP_204_NO_CONTENT)
