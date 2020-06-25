import hashlib

from django.contrib.auth import authenticate
from django.core.validators import validate_email
from django.shortcuts import get_object_or_404
from django.db.models import Avg

from rest_framework import exceptions, serializers
from rest_framework.relations import SlugRelatedField
from rest_framework_simplejwt.serializers import TokenObtainSerializer,\
    TokenObtainPairSerializer

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.exceptions import (
    ValidationError,
    PermissionDenied,
    AuthenticationFailed
)

from .models import User, Categories, Genres, Titles, Review, Comments


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        fields = [
            "first_name",
            "last_name",
            "username",
            "bio",
            "email",
            "role"]
        model = User


# class YamdbTokenObtainSerializer(TokenObtainSerializer):
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#
#         self.fields[self.username_field] = serializers.CharField()
#         self.fields["password"] = serializers.CharField(required=False)
#         self.fields["conformation_code"] = serializers.CharField()
#
#     def validate(self, attrs):
#         email = attrs[self.username_field]
#         try:
#             validate_email(email)
#         except Exception:
#             raise serializers.ValidationError("Not valid email")
#
#         if not User.objects.filter(email=email).first():
#             hash_email = hashlib.sha256(email.encode("utf-8")).hexdigest()
#             print(hash_email)
#             if hash_email != attrs["conformation_code"]:
#                 raise serializers.ValidationError("credential dosen't match")
#             User.objects.create_user(
#                 email=email, username="", password=attrs["conformation_code"]
#             )
#
#         authenticate_kwargs = {
#             self.username_field: attrs[self.username_field],
#             "password": attrs["conformation_code"],
#         }
#         try:
#             authenticate_kwargs["request"] = self.context["request"]
#         except KeyError:
#             pass
#
#         self.user = authenticate(**authenticate_kwargs)
#         if self.user is None or not self.user.is_active:
#             raise exceptions.AuthenticationFailed(
#                 self.error_messages["no_active_account"], "no_active_account",
#             )
#
#         return {}
#
#
# class YamdbTokenObtainPairSerializer(YamdbTokenObtainSerializer):
#     @classmethod
#     def get_token(cls, user):
#         return RefreshToken.for_user(user)
#
#     def validate(self, attrs):
#         data = super().validate(attrs)
#         refresh = self.get_token(self.user)
#         data["refresh"] = str(refresh)
#         data["access"] = str(refresh.access_token)
#         return data

class YamdbAuthTokenSerializer(serializers.ModelSerializer):
    password = serializers.CharField(required=False)
    email = serializers.EmailField()
    conformation_code = serializers.CharField()

    class Meta:
        model = User
        fields = ('email', 'password', 'conformation_code')

    def validate(self, data):
        email = self.initial_data['email']
        hash_email = hashlib.sha256(email.encode("utf-8")).hexdigest()
        conformation_code = data['conformation_code']
        if hash_email != conformation_code:
            raise serializers.ValidationError("credential dosen't match")
        user = User.objects.create_user(email=email, password=conformation_code)
        refresh = TokenObtainPairSerializer.get_token(user)
        del data['email']
        del data['conformation_code']
        data['token'] = str(refresh.access_token)
        return data


class CategoriesSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('name', 'slug')
        model = Categories


class GenresSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('name', 'slug')
        model = Genres


# Custom slug relational fields for TitleSerializer
class CustomSlugRelatedField(serializers.SlugRelatedField):
    def to_representation(self, obj):
        return {'name': obj.name, 'slug': obj.slug}


# Custom slug relational fields for TitleSerializer
class GenreField(SlugRelatedField):
    def to_representation(self, value):
        serializer = GenresSerializer(value)
        return serializer.data


class TitlesSerializer(serializers.ModelSerializer):
    rating = serializers.SerializerMethodField(read_only=True)
    category = CustomSlugRelatedField(
        queryset=Categories.objects.all(),
        slug_field='slug'
    )
    genre = CustomSlugRelatedField(
        queryset=Genres.objects.all(),
        slug_field='slug', many=True
    )

    class Meta:
        fields = (
            'id', 'name', 'year',
            'rating', 'description',
            'genre', 'category'
        )
        model = Titles

    def get_rating(self, title):
        scores = Review.objects.filter(title_id=title.id).aggregate(
            Avg('score'))
        if scores:
            return scores['score__avg']
        return None


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.username')
    score = serializers.IntegerField(min_value=1, max_value=10)

    class Meta:
        fields = ('id', 'text', 'author', 'score', 'pub_date')
        model = Review

    def create(self, validated_data):
        author = self.context['request'].user
        request = self.context.get('request')
        title_id = request.parser_context['kwargs']['title_id']
        method = request.method
        title = get_object_or_404(Titles, pk=title_id)
        review = Review.objects.filter(title_id=title_id, author=author)
        if method == 'POST' and review:
            raise ValidationError('Вы уже писали отзыв на это произведение')
        return Review.objects.create(
            author=author,
            title_id=title_id,
            **validated_data
        )

    def update(self, instance, validated_data):
        author = self.context['request'].user
        if not author.is_authenticated:
            raise AuthenticationFailed()
        if instance.author != author:
            raise PermissionDenied()
        instance.text = validated_data.get('text', instance.text)
        instance.score = validated_data.get('score', instance.score)
        instance.pub_date = validated_data.get('pub_date', instance.pub_date)
        instance.save()
        return instance


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.username')

    class Meta:
        fields = ('id', 'author', 'text', 'pub_date')
        model = Comments

    def create(self, validated_data):
        author = self.context['request'].user
        request = self.context.get('request')
        review_id = request.parser_context['kwargs']['review_id']
        review = get_object_or_404(Review, pk=review_id)
        return Comments.objects.create(
            author=author,
            review_id=review_id,
            **validated_data
        )

    def update(self, instance, validated_data):
        author = self.context['request'].user
        if not author.is_authenticated:
            raise AuthenticationFailed()
        if instance.author != author:
            raise PermissionDenied()
        instance.text = validated_data.get('text', instance.text)
        instance.pub_date = validated_data.get('pub_date', instance.pub_date)
        instance.save()
        return instance
