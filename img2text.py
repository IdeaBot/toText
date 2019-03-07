from libs import command
import re

VALID_IMG_EXTENSIONS = ['png', 'jpg', 'jpeg']

class Command(command.DirectOnlyCommand):
    '''Get the text from an image

**Usage**
Add an image to the text2img queue
```@Idea read this ```
Don't forget to attach/upload the image!
(Links won't work)

When your image has been processed, the result will be sent to the same channel.

Powered by tesseract, a powerful Optical Character Recognition system '''
    def matches(self, message):
        # print(message.attachments)
        return self.collect_args(message) is not None and get_image_from_attachments(message.attachments) is not None

    def collect_args(self, message):
        return re.search(r'(?:(?:ocr|read|text(?:-?ify))(?:/s+this)?|convert\s+this\s+to\s+text)', message.content, re.I)

    def action(self, message):
        queue_num = self.public_namespace.ocr_q.qsize() + 1
        to_q = {
                'mention':message.author.mention,
                'img':get_image_from_attachments(message.attachments),
                'channel':message.channel.id,
                'lang':'en'
                }
        self.public_namespace.ocr_q.put(to_q)
        yield from self.send_message(message.channel, 'You\'re number **%s** in the queue! You\'ll be pinged here when it\'s ready' % queue_num)

def get_image_from_attachments(attachments):
    for i in attachments:
        file_ending = i['filename'].split('.')[-1]
        if file_ending.lower() in VALID_IMG_EXTENSIONS:
            return i['url']
    return None
