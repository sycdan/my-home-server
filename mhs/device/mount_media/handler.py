from mhs.storage import load_media


def handle():
  media = load_media.call(index=True)
  print(media)
