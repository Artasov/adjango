# utils/pictures.py
try:
    from PIL import ExifTags

    class CorrectOrientation:
        @staticmethod
        def process(image):
            """
            Corrects image orientation based on EXIF data.

            :param image: PIL Image object
            :return: Corrected PIL Image object
            """
            # Get EXIF data
            exif = image.getexif()
            if exif:
                for tag, value in exif.items():
                    tag_name = ExifTags.TAGS.get(tag, tag)
                    if tag_name == 'Orientation':
                        orientation = value
                        break
                else:
                    orientation = None

                # Correct image orientation
                if orientation == 3:
                    image = image.rotate(180, expand=True)
                elif orientation == 6:
                    image = image.rotate(270, expand=True)
                elif orientation == 8:
                    image = image.rotate(90, expand=True)
            return image

except ImportError:
    # Pillow not installed
    pass
