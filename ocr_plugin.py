from libs import plugin
import discord
import requests
import pytesseract
try:
    from PIL import Image
except ImportError:
    import Image
import os

COMPLETE_MSG = '''Hey {mention}, your text file is ready! '''
DATA_LOC = 'data/toText'
IMG_TMP_LOC = os.path.join(DATA_LOC, 'image2text-tmp')
TEXT_TMP_LOC_START = os.path.join(DATA_LOC, 'image2text-tmp')

if not os.path.isdir(DATA_LOC):
    os.mkdir(DATA_LOC)


class Plugin(plugin.ThreadedPlugin):
    ''' Tesseract OCR image reader

For more information:
```@Idea help img2text``` '''
    def __init__(self, *args, **kwargs):
        super().__init__(*args, should_spawn_thread=False, **kwargs)
        self.public_namespace.ocr_q = plugin.Queue()
        self.text_tmp_index = 0
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
            try:
                text = pytesseract.image_to_string(Image.open(IMG_TMP_LOC))
            except pytesseract.pytesseract.TesseractNotFoundError as e:
                text = 'Text to Image conversion failed.\nError: `%s`' % e
                success = False
            else:
                success = True

            if success:
                txt_filename = TEXT_TMP_LOC_START+str(self.text_tmp_index)
                # create attachment text file
                with open(txt_filename, 'w') as f:
                    f.write(text)
                q.put({self.SEND_FILE:{plugin.ARGS:[discord_channel, txt_filename], plugin.KWARGS:{'filename':'text_from_img.txt', 'content':msg_content}}})
                self.text_tmp_index += 1
            else:
                q.put({self.SEND_MESSAGE:{plugin.ARGS:[discord_channel], plugin.KWARGS:{'content':text}}})
