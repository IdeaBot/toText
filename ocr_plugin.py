from libs import plugin
import discord
import requests
import pytesseract
try:
    from PIL import Image
except ImportError:
    import Image

COMPLETE_MSG = '''Hey {mention}, your text file is ready! '''
IMG_TMP_LOC = 'data/image2text-tmp'
TEXT_TMP_LOC = 'data/image2text-tmp'


class Plugin(plugin.ThreadedPlugin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, should_spawn_thread=False, **kwargs)
        self.public_namespace.ocr_q = plugin.Queue()
        self.threaded_kwargs = {"ocr_q":self.public_namespace.ocr_q}
        self.spawn_process()

    def threaded_action(self, q, ocr_q=plugin.Queue()):
        while not ocr_q.empty():
            item = ocr_q.get()
            discord_channel = discord.Object(id=item['channel'])
            mention = item['mention']
            img_url = item['img']
            language = item['lang']
            msg_content = COMPLETE_MSG.format(mention=mention)
            # download img
            resp = requests.get(img_url)
            with open(IMG_TMP_LOC, 'wb') as f:
                f.write(resp.content)
            # process img with ocr
            text = pytesseract.image_to_string(Image.open(IMG_TMP_LOC))
            # create attachment text file
            with open(TEXT_TMP_LOC, 'w') as f:
                f.write(text)
            q.put({self.SEND_FILE:{plugin.ARGS:[discord_channel, TEXT_TMP_LOC], plugin.KWARGS:{'filename':'text_from_img.txt', 'content':msg_content}}})
