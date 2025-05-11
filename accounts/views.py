import stripe
import os
from django.conf import settings
from django.contrib.auth import authenticate, get_user_model
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from dotenv import load_dotenv
from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from rest_framework import serializers
from .serializers import RegisterSerializer, ProfileSerializer
from .utils import generate_password_reset_token, verify_password_reset_token

env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path=env_path)

User = get_user_model()
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')


@api_view(['POST'])
def login_user(request):
    if request.method == 'POST':
        username = request.data.get('username')
        password = request.data.get('password')
        is_staff = request.data.get('is_staff')
        is_premium = request.data.get('is_premium')
        

        print(f"Attempting to authenticate with username: {username} and password: {password}")
        
        user = authenticate(username=username, password=password)

        if user is not None:
            if user.is_locked:
                return Response(
                    {"message": "このユーザーは現在ロックされています"},
                    status=status.HTTP_403_FORBIDDEN
                )
            from rest_framework_simplejwt.tokens import RefreshToken
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)

            return Response(
              {
                    "message": "ログイン成功",
                    "access_token": access_token,
                    "refresh_token": str(refresh),
                    "username": user.username,
                    "is_premium": user.is_premium,
                    "is_staff": user.is_staff,
                },                
              status=status.HTTP_200_OK
            )
        else:
            return Response(
                {"message": "ユーザー名またはパスワードが間違っています"},
                status=status.HTTP_401_UNAUTHORIZED
            )
            
            
@api_view(['POST'])
def register_user(request):
    if request.method == 'POST':
        serializer = RegisterSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()

            return Response(
                {"message": "ユーザー登録成功", "uid": user.id}, 
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class ProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    image = serializers.ImageField(use_url=True)

    def get(self, request):
        serializer = ProfileSerializer(request.user)
        return Response(serializer.data)

    def put(self, request):
        # プロフィール更新処理
        serializer = ProfileSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def send_password_reset_email(request):
    email = request.data.get("email")
    if not email:
        return Response({"message": "メールアドレスを入力してください"}, status=400)

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response({"message": "ユーザーが見つかりません"}, status=404)

    token = generate_password_reset_token(user)
    reset_link = f"http://localhost:3000/reset-password?token={token}"

    send_mail(
        subject="パスワードリセット",
        message=f"以下のリンクからパスワードを再設定してください:\n{reset_link}",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
    )

    return Response({"message": "パスワード再設定リンクを送信しました"}, status=200)

@api_view(['POST'])
def reset_password(request):
    token = request.data.get("token")
    new_password = request.data.get("new_password")

    user_id = verify_password_reset_token(token)
    if not user_id:
        return Response({"message": "無効または期限切れのトークンです"}, status=400)

    user = get_object_or_404(User, pk=user_id)
    user.set_password(new_password)
    user.save()

    return Response({"message": "パスワードが更新されました"}, status=200)

@api_view(['GET'])
@permission_classes([AllowAny])
def admin_user_list(request):
    users = User.objects.all().values('id', 'username', 'email', 'age', 'is_active', 'is_premium', 'is_staff', 'is_locked')
    return Response(list(users))

@api_view(['POST'])
@permission_classes([IsAdminUser])
def toggle_user_lock(request, user_id):
    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return Response({"message": "ユーザーが見つかりません"}, status=404)

    user.is_locked = not user.is_locked
    user.save()

    return Response({
        "message": "ユーザーのロック状態を変更しました",
        "user_id": user.id,
        "is_locked": user.is_locked
    }, status=200)
    
@api_view(['DELETE'])
@permission_classes([IsAdminUser])
def delete_user(request, user_id):
    confirm = request.data.get("confirm")

    if confirm != True:
        return Response({"message": "削除確認が必要です"}, status=403)

    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return Response({"message": "ユーザーが見つかりません"}, status=404)

    if user.is_superuser:
        return Response({"message": "スーパーユーザーは削除できません"}, status=403)

    user.delete()
    return Response({"message": "ユーザーを削除しました"}, status=200)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_payment_intent(request):
    try:
        # 有料オプションの料金　日本円で500円(計算が1銭だから500銭x100=500円)
        amount = 500 * 100
        currency = 'jpy'

        intent = stripe.PaymentIntent.create(
            amount=amount,
            currency=currency,
            automatic_payment_methods={'enabled': True},
        )

        return Response({'clientSecret': intent.client_secret}, status=200)

    except Exception as e:
        return Response({'error': str(e)}, status=400)
    
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def activate_premium(request):
    user = request.user
    print(f'Before saving: {user.is_premium}')  # 保存前に出力
    user.is_premium = True
    user.save()
    print(f'After saving: {user.is_premium}')  # 保存後に出力

    return Response({'message': 'プレミアムが有効になりました！'})
