import datetime
from django.shortcuts import render
from rest_framework.decorators import api_view,authentication_classes
from .models import Account, BankDetails, UPIDetails,UserToken
from .serializers import AccountSerializer, BankSerializer, UpiSerializer
from rest_framework.response import Response
from rest_framework  import status
from django.contrib.auth.hashers import make_password
from .verify import send,check
from . authentication import JWTAuthentications, create_access_token,create_refresh_token,decode_refresh_token
from rest_framework import exceptions
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
from django.contrib import auth
from rest_framework import viewsets
from django.core.mail import send_mail
# Create your views here.


@api_view(['POST'])
def Register(request):
    try:
        data=request.data
        password=data['password']
        confirm_password=data['confirm_password']
        if password==confirm_password:
            userpassword=password
            print(userpassword)
        else:
            response=Response()
            response.data={
            'error':'password miss match'
            }
            return response
       
        mobile=data['mobile']
        email=data['email']
        anonymous=Account.objects.filter(email=email).exists()
        if anonymous:
            response=Response()
            response.data={
            'error':'this mobile email is already taken choose another one'
            }
            return response
        anonymous=Account.objects.filter(mobile=mobile).exists()
        if anonymous:
            response=Response()
            response.data={
            'error':'this mobile number is already taken choose another one'
            }
            return response

        
        
        user=Account.objects.create(
            first_name=data['first_name'],
            last_name=data['last_name'],
            email=data['email'],
            mobile=data['mobile'],            
            password=make_password(userpassword)                
         )   
        
        mobile=data['mobile']        
        send(mobile)        
        serializer=AccountSerializer(user ,many=False)
        return Response(serializer.data)
    except:        
        response=Response()
        response.data={
            'error':'user with this email already exists'
        }
        return response
     
    
  

@api_view(['POST'])
def verification(request):   
    print('enter')  
    data=request.data 
    code=data['code']
    mobile=data['mobile']
    # mobile=request.session['phone_number']
    print(mobile,'second')
    
    print(code)
    if check(mobile,code):      
        user=Account.objects.get(mobile=mobile)
        print(user.is_active)
        user.is_active=True
        email=user.email
        user.save()
        
        send_mail('Welcome ',
            'Thank You For Registering and verify successfully ,we gladly welcome you to our community ',
            'wedidsolutions@gmail.com'
            ,[email]   
            ,fail_silently=False)

        
        serializer=AccountSerializer(user,many=False)
        return Response(serializer.data)
    else:
        response=Response()
        response.data={
            'error':'invalid otp !! give currect otp'
        }
        return response
        # message={'detail':'otp is not valid'}
        # return Response(message,status=status.HTTP_400_BAD_REQUEST)
       
        
   
        # response=Response()
        # response.data={
        #     'otperror':' error found'
        # }
        # return response
        # message={'detail':'error in serializer'}
        # return Response(message,status=status.HTTP_400_BAD_REQUEST)
    
    
    
@api_view(['POST'])
def Login(request):
    data=request.data
    email=data['email']
    password=data['password']
    user=Account.objects.filter(email=email).first()
    print('wow')
    if user is None:
        response=Response()
        response.data={
            'message':'invalid credential'
        }
        return response
      
       
    if not user.check_password(password):
        response=Response()
        response.data={
            'message':'password miss match '
        }
        return response  
    
    
    user_verified=auth.authenticate(email=email,password=password)
    if user_verified:
        
        access_token=create_access_token(user.id)
        refresh_token=create_refresh_token(user.id)
        print(user.id)
        UserToken.objects.create(
            user_id=user.id,
            token=refresh_token,
            expired_at=datetime.datetime.utcnow()+datetime.timedelta(days=7)
            )        
        
        response=Response()
        response.set_cookie(key='refresh_token',value=refresh_token,httponly=True)
        response.data={
            'token':access_token,
            'refresh':refresh_token,
            'id':user.id,
            'first_name':user.first_name,
            'last_name':user.last_name,
            'email':user.email,       
            'count':user.count,
            'is_admin':user.is_admin,
        }
        # serializer=AccountSerializer(user,many=False)
        # return Response(serializer.data)
        return response
    else:
        response=Response()
        response.data={
            'message':'authtification fail failed '
        }
        return response  
        



@api_view(['GET'])
@authentication_classes([JWTAuthentications])
# @authentication_classes([ADMINAuth])
def alluser(request):
    user=Account.objects.all()
    serializer=AccountSerializer(user,many=True)    
    return Response(serializer.data)



@api_view(['POST'])
def refresh(request):
    data=request.data
    refresh=data['refresh']
    id=decode_refresh_token(refresh)
    if not UserToken.objects.filter(
        user_id=id,
        token=refresh,
        expired_at__gt=datetime.datetime.now(tz=datetime.timezone.utc)
    ).exists():
        response=Response()
        response.data={
            'message':'error'
        }
        return response
        raise exceptions.AuthenticationFailed('unauthenticate')
    
    access_token=create_access_token(id)
    return Response({
        'token':access_token,
    })
    
    
    
@api_view(['POST'])
# @authentication_classes([JWTAuthentications])
def Logout(request):
    print('heuuuu')
    refresh_token=request.COOKIES.get('refresh_token')
    # UserToken.objects.filter(user_id=request.user.id).delete()
    UserToken.objects.filter(token=refresh_token).delete()
    response=Response()
    response.delete_cookie(key='refresh_token')
    response.data={
        'message':'successfully logout'
    }
    return response



@api_view(['POST'])
def forgotpassword(request):
    data=request.data
    email=data['email']
    print(email)
    user=Account.objects.filter(email=email).exists()
    if user:
        print('enteredddd')
        user=Account.objects.get(email__exact=email)
        print(user)
        current_site = get_current_site(request)
        mail_subject ='Reset password'
        message= render_to_string('user/forgot_password_email.html',{
                'user':user,
                'domain': current_site,
                'uid':urlsafe_base64_encode(force_bytes(user.id)),
                'token':default_token_generator.make_token(user),

                    })
        to_email = email
        send_email=EmailMessage(mail_subject, message ,to=[to_email])
        print("here")
        send_email.send()
        message={'success':'email sented to your email'}
        return Response(message,status=status.HTTP_200_OK)
    else:
        response=Response()
        response.data={
            'error':'No account assosiate with this email'
        }
        return response
     
    

def resetpassword_validate(request,uidb64,token):
    if request.method=="POST":
        try:
            print('get in ittt')
            uid=urlsafe_base64_decode(uidb64).decode()
            user =Account._default_manager.get(pk=uid)
        except(TypeError,ValueError,OverflowError,Account.DoesNotExist):
            user=None
        if user is not None and default_token_generator.check_token(user,token): 
            print(uid)
            data=request.POST
            password =data['password']
            confirm_password =data['confirm_password']      
            uid=urlsafe_base64_decode(uidb64).decode()
            print(uid)
            if password == confirm_password:          
                print(uid)
                user=Account.objects.get(pk=uid)
                user.set_password(password)
                user.save()
                return render(request,'user/success.html')           
            
            else:
                message={'detail':'password miss match'}
                return Response(message,status=status.HTTP_400_BAD_REQUEST)
        else:
            message={'detail':'error found'}
            return Response(message,status=status.HTTP_400_BAD_REQUEST)
    else:
        return render(request,'user/reset_password.html')
    
    
@api_view(['POST'])
def resetPassword(request):
    data=request.data
    password =data['password']
    confirm_password =data['confirm_password']

    if password == confirm_password:
        uid =request.session.get('uid')
        print(uid)
        user=Account.objects.get(pk=uid)
        user.set_password(password)
        user.save()
        message={'success':'password reset successfully'}
        return Response(message,status=status.HTTP_200_OK)

    else:
        message={'error':'password missmatch'}
        return Response(message,status=status.HTTP_400_BAD_REQUEST)



    
@api_view(['GET'])
@authentication_classes([JWTAuthentications])
def userdata(request):
    print('ethiiittttp')
    user=request.user
    print(user,'fgdgfgs')
    data=Account.objects.get(email=user)
    serializer=AccountSerializer(data,many=False)
    return Response(serializer.data)


@api_view(['PATCH'])
@authentication_classes([JWTAuthentications])
def edituserdata(request):
    print('ddd')
    user=request.user
    edit=Account.objects.get(email=user)
    change=AccountSerializer(instance=edit,data=request.data)
    print('qqqq')
    if change.is_valid():
        print('djfjhk')
        change.save()
    return Response(change.data)



class userprofile(viewsets.ModelViewSet):
    authentication_classes=[JWTAuthentications]
    queryset=Account.objects.all()
    serializer_class=AccountSerializer
    
    
    
@api_view(['GET'])
@authentication_classes([JWTAuthentications])
def single_user_profile(request):
    user=request.user
    print(user)
    userr=Account.objects.get(email=user)
    serializer=AccountSerializer(userr,many=False)
    return Response(serializer.data)



@api_view(['POST'])
@authentication_classes([JWTAuthentications])
def change_password(request):
    data=request.data
    current_password=data['currentPassword']
    new_password=data['newPassword']
    confirm_password=data['confirmPassword']
    
    user=Account.objects.get(email=request.user)
    if new_password==confirm_password:            
        success=user.check_password(current_password)
        if success:
            user.set_password(new_password)
            user.save()
            message={'success':'password reset successfully'}
            return Response(message,status=status.HTTP_200_OK)
        else:
            message={'error':' current password   is not currect'}
            return Response(message,status=status.HTTP_400_BAD_REQUEST)
           
    else:
        message={'error':'password missmatch'}
        return Response(message,status=status.HTTP_400_BAD_REQUEST)


class bank_create(viewsets.ModelViewSet):
    authentication_classes=[JWTAuthentications]
    queryset=BankDetails.objects.all()
    serializer_class=BankSerializer



@api_view(['GET'])
@authentication_classes([JWTAuthentications])
def bank_of_user(request):
    user=request.user    
    userr=BankDetails.objects.filter(user=user)
    serializer=BankSerializer(userr,many=True)
    return Response(serializer.data)


class upi_create(viewsets.ModelViewSet):
    authentication_classes=[JWTAuthentications]
    queryset=UPIDetails.objects.all()
    serializer_class=UpiSerializer


@api_view(['GET'])
@authentication_classes([JWTAuthentications])
def upi_of_user(request):
    user=request.user    
    userr=UPIDetails.objects.filter(user=user)
    serializer=UpiSerializer(userr,many=True)
    return Response(serializer.data)
