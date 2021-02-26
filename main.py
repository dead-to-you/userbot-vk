import ujson
import time
import requests
import os.path
from vkbottle.user import User, Message
from vkbottle.api.uploader.photo import PhotoUploader
from vkbottle.api.uploader.doc import DocUploader
from vkbottle.rule import FromMe
from PIL import Image
import threading
import random


user = User("")  # токен юзера от VK Admin с полными провами (vkhost.github.io)
owner_id = user.user_id

photo_uploader = PhotoUploader(user.api, generate_attachment_strings=True)
doc_uploader = DocUploader(user.api, generate_attachment_strings=True)

def editData(id_name, newData):
    try:
        file = open('data.json', 'r')
        try:
            data = ujson.loads(file.readline())
        except:
            data = {}
        data[id_name] = newData

        file.close()
        file = open('data.json', 'w')

        file.writelines(ujson.dumps(data))
        file.close()

        return True
    except:
        return False


def getData(id_name):
    try:
        file = open('data.json')
        data = ujson.loads(file.readline())

        return data[str(id_name)]
    except:
        return None

async def DelCommandForAll(ans: Message, args):
    if(ans.reply_message != None):
        if(ans.reply_message.from_id != user.user_id):
            await user.api.messages.send(
                peer_id=ans.peer_id,
                random_id=0,
                message="Это не моё сообщение, дурик 👈🏻",
                reply_to=ans.id
            )
            return
        times = int(time.time()) - ans.date
        if (times > 86400):
            await user.api.messages.send(
                peer_id=ans.peer_id,
                random_id=0,
                message="Это уже старое сообщение, его нельзя удалить",
                reply_to=ans.id
            )
            return

        await user.api.messages.delete(
            message_ids=[ans.reply_message.id],
            delete_for_all=True
        )
        return

    if (len(args) < 2):
        await user.api.messages.send(
            peer_id=ans.peer_id,
            random_id=0,
            message="А кто количество сообщениий введет? 🥴",
            reply_to=ans.id
        )

        time.sleep(3)

        await user.api.messages.delete(
            message_ids=ans.id,
            delete_for_all= None if ans.peer_id == user.user_id else True
        )
        return

    messages = await user.api.messages.get_history(
        count=200,
        peer_id=ans.peer_id,
        start_message_id=ans.id
    )

    messages = messages.items
    deleted = 0
    sum = int(args[1])
    list_messages = []
    for message in messages:
        if (deleted >= sum):
            break

        times = int(time.time()) - message.date
        if (times > 86400):
            break

        if (message.from_id == user.user_id):
            list_messages.append(message.id)
            deleted += 1

    await user.api.messages.delete(
        message_ids=list_messages,
        delete_for_all=True
    )
    return

async def DelCommand(ans: Message, args):
    for_all = None if ans.from_id == ans.peer_id else True

    if(len(args) < 2):
        await user.api.messages.edit(
            peer_id=ans.peer_id,
            message_id=ans.id,
            message="А кто количество сообщениий введет? 🥴"
        )
        return;

    await user.api.messages.delete(message_ids=[ans.id], delete_for_all=for_all)
    messages = await user.api.messages.get_history(
        count=200,
        peer_id=ans.peer_id,
        start_message_id=ans.id
    )

    messages = messages.items
    deleted = 0
    sum = int(args[1])
    list_messages = []

    for message in messages:
        if (deleted >= sum):
            break

        times = int(time.time()) - message.date
        if (times > 86400):
            break

        if (message.from_id == user.user_id):
            try:
                if(len(args) >= 3):
                    await user.api.messages.edit(
                        peer_id=message.peer_id,
                        message_id=message.id,
                        message="&#13;"
                    )
            except Exception as e:
                print(e)

            list_messages.append(message.id)
            deleted += 1

    await user.api.messages.delete(message_ids=list_messages, delete_for_all=for_all)
    return

async def Copy(ans: Message, args):
    for_all = None if ans.from_id == ans.peer_id else True

    if (ans.reply_message == None):
        await user.api.messages.edit(
            peer_id=ans.peer_id,
            message_id=ans.message_id,
            message="Так-то на сообщение ответить надо дурень 🥳"
        )
        return


    await user.api.messages.delete(message_ids=[ans.id], delete_for_all=for_all)
    reply = ans.reply_message
    if(reply.attachments[0]['audio_message'] != None):
        gc=reply.attachments[0]['audio_message']
        await user.api.messages.send(peer_id=ans.peer_id, random_id=0, attachment="doc"+str(gc['owner_id'])+"_"+str(gc['id'])+"_"+str(gc['access_key']))
    elif(reply.attachments[0]['sticker'] != None):
        sticker=reply.attachments[0]['sticker']
        await user.api.messages.send(peer_id=ans.peer_id, random_id=0, sticker_id=sticker['sticker_id'])
    return

async def CopyForAll(ans: Message, args):
    if (ans.reply_message == None):
        await user.api.messages.send(
            peer_id=ans.peer_id,
            message="Так-то на сообщение ответить надо дурень 🥳",
            random_id=0
        )
        return

    reply = ans.reply_message
    if(len(reply.attachments) == 0):
        await user.api.messages.send(
            peer_id=ans.peer_id,
            message="Надо сообщение с гс или стикером....",
            random_id=0
        )
        return

    if(reply.attachments[0]['audio_message'] != None):
        gc=reply.attachments[0]['audio_message']
        await user.api.messages.send(reply_to=ans.id, peer_id=ans.peer_id, random_id=0, attachment="doc"+str(gc['owner_id'])+"_"+str(gc['id'])+"_"+str(gc['access_key']))
    elif(reply.attachments[0]['sticker'] != None):
        sticker=reply.attachments[0]['sticker']
        await user.api.messages.send(reply_to=ans.id, peer_id=ans.peer_id, random_id=0, sticker_id=sticker['sticker_id'])
    else:
        await user.api.messages.send(
            peer_id=ans.peer_id,
            message="Надо сообщение с гс или стикером....",
            random_id=0
        )
        return


async def AudioMsgChange(ans: Message, args):
    if (ans.peer_id == user.user_id): for_all = None
    else: for_all = True

    reply = ans.reply_message
    if(reply == None):
        await user.api.messages.send(
            peer_id=ans.peer_id,
            random_id=0,
            message="Мне кажется ты пытаешься меня обмануть: необходимо ответить на сообщение с гс",
            reply_to=ans.message_id
        )
        return

    if(len(reply.attachments) < 1):
        await user.api.messages.send(
            peer_id=ans.peer_id,
            random_id=0,
            message="Мне кажется ты пытаешься меня обмануть: необходимо ответить на сообщение с гс",
            reply_to=ans.message_id
        )
        return

    if(reply.attachments[0]['audio_message'] == None):
        await user.api.messages.send(
            peer_id=ans.peer_id,
            random_id=0,
            message="Мне кажется ты пытаешься меня обмануть: необходимо ответить на сообщение с гс",
            reply_to=ans.message_id
        )
        return

    audio = reply.attachments[0]['audio_message']['link_ogg']
    filename = "files/" + os.path.basename(audio).split('?')[0]
    r = requests.get(audio)
    with open(filename, 'wb') as f:
        f.write(r.content)

    if(os.path.isfile('files/render1.ogg')): os.remove('files/render1.ogg')
    if(os.path.isfile('files/render2.ogg')): os.remove('files/render2.ogg')

    if(len(args) >= 2):
        if(args[1] == "1"):
            cmd = f'ffmpeg -i {filename} -af "chorus=0.5:0.9:50|60|40:0.4|0.32|0.3:0.25|0.4|0.3:2|2.3|1.3" files/render1.ogg'
            os.system(cmd)

            cmd = f'ffmpeg -i files/render1.ogg -filter_complex "vibrato=f=15" files/render2.ogg'
            os.system(cmd)
        elif(args[1] == "2"):
            cmd = f'ffmpeg -i {filename} -af "chorus=0.5:0.9:50|60|40:0.4|0.32|0.3:0.25|0.4|0.3:2|2.3|1.3" files/render1.ogg'
            os.system(cmd)

            cmd = f'ffmpeg -i files/render1.ogg -filter_complex "vibrato=f=35" files/render2.ogg'
            os.system(cmd)
        elif(args[1] == "3"):
            cmd = f'ffmpeg -i {filename} -af "chorus=0.5:0.9:50|60|40:0.4|0.32|0.3:0.25|0.4|0.3:2|2.3|1.3" files/render1.ogg'
            os.system(cmd)

            cmd = f'ffmpeg -i files/render1.ogg -filter_complex "vibrato=f=10" files/render2.ogg'
            os.system(cmd)
        elif(args[1] == "4"):
            cmd = f"ffmpeg -i {filename} -filter_complex \"afftfilt=real='hypot(re,im)*sin(0)':imag='hypot(re,im)*cos(0)':win_size=512:overlap=0.75\" files/render2.ogg"
            os.system(cmd)
        else:
            await user.api.messages.send(
                peer_id=ans.peer_id,
                random_id=0,
                message="Использование команды: /audio [1-4]<br>1 - стандартный жмых<br>2 - сильный жмых<br>3 - слабый жмых<br>4 - робот",
                reply_to=ans.message_id
            )
            os.remove(filename)
            return
    else:
        await user.api.messages.send(
            peer_id=ans.peer_id,
            random_id=0,
            message="Использование команды: /audio [1-4]<br>1 - стандартный жмых<br>2 - сильный жмых<br>3 - слабый жмых<br>4 - робот",
            reply_to=ans.message_id
        )
        os.remove(filename)
        return

    uploaded = await doc_uploader.upload_doc_to_message(pathlike="files/render2.ogg", peer_id=ans.peer_id, doc_type="audio_message")
    await user.api.messages.send(
        peer_id=ans.peer_id,
        random_id=0,
        message="OK ⚡️",
        attachment=uploaded,
        reply_to=ans.message_id
    )

    os.remove(filename)
    if(os.path.isfile('files/render1.ogg')): os.remove('files/render1.ogg')
    os.remove('files/render2.ogg')
    return

async def Dist(ans: Message, args):
    for_all = None if ans.from_id == ans.peer_id else True

    attach = ans.attachments
    reply = ans.reply_message
    if(len(attach) == 0 and reply == None):
        await user.api.messages.send(
            peer_id=ans.peer_id,
            random_id=0,
            message="Мне кажется ты пытаешься меня обмануть: необходимо прикрепить фотографию или ответить на сообщение со стикером",
            reply_to=ans.message_id
        )
        return

    sticker_link = None
    try:
        if (reply != None):
            type = reply.attachments[0]['type']
            if(reply.attachments[0]['sticker'] != None):
                sticker_link = f"https://vk.com/sticker/3-{reply.attachments[0]['sticker']['sticker_id']}-0.json";
                r = requests.get(sticker_link)
                if(r.status_code == 200):
                    await user.api.messages.send(
                        peer_id=ans.peer_id,
                        random_id=0,
                        message="Анимированные стикеры временно не поддерживаются... Сорри 😔",
                        reply_to=ans.message_id
                    )
                    return
                else:
                    img = reply.attachments[0]['sticker']['images'].pop()['url']
                    sticker_link = None;
            elif(reply.attachments[0]['photo'] != None):
                img = reply.attachments[0]['photo']['sizes'].pop()['url']
            else: raise Exception()
        else:
            type = 'photo'
            img = attach[0]['photo']['sizes'].pop()['url']
    except:
        await user.api.messages.send(
            peer_id=ans.peer_id,
            random_id=0,
            message="Мне кажется ты пытаешься меня обмануть: необходимо прикрепить фотографию или ответить на сообщение со стикером",
            reply_to=ans.message_id
        )
        return

    filename = "files/" + os.path.basename(img).split('?')[0]
    if(len(filename.split('.')) < 2): filename += ".png"

    r = requests.get(img)
    with open(filename, 'wb') as f:
        f.write(r.content)

    new_msg = None
    if(sticker_link != None):
        new_msg = await user.api.messages.send(
            peer_id=ans.peer_id,
            random_id=0,
            message="Рендерим анимацию😇️",
            reply_to=ans.message_id
        )
        cmd = f"lottie_convert.py {filename} files/gif_sticker.gif --frame 30"
        os.system(cmd)
        os.remove(filename)
        filename = "files/gif_sticker.gif"

    if(len(args) >= 2):
        if(sticker_link != None): size = '85x85%'
        elif (args[1] == "1" or args[1] == None): size = '50x50%'
        elif (args[1] == "2"): size = '45x45%'
        elif (args[1] == "3"): size = '40x40%'
        elif (args[1] == "4"): size = '35x35%'
        elif (args[1] == "5"): size = '30x30%'
        else:
            await user.api.messages.send(
                peer_id=ans.peer_id,
                random_id=0,
                message="Правильное использование: /d [/dister] [степень от 1 до 5]",
                reply_to=ans.message_id
            )
            return
    else:
        size = '50x50%'

    im = Image.open(filename)
    width, height = im.size
    cmd = f"convert {filename} -liquid-rescale {size}! -resize {width}x{height}\! {filename}"
    os.system(cmd)

    if (new_msg != None):
        await user.api.messages.delete(
            message_ids=[new_msg],
            delete_for_all=for_all
        )

    if(type == "sticker"):
        if(sticker_link == None): uploaded = await doc_uploader.upload_doc_to_message(pathlike=filename, peer_id=ans.peer_id, doc_type="graffiti")
        else: uploaded = await doc_uploader.upload_doc_to_message(pathlike=filename, peer_id=ans.peer_id)
    else:
        uploaded = await photo_uploader.upload_message_photo(filename)

    os.remove(filename)
    await user.api.messages.send(
        peer_id=ans.peer_id,
        random_id=0,
        message="OK ⚡️",
        attachment=uploaded,
        reply_to=ans.message_id
    )
    return

async def InvisibleMessage(ans: Message, args):
    for_all = None if ans.from_id == ans.peer_id else True

    if(len(args) < 2 and len(ans.attachments) == 0 and len(ans.reply_message.attachments) == 0):
        await user.api.messages.edit(
            peer_id=ans.peer_id,
            message_id=ans.message_id,
            message="Необходимо сообщение..."
        )
        time.sleep(1)
        await user.api.messages.delete(
            message_ids=[ans.message_id],
            delete_for_all=for_all
        )
        return

    await user.api.messages.edit(
        peer_id=ans.peer_id,
        message_id=ans.message_id,
        message="сообщение исчезло 😅"
    )
    await user.api.messages.delete(
        message_ids=[ans.message_id],
        delete_for_all=for_all
    )

    expire_ttl = 86400
    try:
        last_n = args[1][-1]
        num = int(args[1][0:-1])
        text = ans.text.split(' ', 1)[1]

        if(last_n in [ 's', 'с' ] and num < 86400):
            text = ans.text.split(' ', 2)[2]
            expire_ttl = num
        elif(last_n in [ 'm', 'м' ] and (num*60) < 86400):
            text = ans.text.split(' ', 2)[2]
            expire_ttl = num*60
        elif(last_n in [ 'h', 'ч' ] and (num*60*60) < 86400):
            text = ans.text.split(' ', 2)[2]
            expire_ttl = num*60*60
    except:
        expire_ttl = 86400
        text = ans.text.split(' ', 1)[1]

    attachments = []
    for att in ans.attachments:
        att_type = att[att['type']]
        attachment = (f"{att['type']}{att_type['owner_id'] if att_type['owner_id'] else att_type['from_id']}_{att_type['id']}")
        attachments.append(attachment)
    attachments = ",".join(attachments)

    reply = None
    fwd_messages = None

    if(ans.reply_message != None):
        reply = ans.reply_message.id
        if(len(ans.reply_message.attachments) > 0 and ans.reply_message.from_id == user.user_id):
            type = ans.reply_message.attachments[0]['type']
            if(type == 'audio_message'):
                obj = ans.reply_message.attachments[0][type]
                await user.api.messages.delete(message_ids=ans.reply_message.id, delete_for_all=for_all)
                await user.api.messages.send(
                    peer_id=ans.reply_message.peer_id,
                    random_id=0,
                    expire_ttl=expire_ttl,
                    attachment=f"audio_message{obj['owner_id']}_{obj['id']}_{obj['access_key']}"
                )
                return
            elif(type == 'sticker'):
                obj = ans.reply_message.attachments[0][type]
                await user.api.messages.delete(message_ids=ans.reply_message.id, delete_for_all=for_all)
                await user.api.messages.send(
                    peer_id=ans.reply_message.peer_id,
                    random_id=0,
                    expire_ttl=expire_ttl,
                    sticker_id=f"{obj['sticker_id']}"
                )
                return
    elif(ans.fwd_messages != None):
        fwd_messages = ""
        for fwd_msg in ans.fwd_messages:
            fwd_messages += str(fwd_msg.id) + ","
        fwd_messages = fwd_messages[0:-1]

    if(text == None):
        mid = await user.api.messages.send(
            peer_id=ans.peer_id,
            random_id=0,
            message="Необходимо сообщение..."
        )
        time.sleep(1)
        await user.api.messages.delete(
            message_ids=[mid],
            delete_for_all=for_all
        )
        return

    await user.api.messages.send(
        peer_id=ans.peer_id,
        random_id=0,
        message=text,
        attachment=attachments,
        expire_ttl=expire_ttl,
        reply_to=reply,
        forward_messages=fwd_messages
    )
    return

async def TestersCheck(ans: Message, args):
    if(ans.reply_message != None):
        user_id = ans.reply_message.from_id
    else:
        user_id = args[1]


    try:
        target = await user.api.users.get(user_ids=user_id)
        target = target.pop()
    except:
        await user.api.messages.send(
            random_id=0,
            peer_id=ans.peer_id,
            message="Необходимо переслать сообщение или написать ID пользователя...",
            reply_to=ans.message_id
        )
        return


    tester_bool = await user.api.groups.is_member(group_id=134304772, user_id=target.id)

    if not(tester_bool):
        await user.api.messages.send(
            peer_id=ans.peer_id,
            random_id=0,
            message="[id"+str(target.id)+"|" +  str(target.first_name) + " " + str(target.last_name) + "] не тестировщик из [testpool|/testpool].",
            reply_to=ans.message_id,
            disable_mentions=True
        )
    else:
        await user.api.messages.send(
            peer_id=ans.peer_id,
            random_id=0,
            message="[id"+str(target.id)+"|" +  str(target.first_name) + " " + str(target.last_name) + "] тестировщик из [testpool|/testpool].<br>&#13;<br>https://vk.com/bugs?act=reporter&id="+str(target.id),
            reply_to=ans.message_id,
            disable_mentions=True
        )

    return

async def RepeatMessageAll(ans: Message, args):
    if(len(args) < 2):
        await user.api.messages.send(
            peer_id=ans.peer_id,
            random_id=0,
            message="Использование: /repeat [количество]<br>P.S. надо отвеить на сообщение....",
            reply_to=ans.message_id
        )
        return

    try:
        sumRepeat = int(args[1])
        if (sumRepeat < 0 or sumRepeat > 20):
            await user.api.messages.send(
                peer_id=ans.peer_id,
                random_id=0,
                message="Использование: /repeat [количество 1-20]<br>P.S. надо отвеить на сообщение....",
                reply_to=ans.message_id
            )
            return
    except:
        await user.api.messages.send(
            peer_id=ans.peer_id,
            random_id=0,
            message="Использование: /repeat [количество 1-20]<br>P.S. надо отвеить на сообщение....",
            reply_to=ans.message_id
        )
        return

    reply = ans.reply_message;
    if(reply == None):
        await user.api.messages.send(
            peer_id=ans.peer_id,
            random_id=0,
            message="Использование: /repeat [количество]<br>P.S. надо отвеить на сообщение....",
            reply_to=ans.message_id
        )
        return


    text = reply.text
    if(text == None):
        await user.api.messages.send(
            peer_id=ans.peer_id,
            random_id=0,
            message="В этом сообщении нет текста...",
            reply_to=ans.message_id
        )
        return

    for x in range(sumRepeat):
        try:
            await user.api.messages.send(
                peer_id=ans.peer_id,
                random_id=0,
                message=text
            )
        except:
            break;
        time.sleep(random.randrange(0,5))
    return

async def RepeatMessage(ans: Message, args):
    for_all = None if ans.from_id == ans.peer_id else True

    if(len(args) < 3):
        await user.api.messages.edit(
            peer_id=ans.peer_id,
            message_id=ans.message_id,
            message="Использование: /repeat [количество] [сообщение]"
        )
        time.sleep(1)
        await user.api.messages.delete(
            message_ids=[ans.message_id],
            delete_for_all=for_all
        )
        return

    await user.api.messages.delete(
        message_ids=[ans.message_id],
        delete_for_all=for_all
    );

    try:
        sumRepeat = int(args[1])
        if (sumRepeat < 0 or sumRepeat > 20):
            await user.api.messages.edit(
                peer_id=ans.peer_id,
                message_id=ans.message_id,
                message="Использование: /repeat [количество 1-20] [сообщение]"
            )
            time.sleep(1)
            await user.api.messages.delete(
                message_ids=[ans.message_id],
                delete_for_all=for_all
            )
            return
    except:
        await user.api.messages.edit(
            peer_id=ans.peer_id,
            message_id=ans.message_id,
            message="Использование: /repeat [количество 1-20] [сообщение]"
        )
        time.sleep(1)
        await user.api.messages.delete(
            message_ids=[ans.message_id],
            delete_for_all=for_all
        )
        return

    text = ans.text.split(' ', 2)[2]
    for x in range(sumRepeat):
        try:
            await user.api.messages.send(
                peer_id=ans.peer_id,
                random_id=0,
                message=text
            )
        except:
            break;
        time.sleep(random.randrange(0,5))
    return

async def MusicAudio(ans: Message, args):
    attach = ans.attachments
    reply = ans.reply_message
    if(len(attach) == 0 and reply == None):
        await user.api.messages.send(
            peer_id=ans.peer_id,
            random_id=0,
            message="Мне кажется ты пытаешься меня обмануть: необходимо прикрепить аудиозапись или ответить на сообщение с аудиозаписью",
            reply_to=ans.message_id
        )
        return

    try:
        if (reply != None):
            type = reply.attachments[0]['type']
            if(reply.attachments[0]['audio'] != None):
                audio = reply.attachments[0]['audio']['url']
            else: raise Exception()
        else:
            audio = attach[0]['audio']['url']
    except:
        await user.api.messages.send(
            peer_id=ans.peer_id,
            random_id=0,
            message="Мне кажется ты пытаешься меня обмануть: необходимо прикрепить аудиозапись или ответить на сообщение с аудиозаписью",
            reply_to=ans.message_id
        )
        return

    filename = "files/" + os.path.basename(audio).split('?')[0]
    if (len(filename.split('.')) < 2): filename += ".mp3"

    r = requests.get(audio)
    with open(filename, 'wb') as f:
        f.write(r.content)

    if(os.path.isfile('files/new_audio.wav')): os.remove('files/new_audio.wav')

    cmd = f"ffmpeg -i {filename} -acodec pcm_s16le -ac 1 -ar 16000 files/new_audio.wav"
    os.system(cmd)

    uploaded = await doc_uploader.upload_doc_to_message(
        pathlike="files/new_audio.wav",
        peer_id=ans.peer_id,
        doc_type="audio_message"
    )

    os.remove(filename)
    os.remove("files/new_audio.wav")

    await user.api.messages.send(
        peer_id=ans.peer_id,
        random_id=0,
        message="OK ⚡️",
        attachment=uploaded,
        reply_to=ans.message_id
    )
    return

async def BanUser(ans: Message, args):
    for_all = None if ans.from_id == ans.peer_id else True

    if(ans.reply_message is not None):
        target = await user.api.users.get(
            user_ids=ans.reply_message.from_id
        )
    else:
        try:
            target = await user.api.users.get(
                user_ids=args[1]
            )
        except:
            await user.api.messages.edit(
                peer_id=ans.peer_id,
                message_id=ans.id,
                message="⚡️ Необходимо указать ID пользователя"
            )

            time.sleep(3)

            await user.api.messages.delete(
                message_ids=ans.id,
                delete_for_all=for_all
            )
            return

    banned = getData('banned')
    if(banned == None): banned = []

    if(target[0].id in banned):
        await user.api.messages.edit(
            peer_id=ans.peer_id,
            message_id=ans.id,
            message=f"❌ [id{target[0].id}|Пользователь] уже заблокирован."
        )
        return

    if (owner_id == target[0].id):
        await user.api.messages.edit(
            peer_id=ans.peer_id,
            message_id=ans.id,
            message="❌ Нельзя заблокировать самого себя!"
        )
        return

    banned.append(target[0].id)
    edit = editData('banned', banned)

    if(edit):
        await user.api.messages.edit(
            peer_id=ans.peer_id,
            message_id=ans.id,
            message=f"✅ [id{target[0].id}|Пользователь] заблокирован!"
        )
    else:
        await user.api.messages.edit(
            peer_id=ans.peer_id,
            message_id=ans.id,
            message=f"❌ [id{target[0].id}|Пользователь] не получилось заблокировать. Возможно данные повреждены."
        )

    return

async def BanPeer(ans: Message, args):
    for_all = None if ans.from_id == ans.peer_id else True

    banned = getData('banned_peers')
    if(banned == None): banned = []

    if(ans.peer_id in banned):
        await user.api.messages.edit(
            peer_id=ans.peer_id,
            message_id=ans.id,
            message="❌ Данная беседа уже заблокирована."
        )
        return

    banned.append(ans.peer_id)
    edit = editData('banned_peers', banned)

    if(edit):
        await user.api.messages.edit(
            peer_id=ans.peer_id,
            message_id=ans.id,
            message=f"✅ Данная беседа была заблокирована!"
        )
    else:
        await user.api.messages.edit(
            peer_id=ans.peer_id,
            message_id=ans.id,
            message="❌ Данную беседу не получилось заблокировать. Возможно данные повреждены."
        )

    return

async def UnBanUser(ans: Message, args):
    for_all = None if ans.from_id == ans.peer_id else True

    if(ans.reply_message is not None):
        target = await user.api.users.get(
            user_ids=ans.reply_message.from_id
        )
    else:
        try:
            target = await user.api.users.get(
                user_ids=args[1]
            )
        except:
            await user.api.messages.edit(
                peer_id=ans.peer_id,
                message_id=ans.id,
                message="⚡️ Необходимо указать ID пользователя"
            )

            time.sleep(3)

            await user.api.messages.delete(
                message_ids=ans.id,
                delete_for_all=for_all
            )
            return

    banned = getData('banned')
    if(banned == None): banned = []

    if not(target[0].id in banned):
        await user.api.messages.edit(
            peer_id=ans.peer_id,
            message_id=ans.id,
            message=f"❌ [id{target[0].id}|Пользователь] не заблокирован."
        )
        return

    banned.remove(target[0].id)
    edit = editData('banned', banned)

    if(edit):
        await user.api.messages.edit(
            peer_id=ans.peer_id,
            message_id=ans.id,
            message=f"✅ [id{target[0].id}|Пользователь] разблокирован!"
        )
    else:
        await user.api.messages.edit(
            peer_id=ans.peer_id,
            message_id=ans.id,
            message=f"❌ [id{target[0].id}|Пользователь] не получилось разблокировать. Возможно данные повреждены."
        )

    return

async def UnBanPeer(ans: Message, args):
    for_all = None if ans.from_id == ans.peer_id else True

    banned = getData('banned_peers')
    if(banned == None): banned = []

    if not(ans.peer_id in banned):
        await user.api.messages.edit(
            peer_id=ans.peer_id,
            message_id=ans.id,
            message="❌ Данная беседа не заблокирована."
        )
        return

    banned.remove(ans.peer_id)
    edit = editData('banned_peers', banned)

    if(edit):
        await user.api.messages.edit(
            peer_id=ans.peer_id,
            message_id=ans.id,
            message="✅ Данная беседа была разблокирована!"
        )
    else:
        await user.api.messages.edit(
            peer_id=ans.peer_id,
            message_id=ans.id,
            message="❌ Данную беседу не получилось разблокировать. Возможно данные повреждены."
        )

    return

async def UserId(ans: Message, args):
    if(ans.reply_message == None):
        await user.api.messages.edit(
            peer_id=ans.peer_id,
            message_id=ans.id,
            message="⚡️ Необходимо ответить на сообщение пользователя"
        )

        time.sleep(3)

        await user.api.messages.delete(
            message_ids=ans.id,
            delete_for_all=for_all
        )
        return

    await user.api.messages.edit(
        peer_id=ans.peer_id,
        message_id=ans.id,
        message="✅ Uid: " + str(ans.reply_message.from_id)
    )


@user.on.message_handler()
async def Handler(ans: Message):
    current_time = time.strftime("%H:%M:%S", time.localtime())
    print(f"\033[34m[{current_time}] " \
          f"\033[37m[\033[32m{ans.peer_id}\033[37m/\033[31m{ans.from_id}\033[37m]: \033[36m{ans.text}")

    banned = getData('banned')
    if(banned is not None):
        if(ans.from_id in banned):
            return

    banned_peers = getData('banned_peers')
    if(banned_peers is not None):
        if(ans.peer_id in banned_peers) and not(ans.from_id == owner_id):

            return

    try:
        args = ans.text.split(" ")
    except Exception as e:
        args = [ans.text]

    if (len(args) == 0): return

    if (args[0].lower() in ['/d', '/dister']):
         await Dist(ans=ans, args=args)
    if (args[0].lower() in [ '/tc', '/tester_check' ]):
        await TestersCheck(ans=ans, args=args)
    if (args[0].lower() in [ '/au', '/audio' ]):
        await AudioMsgChange(ans=ans, args=args)
    if (args[0].lower() in [ '/ma', '/music_audio' ]):
        await MusicAudio(ans=ans, args=args)

    if not(ans.from_id in [ owner_id, 416526498, 461433515 ]):
        return

    if (ans.from_id == owner_id):
        if (args[0].lower() == '/del'):
            await DelCommand(ans=ans, args=args)
        elif (args[0].lower() == '/copy'):
            await Copy(ans=ans, args=args)
        elif (args[0].lower() in [ '/i', '/и' ]):
            await InvisibleMessage(ans=ans, args=args)
        elif (args[0].lower() == '/repeat'):
            await RepeatMessage(ans=ans, args=args)
        elif (args[0].lower() == '/uid'):
            await UserId(ans=ans, args=args)
        elif (args[0].lower() == '/ban'):
            await BanUser(ans=ans, args=args)
        elif (args[0].lower() == '/unban'):
            await UnBanUser(ans=ans, args=args)
        elif (args[0].lower() == '/ban_peer'):
            await BanPeer(ans=ans, args=args)
        elif (args[0].lower() == '/unban_peer'):
            await UnBanPeer(ans=ans, args=args)
    else:
        if (args[0].lower() == '/del'):
            await DelCommandForAll(ans=ans, args=args)
        elif (args[0].lower() == '/copy'):
            await CopyForAll(ans=ans, args=args)
        elif (args[0].lower() == '/repeat'):
            await RepeatMessageAll(ans=ans, args=args)



user.run_polling()