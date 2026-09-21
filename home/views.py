import random
import base64
import cv2
import numpy as np
import os

from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.core.paginator import Paginator
from django.utils import timezone
from datetime import timedelta
from django.conf import settings

from ultralytics import YOLO
from twilio.rest import Client
from sklearn.cluster import KMeans

from product.models import Product, Cart, Wishlist, Order
from .models import User, Address, OTP


# =========================
# YOLO MODEL
# =========================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "yolov8n-face.pt")
model = YOLO(MODEL_PATH)


# =========================
# SAFE USER HANDLING
# =========================
def get_user(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return None
    return User.objects.filter(id=user_id).first()


# =========================
# LOGIN DECORATOR (SAFE)
# =========================
def login_required(view_func):
    def wrapper(request, *args, **kwargs):
        user = get_user(request)
        if not user:
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper


# =========================
# OTP SEND
# =========================
def send_otp(mobile, otp):
    try:
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

        client.messages.create(
            body=f"Your Almirah OTP is {otp}",
            from_=settings.TWILIO_PHONE_NUMBER,
            to="+91" + mobile
        )
    except Exception as e:
        print("TWILIO ERROR:", e)


# =========================
# HOME
# =========================
@login_required
def home(request):

    products = Product.objects.all()
    detected_tone = None
    image_preview = None
    recommended_colors = []
    category = request.GET.get('category')
    colors = request.GET.getlist('color')
    max_price = request.GET.get('max_price')
    query = request.GET.get('q')
    selected_colors = colors

    if query:
        products = products.filter(
            Q(product_name__icontains=query) |
            Q(brand__icontains=query) |
            Q(product_description__icontains=query)
        )

    if request.method == "POST":

        image_file = request.FILES.get("image")
        captured_image = request.POST.get("captured_image")

        img = None

        if image_file:
            file_bytes = np.asarray(bytearray(image_file.read()), dtype=np.uint8)
            img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

        elif captured_image:
            try:
                _, imgstr = captured_image.split(";base64,")
                img = cv2.imdecode(
                    np.frombuffer(base64.b64decode(imgstr), np.uint8),
                    cv2.IMREAD_COLOR
                )
            except:
                img = None

        if img is not None:

            img = cv2.convertScaleAbs(img, alpha=1.15, beta=15)

            _, buffer = cv2.imencode(".jpg", img)
            image_preview = base64.b64encode(buffer).decode()

            results = model(img)[0]

            if len(results.boxes) > 0:

                best_box = max(results.boxes, key=lambda b: float(b.conf[0]))

                if float(best_box.conf[0]) > 0.5:

                    x1, y1, x2, y2 = map(int, best_box.xyxy[0])
                    face = img[y1:y2, x1:x2]

                    if face.size > 0:

                        face = cv2.resize(face, (250, 250))
                        hsv = cv2.cvtColor(face, cv2.COLOR_BGR2HSV)

                        skin_mask = cv2.inRange(
                            hsv,
                            np.array([0, 30, 60]),
                            np.array([25, 180, 255])
                        )

                        lab = cv2.cvtColor(face, cv2.COLOR_BGR2LAB)
                        pixels = lab[skin_mask > 0]

                        if len(pixels) > 100:

                            pixels = pixels.reshape(-1, 3)

                            kmeans = KMeans(n_clusters=3, n_init=10, random_state=42)
                            kmeans.fit(pixels)

                            centers = kmeans.cluster_centers_
                            valid = sorted(centers, key=lambda x: x[0], reverse=True)

                            L, A, B = map(int, valid[0])

                            # DEPTH
                            if L > 210:
                                depth = "Very Light"
                            elif L > 170:
                                depth = "Light"
                            elif L > 140:
                                depth = "Light-Medium"
                            elif L > 100:
                                depth = "Medium"
                            elif L > 70:
                                depth = "Deep-tan"
                            else:
                                depth = "Very Deep"

                            # UNDERTONE
                            if A > 145 and B > 145:
                                undertone = "Warm"
                            elif A < 135 and B < 135:
                                undertone = "Cool"
                            elif 135 <= A <= 145:
                                undertone = "Neutral"
                            else:
                                undertone = "Olive"

                            detected_tone = f"{depth} + {undertone}"
                            

                            if "Warm" in detected_tone:
                                recommended_colors = ["Mustard", "Olive", "Coral", "Brown", "Gold"]

                            elif "Cool" in detected_tone:
                                recommended_colors = ["Blue", "Purple", "Pink", "Silver", "Teal"]

                            elif "Neutral" in detected_tone:
                                recommended_colors = ["White", "Black", "Navy", "Beige", "Grey"]

                            elif "Olive" in detected_tone:
                                recommended_colors = ["Earthy Green", "Tan", "Cream", "Rust", "Khaki"]
                                paginator = Paginator(products, 12)
                                page = request.GET.get('page')
                                products = paginator.get_page(page)
        
    # if max_price:
    #     pass
    # if colors:
    #     pass
    # if category:
    #     pass
    
    if recommended_colors:
        products = products.filter(colour__in=recommended_colors)

    if category:
        products = products.filter(sub_category__iexact=category)

    if colors:
        products = products.filter(colour__in=colors)

    if max_price:
        products = products.filter(max_retail_price__lte=max_price)

    paginator = Paginator(products, 12)  # 12 products per page
    page_number = request.GET.get('page')

    products = paginator.get_page(page_number)


    return render(request, "base_home.html", {
    "products": products,
    "tone": detected_tone,
    "image_preview": image_preview,
    "recommended_colors": recommended_colors,
    'selected_colors': selected_colors,
})


def product_detail(request, id):
    product = get_object_or_404(Product, id=id)

    related_products = Product.objects.filter(
        category=product.category
    ).exclude(id=id)[:4]

    return render(request, "product.html", {
        "product": product,
        "related_products": related_products
    })


# =========================
# LOGIN / OTP
# =========================
def login_view(request):
    if request.method == "POST":
        mobile = request.POST.get('mobile')

        otp = str(random.randint(100000, 999999))
        OTP.objects.create(mobile=mobile, otp=otp)

        send_otp(mobile, otp)

        request.session['mobile'] = mobile
        return redirect('verify_otp')

    return render(request, 'login_page.html')


def verify_otp(request):
    if request.method == "POST":

        mobile = request.session.get('mobile')
        entered_otp = request.POST.get('otp', '').strip()

        otp_obj = OTP.objects.filter(mobile=mobile).order_by('-created_at').first()

        if otp_obj:

            if otp_obj.created_at < timezone.now() - timedelta(minutes=5):
                return render(request, 'verify_otp.html', {'error': 'OTP expired'})

            if str(otp_obj.otp).strip() == entered_otp:

                user, _ = User.objects.get_or_create(mobile=mobile)
                request.session['user_id'] = user.id

                otp_obj.delete()
                return redirect('home')

        return render(request, 'verify_otp.html', {'error': 'Invalid OTP'})

    return render(request, 'verify_otp.html')


def logout_view(request):
    request.session.flush()
    return redirect('login')


# =========================
# PROFILE
# =========================
@login_required
def profile(request):
    user = get_user(request)
    return render(request, 'profile.html', {
        'user': user,
        'addresses': user.addresses.all()
    })


@login_required
def edit_profile(request):
    user = get_user(request)

    if request.method == "POST":
        user.name = request.POST.get('name')
        user.gender = request.POST.get('gender')
        user.age = request.POST.get('age')
        user.save()
        return redirect('profile')

    return render(request, 'edit_profile.html', {'user': user})


@login_required
def add_address(request):
    user = get_user(request)

    if request.method == "POST":
        Address.objects.create(
            user=user,
            full_name=request.POST.get('name'),
            phone=request.POST.get('phone'),
            house_no=request.POST.get('house'),
            area=request.POST.get('area'),
            city=request.POST.get('city'),
            state=request.POST.get('state'),
            pincode=request.POST.get('pincode'),
        )
        return redirect('profile')

    return render(request, 'add_address.html')


# =========================
# HELP / FAQ
# =========================
@login_required
def help(request):
    return render(request, 'helpcenter.html')


@login_required
def faq(request):
    return render(request, 'faq.html')


# =========================
# WISHLIST
# =========================
@login_required
def add_to_wishlist(request, pid):
    user = get_user(request)
    product = get_object_or_404(Product, id=pid)

    Wishlist.objects.get_or_create(user=user, product=product)
    return redirect('home')


@login_required
def wishlist(request):
    user = get_user(request)
    items = Wishlist.objects.filter(user=user)

    return render(request, 'wishlist.html', {
        'wishlist_items': items
    })


# =========================
# CART
# =========================
@login_required
def cart(request):
    user = get_user(request)
    items = Cart.objects.filter(user=user)

    total = sum(item.product.max_retail_price * item.quantity for item in items)

    return render(request, 'cart.html', {
        'items': items,
        'total': total
    })

@login_required
def add_to_cart(request, pid):
    user = get_user(request)
    product = get_object_or_404(Product, id=pid)

    cart_item, created = Cart.objects.get_or_create(
        user=user,
        product=product
    )

    if not created:
        cart_item.quantity += 1
        cart_item.save()

    return redirect('home')

@login_required
def increase_qty(request, cid):
    item = get_object_or_404(Cart, id=cid, user=get_user(request))
    item.quantity += 1
    item.save()
    return redirect('cart')


@login_required
def decrease_qty(request, cid):
    item = get_object_or_404(Cart, id=cid, user=get_user(request))

    if item.quantity > 1:
        item.quantity -= 1
        item.save()
    else:
        item.delete()

    return redirect('cart')


@login_required
def remove_cart(request, cid):
    item = get_object_or_404(Cart, id=cid, user=get_user(request))
    item.delete()
    return redirect('cart')


# =========================
# ORDER
# =========================


@login_required
def orders(request):
    user = get_user(request)
    items = Order.objects.filter(user=user)

    return render(request, 'orders.html', {
        'items': items
    })

@login_required
def remove_wishlist(request, wid):
    item = get_object_or_404(Wishlist, id=wid, user=get_user(request))
    item.delete()
    return redirect('wishlist')

@login_required
def move_to_cart(request, wid):
    user = get_user(request)
    item = get_object_or_404(Wishlist, id=wid, user=user)

    # add to cart
    cart_item, created = Cart.objects.get_or_create(
        user=user,
        product=item.product
    )

    if not created:
        cart_item.quantity += 1
        cart_item.save()

    # remove from wishlist
    item.delete()

    return redirect('wishlist')

@login_required
def place_order(request):
    if request.method == "POST":
        user = get_user(request)
        cart_items = Cart.objects.filter(user=user)

        if not cart_items:
            return redirect('cart')

        for item in cart_items:
            Order.objects.create(
                user=user,
                product=item.product,
                quantity=item.quantity
            )

        cart_items.delete()

    return redirect('orders')