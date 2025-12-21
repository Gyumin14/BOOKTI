from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import Book, Profile

class BookCardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        field=["id", "title", "author", "cover_url"]



class BookDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ["id", "title", "author", "description", "cover_url", "category", "created_at"]


User = get_user_model()

class SignupSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)

    name = serializers.CharField(max_length=50)
    birth_date = serializers.DateField()

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("이미 사용 중인 아이디입니다.")
        return value

    def validate(self, attrs):
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError({"password": "비밀번호가 일치하지 않습니다."})
        return attrs

    def create(self, validated_data):
        username = validated_data["username"]
        password = validated_data["password"]
        name = validated_data["name"]
        birth_date = validated_data["birth_date"]

        # 유저 생성
        user = User.objects.create_user(username=username, password=password)

        # 프로필 생성
        Profile.objects.create(user=user, name=name, birth_date=birth_date)

        return user
    
class BooktiSubmitSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    bookti_code = serializers.CharField(max_length=4)

    def validate_bookti_code(self, value):
        value = value.strip().upper()
        if len(value) != 4:
            raise serializers.ValidationError("BOOKTI 코드는 4글자여야 합니다.")
        allowed = set("PEFCLDRA")
        if any(ch not in allowed for ch in value):
            raise serializers.ValidationError("BOOKTI 코드 형식이 올바르지 않습니다.")
        return value
    
