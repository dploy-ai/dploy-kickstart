from PIL import Image
import io


# @dploy endpoint f1
# @dploy request_content_type image
def f1(raw_image):
    image = Image.open(io.BytesIO(raw_image))
    width, height = image.size
    # build a response dict to send back to client
    return {"message": "size={}x{}".format(width, height)}


# @dploy endpoint f2
# @dploy request_content_type image
def f2(raw_image):
    image = Image.open(io.BytesIO(raw_image))
    width, height = image.size
    # build a response dict to send back to client
    return {"message": "image received. size={}x{}".format(width, height)}


# @dploy endpoint f3
# @dploy request_content_type image
# @dploy response_mime_type image
def f3(raw_image):
    image = Image.open(io.BytesIO(raw_image))

    # create file-object in memory
    file_object = io.BytesIO()

    # write PNG in file-object keep quality as 100 and subsampling as 0
    # to save the image exactly same with the original format
    image.save(file_object, image.format, quality=100, subsampling=0)

    # move to beginning of file so `send_file()` it will read from start
    file_object.seek(0)
    return file_object


# @dploy endpoint f4
# @dploy request_content_type image
# @dploy response_mime_type image
def f4(raw_image):
    image = Image.open(io.BytesIO(raw_image))
    width, height = image.size
    # build a response dict to send back to client
    return {"message": "image received. size={}x{}".format(width, height)}


# @dploy endpoint f5
# @dploy request_content_type image
# @dploy response_mime_type image
def f5(raw_image):
    image = Image.open(io.BytesIO(raw_image))

    # create file-object in memory
    file_object = io.BytesIO()

    # write PNG in file-object keep quality as 100 and subsampling as 0
    # to save the image exactly same with the original format
    image.save(file_object, image.format, quality=100, subsampling=0)

    # move to beginning of file so `send_file()` it will read from start
    file_object.seek(0)
    return file_object.getvalue()


# @dploy endpoint f6
# @dploy request_content_type random
# @dploy response_mime_type random
def f6(raw_image):
    image = Image.open(io.BytesIO(raw_image))

    # create file-object in memory
    file_object = io.BytesIO()

    # write PNG in file-object keep quality as 100 and subsampling as 0
    # to save the image exactly same with the original format
    image.save(file_object, image.format, quality=100, subsampling=0)

    # move to beginning of file so `send_file()` it will read from start
    file_object.seek(0)
    return file_object.getvalue()