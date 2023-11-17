import json
import logging

import requests
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from main_app import mpesa

logger = logging.getLogger(__name__)


# Create your views here.
@csrf_exempt
def initiate_payment(request):
    if request.method == "POST":
        phone = request.POST['phone']
        amount = request.POST['amount']
        logger.info(f"{phone} {amount}")
        data = {
            "BusinessShortCode": mpesa.get_business_shortcode(),
            "Password": mpesa.generate_password(),
            "Timestamp": mpesa.get_current_timestamp(),
            "TransactionType": "CustomerPayBillOnline",
            "Amount": amount,
            "PartyA": phone,
            "PartyB": mpesa.get_business_shortcode(),
            "PhoneNumber": phone,
            "CallBackURL": mpesa.get_callback_url(),
            "AccountReference": "123456",
            "TransactionDesc": "Payment for Booking",
        }
        headers = mpesa.generate_request_headers()
        response = requests.post(mpesa.get_payment_url(), json=data, headers=headers)
        logger.info(response.json())
        json_response = response.json()
        if "ResponseCode" in json_response:
            code = json_response['ResponseCode']
            if code == 0:
                mid = json_response['MerchantRequestID']
                cid = json_response['CheckoutRequestID']
                logger.info(f"{mid} {cid}")
            else:
                logger.error(f"Error while initiating stk push {code}")
        elif "errorCode" in json_response:
            erroCode = json_response["errorCode"]
            logger.error(f"Error with the server")

        # print(phone,amount)
    return render(request, 'payment.html')


@csrf_exempt
def callback(request):
    result = json.load(request.body)
    logger.info(result)
    mid = result["Body"]["stkCallback"]["MerchantRequestID"]
    cid = result["Body"]["stkCallback"]["CheckoutRequestID"]
    code = result["Body"]["stkCallback"]["ResultCode"]
    logger.info(f"From callback Result {mid} {cid} {code}")
    return HttpResponse({"message": "Successfully received"})
