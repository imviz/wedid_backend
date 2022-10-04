from rest_framework.decorators import api_view,authentication_classes
from user.models import Account,UserToken,Categories,District,City
from rest_framework.response import Response
import random
import datetime
from user.authentication import ADMINAuth, JWTAuthentications
from .models import Rent_detail, RentComplaint
from .serializer import RentComplaintSerializer, RentSerializer
from user.authentication import JWTAuthentications
from jobportal.serializer import  CategorySerializer
from rest_framework import generics
from rest_framework import filters
from rest_framework import viewsets
from rest_framework  import status
# Create your views here.

@api_view(["POST"])
@authentication_classes([JWTAuthentications])
def rentpost(request):
    data=request.data
    user=request.user
    mobiles=user.mobile  
    print(data)
    print(mobiles)
    print(data)
    yr= int(datetime.date.today().strftime('%Y'))
    dt= int(datetime.date.today().strftime('%d'))
    mt= int(datetime.date.today().strftime('%m'))
    d=datetime.date(yr,mt,dt)
    current_date =d.strftime("%Y%m%d")  
    val=(random.randint(1, 99))
    order_number=current_date +str(user.id)+str(val)
    print(order_number)
   
    
    rent= Rent_detail.objects.create(        
        user=user,
        mobile=mobiles,
        district_id=request.data['district'],
        city_id=request.data['city'],
        title=request.data['title'],
        category_id=request.data['category'],
        discriptions=request.data['discription'],
        sub_mobile=request.data['sub_mobile'],           
        place=request.data['place'],
        address=request.data['address'],
        rate=request.data['rate'],
        slug=request.data['slug'],
        available=True,
        ordernumber=order_number,  
        image=request.FILES['image'],
        image1=request.FILES['image1'],
        image2=request.FILES['image2'],
        price_in=request.data['price_in'],
        valid_at=request.data['date'],        
                  
    )     
    serializer=RentSerializer(rent,many=False)
    return Response(serializer.data)                    


# category for rent
@api_view(['GET'])
@authentication_classes([JWTAuthentications])
def rentcategories(request):
    rent=Categories.objects.filter(category_of='rent')
    serializer=CategorySerializer(rent,many=True)
    return Response(serializer.data)


# all data
@api_view(['GET'])
@authentication_classes([JWTAuthentications])
def all_rent_show(request):
    try:  
        rent=Rent_detail.objects.filter(payment='True').order_by('id')
        serializer=RentSerializer(rent,many=True)
        return Response(serializer.data)
    except:
        response=Response()
        response.data={
            'error':'error in request'
        }
        return response 


# for compliting the post and showing on posted surface
@api_view(['POST'])
# @authentication_classes([JWTAuthentications])
def rentpaymentdone(request):
    data=request.data
    print(data)
    orderid=data['order_number']
    print(orderid)
    rent=Rent_detail.objects.filter(ordernumber=orderid).exists()
    if not rent:
        response=Response()
        response.data={
            'error':'this item is not present '
        }
        return response 
    else:
        rent=Rent_detail.objects.get(ordernumber=orderid)
        rent.payment=True
        rent.save()
        serializer=RentSerializer(rent,many=False)
        return Response(serializer.data)
 
    
#filter with district 
 
@api_view(['GET'])
@authentication_classes([JWTAuthentications])
def disctrict_rent_show(request,id):
    try:        
        district=District.objects.get(id=id)
        print(district)
        rent=Rent_detail.objects.filter(district=district,payment='True',booked='False',available='True')
        serializer=RentSerializer(rent,many=True)
        return Response(serializer.data)
    except:
        response=Response()
        response.data={
            'error':'error in request'
        }
        return response 
    
    


 
#  filter with category and place
@api_view(['GET'])
@authentication_classes([JWTAuthentications])
def filter_rent_show(request,id,cid):
    try:
        category=Categories.objects.get(id=id)
        print(category)
        city=City.objects.get(id=cid)
        print(city)
        rent=Rent_detail.objects.filter(category=category,city=city,payment='True',booked='False',available='True')
        serializer=RentSerializer(rent,many=True)
        return Response(serializer.data)
    except:
        response=Response()
        response.data={
            'error':'error in request'
        }
        return response 
    
class Rentitems(generics.ListAPIView):
    queryset =Rent_detail.objects.filter(payment='True')
    serializer_class = RentSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['title','place','category__name','district__district','city__city']
    # search_fields = ['title']


# single view of rent

@api_view(['GET'])
@authentication_classes([JWTAuthentications])
def singlerentview(request,id):
    rent=Rent_detail.objects.get(id=id)
    serializer=RentSerializer(rent,many=False)
    return Response(serializer.data)




@api_view(['GET'])
@authentication_classes([JWTAuthentications])
def Giving_rent_history(request):
    user=request.user
    job=Rent_detail.objects.filter(user__email=user)
    serializer=RentSerializer(job,many=True)
    return Response(serializer.data)


class Edit_giving_job(viewsets.ModelViewSet):
    authentication_classes=[JWTAuthentications]
    queryset=Rent_detail.objects.all()
    serializer_class=RentSerializer


@api_view(['GET'])
@authentication_classes([JWTAuthentications])
def taking_rent_history(request):
    user=request.user
    print(user,'kkkkkkk')
    job=Rent_detail.objects.filter(booked_person__email=user)
    serializer=RentSerializer(job,many=True)
    return Response(serializer.data)
  
  
  
# total completed services
@api_view(['GET'])
@authentication_classes([JWTAuthentications])
def total_completed_task(request):
    user=request.user
    verify=Rent_detail.objects.filter(user=user,item_backed=True).exists()
    if verify:
        verify=Rent_detail.objects.filter(user=user,item_backed=True)
        
    else:
        ver=Rent_detail.objects.filter(booked_person__email=user,item_backed=True).exits()
        if ver:
           verify=Rent_detail.objects.filter(booked_person__email=user,item_backed=True) 

    serializer=RentSerializer(verify,many=True)
    return Response(serializer.data)


@api_view(["POST"])
@authentication_classes([JWTAuthentications])
def rent_complaint(request):
    data=request.data
    user=request.user
    rent=data['jobId'] 
    typeId=Rent_detail.objects.filter(user=user).exists()
    if typeId:
        type='buyer'
    else:
        type='worker'
        
    value=RentComplaint.objects.filter(rent=rent).exists()
    if value:       
        if type=='buyer':
            verify=RentComplaint.objects.filter(rent=rent,buyer=True).exists()
            if verify:
                message={'error':'you are already submitted the complaint'}
                return Response(message,status=status.HTTP_400_BAD_REQUEST)
            
            else:
                comp=RentComplaint.objects.create(
                user=user,
                rent_id=rent,
                complaint=data['complaint'],
                buyer=True,    
            )
                serializer=RentComplaintSerializer(comp,many=False)
                return Response(serializer.data)         
        else:
            verify=RentComplaint.objects.filter(rent=rent,buyer=False).exists()
            if verify:
                message={'error':'you are already submitted the complaint'}
                return Response(message,status=status.HTTP_400_BAD_REQUEST)
            else:
                comp=RentComplaint.objects.create(
                user=user,
                rent_id=rent,
                complaint=data['complaint'],
                buyer=False,    
                )
                serializer=RentComplaintSerializer(comp,many=False)
                return Response(serializer.data)     

            
    else:
        if type=='buyer':
            verify=RentComplaint.objects.filter(user=user,buyer=True).exists()
            comp=RentComplaint.objects.create(
                user=user,
                rent_id=rent,
                complaint=data['complaint'],
                buyer=True,    
            )
            serializer=RentComplaintSerializer(comp,many=False)
            return Response(serializer.data)           
        else:
            comp=RentComplaint.objects.create(
                user=user,
                rent_id=rent,
                complaint=data['complaint'],
                buyer=False,    
            )
            serializer=RentComplaintSerializer(comp,many=False)
            return Response(serializer.data)      
        
                        
  
