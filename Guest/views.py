import os
import re
from datetime import *

from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.core.serializers import serialize
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import redirect, render

# from .forms import SignUpForm
from django.template import loader
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from user.models import *


import logging

logger = logging.getLogger('django')


from user.models import CarouselImages


def index2(request):
    template = loader.get_template("index2.html")
    context = {}

    cloths = Cloth.objects.all().filter(is_approved=True)
    slides = CarouselImages.objects.filter(is_active=True).order_by("priority")
    if cloths:
        n = len(cloths)
        nslide = n // 3 + (n % 3 > 0)
        cloths_data = [cloths, range(1, nslide), n]
        context.update({"cloths": cloths_data})
        context.update({"images": slides})
    logger.info(f"User {request.user.email} accessed the index2 page.")
    return HttpResponse(template.render(context, request))


def home(request):
    template = loader.get_template("home.html")
    context = {}
    context.update({"result": ""})
    context.update({"msg": "Search your query"})
    return HttpResponse(template.render(context, request))


def search(request):
    template = loader.get_template("home.html")
    context = {}

    if request.method == "GET":
        typ = request.GET.get("type", "")
        q = request.GET.get("q", "")
        context.update({"type": typ, "q": q})

        results = Cloth.objects.filter(Q(type__icontains=q) | Q(brand__icontains=q))
        logger.info(f"Search query: {q} by user: {request.user.email}")

        if not results.exists():
            messages.success(request, "No matching results for your query..")

        result = [results, len(results)]
        context.update({"result": result})

    return HttpResponse(template.render(context, request))


def about(request):
    template = loader.get_template("about.html")
    context = {}

    room = Cloth.objects.all()
    if bool(room):
        context.update({"room": room})
    house = Cloth.objects.all()
    if bool(house):
        context.update({"house": house})
    logger.info(f"User {request.user.email} accessed the about page.")    
    return HttpResponse(template.render(context, request))


def contact(request):
    template = loader.get_template("contact.html")
    context = {}

    if request.method == "POST":
        subject = request.POST["subject"]
        email = request.POST["email"]
        body = request.POST["body"]
        regex = "^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$"
        if re.search(regex, email):
            pass
        else:
            template = loader.get_template("register.html")
            context.update({"msg": "invalid email"})
            return HttpResponse(template.render(context, request))
        contact = Contact(subject=subject, email=email, body=body)
        contact.save()
        context.update({"msg": "msg send to admin"})
        logger.info(f"Contact form submitted by user: {request.user.email}")
        return HttpResponse(template.render(context, request))
    else:
        context.update({"msg": ""})
        return HttpResponse(template.render(context, request))


def cloth_descr(request):
    template = loader.get_template("cloth_desc.html")
    context = {}

    if request.method == "GET":
        cloth_id = request.GET.get("id")
        try:
            cloth = Cloth.objects.get(cloth_id=cloth_id)
            context.update({"val": cloth})
            context.update({"type": "Cloth"})
            user = User.objects.get(email=cloth.user_email)
            context.update({"user": user})
        except Cloth.DoesNotExist:
            return HttpResponse("Cloth not found", status=404)

    return HttpResponse(template.render(context, request))


def register(request):
    if request.method == "GET":
        return render(request, "register.html", {"msg": ""})

    name = request.POST["name"]
    email = request.POST["email"]
    location = request.POST["location"]
    city = request.POST["city"]
    state = request.POST["state"]
    phone = request.POST["phone"]
    pas = request.POST["pass"]
    cpas = request.POST["cpass"]
    regex = "^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$"
    if re.search(regex, email):
        pass
    else:
        template = loader.get_template("register.html")
        context = {"msg": "invalid email"}
        return HttpResponse(template.render(context, request))

    if len(str(phone)) != 10:
        template = loader.get_template("register.html")
        context = {"msg": "invalid phone number"}
        return HttpResponse(template.render(context, request))

    if pas != cpas:
        template = loader.get_template("register.html")
        context = {"msg": "password did not matched"}
        return HttpResponse(template.render(context, request))
    already = User.objects.filter(email=email)
    if bool(already):
        template = loader.get_template("register.html")
        context = {"msg": "email already registered"}
        return HttpResponse(template.render(context, request))

    user = User.objects.create_user(
        name=name,
        email=email,
        location=location,
        city=city,
        state=state,
        number=phone,
        password=pas,
    )
    user.save()
    logger.info(f"New user registered: {email}")
    login(request, user)
    messages.success(request, "Registration successful. You can now log in.")
    return redirect("/profile/")


@login_required(login_url="/login")
def profile(request):
    report = Contact.objects.filter(email=request.user.email)
    cloth = Cloth.objects.filter(user_email=request.user)
    house = House.objects.filter(user_email=request.user)
    clothno = cloth.count()
    housecnt = house.count()
    reportcnt = report.count()
    rooms = []
    houses = []
    if bool(cloth):
        n = len(cloth)
        nslide = n // 3 + (n % 3 > 0)
        rooms = [cloth, range(1, nslide), n]
    # if bool(house):
    #     n = len(house)
    #     nslide = n // 3 + (n % 3 > 0)
    #     houses = [house, range(1, nslide), n]

    context = {
        "user": request.user,
        "report": report,
        "reportno": reportcnt,
        "clothno": clothno,
        "houseno": housecnt,
    }
    context.update({"room": rooms})
    context.update({"house": houses})
    logger.info(f"User {request.user.email} accessed the profile page.")
    return render(request, "profile.html", context=context)


from django.http import JsonResponse

from Guest.serializers import ClothSerializer


# @login_required(login_url='/login')
def get_cloth_list(request):
    cloth_list = Cloth.objects.all()
    serializer = ClothSerializer(
        cloth_list, many=True
    )  # Serialize the queryset to JSON
    return JsonResponse({"cloth_list": serializer.data}, safe=False)


@login_required(login_url="/login")
def post_cloth(request):
    if request.method == "GET":
        context = {"user": request.user}
        return render(request, "post_cloth.html", context)

    elif request.method == "POST":
        try:
            size = request.POST["size"]
            cloth_type = request.POST["type"]
            brand = request.POST["brand"]
            material = request.POST["material"]
            color = request.POST["color"]
            rent_cost = request.POST["rent_cost"]
            availability = request.POST.get("availability") == "on"
            description = request.POST["description"]
            img = request.FILES.get("img")  # Use get() to make it optional

            user_obj = User.objects.get(email=request.user.email)

            cloth = Cloth.objects.create(
                user_email=user_obj,
                size=size,
                type=cloth_type,
                brand=brand,
                material=material,
                color=color,
                rent_cost=rent_cost,
                availability=availability,
                description=description,
                img=img,  # img will be None if not provided
            )
            messages.success(request, "Cloth posted successfully.")
            logger.info(f"Cloth posted successfully by user: {request.user.email}")
            return render(request, "post_cloth.html")

        except Exception as e:
            return HttpResponse(f"Error: {str(e)}", status=500)


def deleter(request):
    if request.method == "GET":
        id = request.GET["id"]
        instance = Cloth.objects.get(cloth_id=id)
        instance.delete()
        messages.success(request, "Cloth details deleted successfully..")
        logger.info(f"Cloth with ID {id} deleted by user: {request.user.email}")
    return redirect("/profile")


def deleteh(request):
    if request.method == "GET":
        id = request.GET["id"]
        instance = House.objects.get(house_id=id)
        instance.delete()
        messages.success(request, "House details deleted successfully..")
    return redirect("/profile")


def login_view(request):
    if request.method == "GET":
        return render(request, "login.html")

    email = request.POST["email"]
    password = request.POST["password"]
    user = authenticate(request, email=email, password=password)

    if user is not None:
        login(request, user)
        logger.info(f"User {email} logged in successfully.")
        return redirect("/")
    else:
        template = loader.get_template("login.html")
        context = {"msg": "Email and password, you entered, did not matched."}
        return HttpResponse(template.render(context, request))


from django.contrib.auth import authenticate
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status, viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView


@method_decorator(csrf_exempt, name="dispatch")
class ClothViewSet(viewsets.ModelViewSet):
    queryset = Cloth.objects.all()
    serializer_class = ClothSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(user_email=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user_email=self.request.user)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)

        response_data = {
            "status": "success",
            "count": queryset.count(),
            "data": serializer.data,
        }
        return Response(response_data, status=status.HTTP_200_OK)


import json


@csrf_exempt
def generate_token(request):
    data = json.loads(request.body)
    email = data.get("email")
    password = data.get("password")
    if email is None or password is None:
        return JsonResponse({"error": "Email and password are required."}, status=400)
    user = User.objects.get(email=email)
    if user is None:
        return JsonResponse({"error": "User not found."}, status=404)
    try:
        token = Token.objects.get(user=user)
        logger.info(f"Token already exists for user: {user.email}")
    except Token.DoesNotExist:
        token = Token.objects.create(user=user)
        logger.info(f"Token created for user: {user.email}")
    return JsonResponse({"token": f"Token {token.key}"}, status=200)
