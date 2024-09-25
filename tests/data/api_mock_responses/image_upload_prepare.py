image_upload_prepare_regular_success_response = {
    "success": True,
    "imageId": "e10f9911-49a8-4e6f-b206-55c0bab81a68",
    "url": "https://incoming-online-dehancer-com.s3-accelerate.dualstack.amazonaws.com/e10f9911-49a8-4e6f-b206-55c0bab81a68"
           "?X-Amz-Algorithm=AWS4-HMAC-SHA256"
           "&X-Amz-Content-Sha256=UNSIGNED-PAYLOAD"
           "&X-Amz-Credential=AKIA1EXAMPLE22XYZ1234%2F20240527%2Fus-west-2%2Fs3%2Faws4_request"
           "&X-Amz-Date=20240101T000000Z"
           "&X-Amz-Expires=3600"
           "&X-Amz-Signature=d3e5a712c4f3b6a9d0f8e4b3a1c2d9e7b5f4c2a1b6e7d8c3f0a1b2c4e5d3f6a1"
           "&X-Amz-SignedHeaders=host"
           "&x-id=PutObject",
}

image_upload_prepare_multipart_success_response = {
    "success": True,
    "imageId": "e10f9911-49a8-4e6f-b206-55c0bab81a69",
    "isMultipart": True,
    "chunkSize": 7472577,
    "uploadId": "Qb12lMtLYuPyZ7xV9NkJh8X4.yZWPwFiw2EiHqv7cUJkY3B5sRzS0JmJ.IXPwBVvXfGHcMnA4bTZaLrfMskVhB_GmOuXYXpqUslfFrk9sh8TzRjAmEXJtV7gXn",  # noqa: E501
    "urls": [
        "https://incoming-online-dehancer-com.s3-accelerate.dualstack.amazonaws.com/e10f9911-49a8-4e6f-b206-55c0bab81a69"
        "?X-Amz-Algorithm=AWS4-HMAC-SHA256"
        "&X-Amz-Content-Sha256=UNSIGNED-PAYLOAD"
        "&X-Amz-Credential=AKIA5FTZE22JCLHW6PQL%2F20240923%2Fus-east-1%2Fs3%2Faws4_request"
        "&X-Amz-Date=20240101T000000Z"
        "&X-Amz-Expires=3600"
        "&X-Amz-Signature=d3e5a712c4f3b6a9d0f8e4b3a1c2d9e7b5f4c2a1b6e7d8c3f0a1b2c4e5d3f6a1"
        "&X-Amz-SignedHeaders=host"
        "&partNumber=1"
        "&uploadId=Qb12lMtLYuPyZ7xV9NkJh8X4.yZWPwFiw2EiHqv7cUJkY3B5sRzS0JmJ.IXPwBVvXfGHcMnA4bTZaLrfMskVhB_GmOuXYXpqUslfFrk9sh8TzRjAmEXJtV7gXn"
        "&x-id=UploadPart",
        "https://incoming-online-dehancer-com.s3-accelerate.dualstack.amazonaws.com/e10f9911-49a8-4e6f-b206-55c0bab81a69"
        "?X-Amz-Algorithm=AWS4-HMAC-SHA256"
        "&X-Amz-Content-Sha256=UNSIGNED-PAYLOAD"
        "&X-Amz-Credential=AKIA5FTZE22JCLHW6PQL%2F20240923%2Fus-east-1%2Fs3%2Faws4_request"
        "&X-Amz-Date=20240101T000000Z"
        "&X-Amz-Expires=3600"
        "&X-Amz-Signature=d3e5a712c4f3b6a9d0f8e4b3a1c2d9e7b5f4c2a1b6e7d8c3f0a1b2c4e5d3f6a1"
        "&X-Amz-SignedHeaders=host"
        "&partNumber=2"
        "&uploadId=Qb12lMtLYuPyZ7xV9NkJh8X4.yZWPwFiw2EiHqv7cUJkY3B5sRzS0JmJ.IXPwBVvXfGHcMnA4bTZaLrfMskVhB_GmOuXYXpqUslfFrk9sh8TzRjAmEXJtV7gXn"
        "&x-id=UploadPart",
    ],
}

image_upload_prepare_not_success_response = {
    "success": False,
}

image_upload_prepare_invalid_response = "Error"

