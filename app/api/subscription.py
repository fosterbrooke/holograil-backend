from datetime import datetime, timedelta
import os
from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import FileResponse
from app.models.license import License
from app.schemas.user import UserInDB
from app.crud.user import get_user_by_email
from app.crud.license import check_and_update_device_address, create_license, get_available_licenses
from app.config import settings
import stripe

from app.utils.license import generate_license_key

stripe.api_key = settings.STRIPE_API_KEY

router = APIRouter()

@router.post("/create-checkout-session")
async def create_checkout_session(user_mail: str, plan_id: str):
    user = await get_user_by_email(user_mail)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            customer_email=user.email,
            line_items=[{
                'price': plan_id,
                'quantity': 1,
            }],
            mode='subscription',
            success_url='https://thegrail.app/accounts/overview',
            cancel_url='https://thegrail.app/accounts/overview',
        )
        return session
    except stripe.error.StripeError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/retrieve-subscription")
async def retrieve_subscription(subscription_id: str):
    try:
        subscription = stripe.Subscription.retrieve(subscription_id)
        return subscription
    except stripe.error.StripeError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/cancel-subscription")
async def cancel_subscription(subscription_id: str):
    try:
        subscription = stripe.Subscription.delete(subscription_id)
        return subscription
    except stripe.error.StripeError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/webhook")
async def stripe_webhook(request: Request):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError as e:
        raise HTTPException(status_code=400, detail="Invalid signature")

    if event["type"] == "charge.succeeded":
        charge = event["data"]["object"]

        customer_email = charge.get("billing_details", {}).get("email")
        invoice_id = charge.get("invoice")  # Get the invoice ID directly

        if invoice_id:
            invoice = stripe.Invoice.retrieve(invoice_id)  # Retrieve the invoice object
            subscription_id = invoice.get("subscription")  # Now get the subscription ID from the invoice

            if subscription_id:
                subscription = stripe.Subscription.retrieve(subscription_id)
                duration = subscription.get("items", {}).get("data", [{}])[0].get("plan", {}).get("interval_count")
                interval = subscription.get("items", {}).get("data", [{}])[0].get("plan", {}).get("interval")

                if interval == "month":
                    duration_days = duration * 30
                elif interval == "year":
                    duration_days = duration * 365
                else:
                    duration_days = duration

                user = await get_user_by_email(customer_email)
                if user:
                    license_key = generate_license_key(user.dict(), timedelta(days=duration_days))

                    license_data = License(
                        user_id=user.id,
                        license_key=license_key,
                        expire_date=(datetime.utcnow() + timedelta(days=duration_days)).isoformat(),
                        device_number=None
                    )
                    await create_license(license_data)

        print(f"Charge succeeded: {charge}")
    elif event["type"] == "charge.failed":
        charge = event["data"]["object"]
        print(f"Charge failed: {charge}")

    return {"status": "success"}

@router.get("/available-licenses")
async def get_user_available_licenses(user_email: str):
    user = await get_user_by_email(user_email)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    licenses = await get_available_licenses(str(user.id))
    return licenses

@router.post("/validate-license")
async def validate_license(license_key: str, device_address: str):
    result = await check_and_update_device_address(license_key, device_address)
    return result

@router.get("/download-guidebook")
async def download_pdf():
    book_file_path = "./download/guidebook.pdf"
    if not os.path.exists(book_file_path):
        raise HTTPException(status_code=404, detail="Guidebook was not found")
    
    return FileResponse(book_file_path, media_type='application/octet-stream', filename="guidebook.pdf")

@router.get("/download-app")
async def download_app():
    app_file_path = "./download/holograil.zip"
    if not os.path.exists(app_file_path):
        raise HTTPException(status_code=404, detail="App file was not found")
    
    return FileResponse(app_file_path, media_type='application/octet-stream', filename="holograil.zip")