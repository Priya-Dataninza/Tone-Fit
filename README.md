# ToneFit

A Django-based e-commerce and AI skin tone recommendation platform for personalized fashion shopping. The project blends product browsing, wishlist/cart flows, OTP-based authentication, and an AI-powered skin tone analyzer that suggests suitable color palettes for products.

## Overview

ToneFit helps shoppers discover products based on their skin tone and personal style. Users can:

- Create an account using mobile OTP login
- Browse products and search/filter items
- Analyze their skin tone using uploaded or captured images
- Receive recommended product colors based on detected skin tone
- Save products to wishlist and cart
- Place orders

## Tech Stack

- Python
- Django 6.0
- SQLite
- OpenCV
- NumPy
- Ultralytics YOLO
- Scikit-learn
- Twilio

## Project Flow

```mermaid
flowchart LR
    A[Landing Page] --> B[Login with Mobile Number]
    B --> C[Generate OTP]
    C --> D[Send OTP via Twilio]
    D --> E[Verify OTP]
    E --> F[Home Page]
    F --> G[AI Skin Tone Analyzer]
    G --> H[Detect Face & Skin Tone]
    H --> I[Recommend Colors]
    I --> J[Filter Products]
    J --> K[View Product Details]
    K --> L[Wishlist]
    K --> M[Add to Cart]
    M --> N[Place Order]
    L --> M
    N --> O[Order History]
```

## Complete User Journey

1. User lands on the login page.
2. User enters a mobile number.
3. The system generates a 6-digit OTP.
4. OTP is sent through Twilio SMS.
5. User verifies the OTP.
6. User is redirected to the home page.
7. User uploads or captures a face image.
8. The system detects the face using YOLO.
9. Skin tone is analyzed using HSV/LAB color logic.
10. Matching colors are recommended.
11. Products are filtered according to recommended color and category.
12. User adds items to wishlist/cart.
13. User places an order.

## Features

### Authentication
- OTP-based login using mobile number
- Session-based authenticated user flow
- Safe login checks with custom user retrieval helpers

### Product Experience
- Product search
- Category and price filtering
- Product detail pages
- Wishlist management
- Cart quantity management

### AI Recommendation Engine
- Face detection using YOLO
- Skin tone classification based on LAB/HSV analysis
- Color recommendations based on detected undertone and depth

### Order Workflow
- Add items to cart
- Increase/decrease quantities
- Remove items
- Place order
- View order history

## Folder Structure

```text
ToneFit/
├── home/
│   ├── templates/
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   └── tests.py
├── product/
│   ├── models.py
│   ├── views.py
│   └── urls.py
├── tonefit/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── media/
├── manage.py
├── db.sqlite3
├── README.md
├── requirements.txt
└── .gitignore
```

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/your-username/ToneFit.git
cd ToneFit
```

### 2. Create a virtual environment

```bash
python -m venv env
```

On Windows:

```bash
env\Scripts\activate
```

On macOS/Linux:

```bash
source env/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Apply migrations

```bash
python manage.py migrate
```

### 5. Start the development server

```bash
python manage.py runserver
```

Then open:

```text
http://127.0.0.1:8000/
```

## Configuration Notes

### Twilio OTP

SMS sending is configured in the Django settings file. To enable real OTP sending, set valid Twilio credentials:

- `TWILIO_ACCOUNT_SID`
- `TWILIO_AUTH_TOKEN`
- `TWILIO_PHONE_NUMBER`

If Twilio is not configured, the app may print the OTP in the console instead of sending an SMS.

### AI model

The app uses a local YOLO face model file stored in the app directory. Ensure the model file is present:

```text
home/yolov8n-face.pt
```

## Future Enhancements

- Add real product image recommendation matching
- Improve skin tone classification accuracy
- Add payment integration
- Add admin dashboard for inventory management
- Deploy on Render, Railway, or Azure

## License

This project is open for learning and portfolio use. Add your preferred license if you plan to publish it publicly.

## GitHub Showcase Summary

ToneFit is a complete AI-powered fashion recommendation app that combines e-commerce workflow with computer vision to create a personalized shopping experience.

It is a strong portfolio project because it demonstrates:

- Full-stack Django development
- AI/ML integration
- Mobile OTP authentication
- Product filtering and shopping cart logic
- Real-world ecommerce UX
- GitHub-ready project structure
