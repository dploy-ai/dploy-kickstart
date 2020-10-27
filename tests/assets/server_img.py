from PIL import Image
import io


# @dploy endpoint f1
# @dploy request_content_type image/jpeg
def f1(raw_image):
    image = Image.open(io.BytesIO(raw_image))
    width, height = image.size
    # build a response dict to send back to client
    return {'message': 'size={}x{}'.format(width, height)}


# @dploy endpoint f2
# @dploy request_content_type image/png
def f2(raw_image):
    image = Image.open(io.BytesIO(raw_image))
    width, height = image.size
    # build a response dict to send back to client
    return {'message': 'image received. size={}x{}'.format(width, height)}


# @dploy endpoint f3
# @dploy request_content_type image/jpeg
# @dploy response_mime_type image/jpeg
def f3(raw_image):
    return raw_image


# @dploy endpoint f4
# @dploy request_content_type image/png
# @dploy response_mime_type image/png
def f4(raw_image):
    return raw_image

