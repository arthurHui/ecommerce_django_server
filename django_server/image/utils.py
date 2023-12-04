import io
import sys
from PIL import Image
from django.core.files.uploadedfile import InMemoryUploadedFile

def reorient_image(im):
    try:
        image_exif = im._getexif()
        image_orientation = image_exif[274]
        if image_orientation in (2,'2'):
            return im.transpose(Image.FLIP_LEFT_RIGHT)
        elif image_orientation in (3,'3'):
            return im.transpose(Image.ROTATE_180)
        elif image_orientation in (4,'4'):
            return im.transpose(Image.FLIP_TOP_BOTTOM)
        elif image_orientation in (5,'5'):
            return im.transpose(Image.ROTATE_90).transpose(Image.FLIP_TOP_BOTTOM)
        elif image_orientation in (6,'6'):
            return im.transpose(Image.ROTATE_270)
        elif image_orientation in (7,'7'):
            return im.transpose(Image.ROTATE_270).transpose(Image.FLIP_TOP_BOTTOM)
        elif image_orientation in (8,'8'):
            return im.transpose(Image.ROTATE_90)
        else:
            return im
    except (KeyError, AttributeError, TypeError, IndexError):
        return im

def image_to_webp(image=None, image_type="!webp", quality=100, base_size=1024, is_resize=False, optimize=True, expected_size=None):
    try:
        if hasattr(image, 'name'):
            filename = str(image.name)
        else:
            filename = str(image.url)
        format = "webp"
        image = Image.open(image)
        image = reorient_image(image)
        if image.mode != "RGBA" and image_type.lower() != "webp":
            # print("{} convert to RGBA".format(image.mode))
            image = image.convert('RGBA')
        if is_resize:
            pw = image.width
            ph = image.height
            if pw >= ph:
                if pw <= base_size:
                    nw = pw
                else:
                    nw = base_size
                nh = int(round(float(ph) / float(pw) * float(nw)))
            else:
                if ph <= base_size:
                    nh = ph
                else:
                    nh = base_size
                nw = int(round(float(pw) / float(ph) * float(nh)))
            image = image.resize((nw, nh), Image.ANTIALIAS)
        output = io.BytesIO()
        image.save(output, format=format, quality=quality, optimize=optimize)
        size = output.tell()
        if expected_size is not None and size > expected_size:
            return (None, size, format,)
        image = InMemoryUploadedFile(output, 'ImageField', "%s.webp" % filename.split('.')[0],
                                     'image/webp', sys.getsizeof(output), None)
        return (image, size, format,)
    except Exception as e:
        print("image_to_webp", e)
        return (None, 0, "Webp error")

def image_resize(base_size, quality, image, format=None):
    pil_image = Image.open(image)
    pil_image = reorient_image(pil_image)
    pw = pil_image.width
    ph = pil_image.height
    if pw >= ph:
        if pw <= base_size:
            nw = pw
        else:
            nw = base_size
        nh = int(round(float(ph) / float(pw) * float(nw)))
    else:
        if ph <= base_size:
            nh = ph
        else:
            nh = base_size
        nw = int(round(float(pw) / float(ph) * float(nh)))

    originl_extension = image.name.split('.')[-1].lower()
    png_list = ['png']
    jpg_list = ['jpg', 'jpeg', 'jfif']

    if originl_extension in png_list:
        format = 'png'
        extension = 'png'
    elif originl_extension in jpg_list:
        format = 'jpeg'
        extension = 'jpg'
    else:
        raise Exception("invalid format %s" % image.name)
    resized_pil_image = pil_image.resize((nw, nh), Image.ANTIALIAS)
    save_opts = {'optimize': True, 'quality': quality, 'format': format}
    output = io.BytesIO()
    resized_pil_image.save(output, **save_opts)
    size = output.tell()
    image = InMemoryUploadedFile(output, 'ImageField', "%s.%s" % (image.name.split('.')[0], extension),
                                 'image/%s' % format, sys.getsizeof(output), None)
    return (image, size, format,)

def image_calculator(memory_image, base_size, type, is_webp):
    lowQuality = 00
    highQuality = 100
    if type == 'high':
        middleQuality = 100
        maxDeviation = 50
        maxSize = 350
        iteration = 0
        if is_webp:
            result_image, size, format = image_to_webp(base_size=base_size,
                                                    quality=middleQuality, image=memory_image)
            while (abs(size / 1024 - maxSize) > maxDeviation and iteration < 0):
                result_image, size, format = image_to_webp(base_size=base_size,
                                                        quality=middleQuality, image=memory_image)
                if size / 1024 < (maxSize - maxDeviation):
                    lowQuality = middleQuality
                elif size / 1024 > maxSize:
                    highQuality = middleQuality

                middleQuality = (lowQuality + highQuality) / 2
                iteration += 1
        else:
            result_image, size, format = image_resize(base_size=base_size,
                                                    quality=middleQuality, image=memory_image)
            while (abs(size / 1024 - maxSize) > maxDeviation and iteration < 0):
                result_image, size, format = image_resize(base_size=base_size,
                                                        quality=middleQuality, image=memory_image)
                if size / 1024 < (maxSize - maxDeviation):
                    lowQuality = middleQuality
                elif size / 1024 > maxSize:
                    highQuality = middleQuality

                middleQuality = (lowQuality + highQuality) / 2
                iteration += 1
        return result_image
    elif type == 'low':
        middleQuality = 70
        maxDeviation = 20
        maxSize = 120
        iteration = 0
        result_image, size, format = image_resize(base_size=base_size,
                                                  quality=middleQuality, image=memory_image)
        
        while (abs(size / 1024 - maxSize) > maxDeviation and iteration < 0):
            result_image, size, format = image_resize(base_size=base_size,
                                                    quality=middleQuality, image=memory_image)
            if size / 1024 < (maxSize - maxDeviation):
                lowQuality = middleQuality
            elif size / 1024 > maxSize:
                highQuality = middleQuality

            middleQuality = (lowQuality + highQuality) / 2
            iteration += 1

        return result_image