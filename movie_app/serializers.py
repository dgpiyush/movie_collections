# movie_app/serializers.py
from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from movie_app.models import Collection, Movie


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True, style={"input_type": "password"})

    def validate(self, data):
        username = data.get("username", None)
        password = data.get("password", None)

        if username and password:
            user = authenticate(username=username, password=password)
            if user and user.is_active:
                data["user"] = user
            else:
                raise serializers.ValidationError(
                    {"message": "Incorrect credentials. Please try again."}
                )
        else:
            raise serializers.ValidationError(
                "Both username and password are required."
            )

        return data


class RegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, style={"input_type": "password"})

    class Meta:
        model = User
        fields = ["username", "password"]

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class MovieSerializer(serializers.ModelSerializer):
    uuid = serializers.UUIDField(read_only=True)
    class Meta:
        model = Movie
        fields = ['title', 'description', 'genres', 'uuid']

class CollectionSerializer(serializers.ModelSerializer):
    movies = MovieSerializer(many=True)
    uuid = serializers.UUIDField(read_only=True)

    class Meta:
        model = Collection
        fields = ['title', 'description', 'uuid', 'movies']
    
    def create(self, validated_data):
        movies_data = validated_data.pop('movies', [])  # Extract movie data
        collection = Collection.objects.create(**validated_data)
        # collection = Collection.objects.all()


        # Create and associate movies with the collection
        for movie_data in movies_data:
            movie = MovieSerializer(data=movie_data)
            movie.is_valid(raise_exception=True)
            collection.movies.add(movie.save())
        return collection
    