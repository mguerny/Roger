import asyncio
import discord
import pyautogui

token = 'Wedz\'s way'
with open('./discord_token.txt') as f:
    token = f.read().strip()

# client
client = discord.Client()

# channel id
channelId_ACckChat = "494840511308234764"
channelId_RogerLog = "615438024641347592"

channelList = [
    channelId_ACckChat,
    channelId_RogerLog
]

# building status
# 0 : grey (nobody)
# 1 : blue (us)
# 2 : red (them)
buildingList = [0, 0, 0, 0, 0, 0]

# building position on screenshot. Must be changed each city
buildingPos = [[298, 345], [241, 495], [491, 588], [771, 600], [979, 500], [963, 327]]

# if first test, don't send message since every building goes from 0gray to something else
firstTest = True

disconnected = False


@client.event
async def on_ready():
    print("Ready")
    message = ":eggplant:"
    await sendMessage(channelId_ACckChat, message)


@client.event
async def on_message(message):
    global disconnected

    # annule si l'auteur du message est le bot
    if message.author == client.user:
        return

    # annule si mauvais channel
    if not str(message.channel.id) in channelList:
        return

    if message.content.upper().startswith('ROGERSAYS'):
        await message.delete()
        text = message.content
        if len(text) > 9:
            msg = text[9:]
            canTalk = False
            for role in message.author.roles:
                if role.name == 'Admin' or role.name == 'Leader':
                    canTalk = True
            if canTalk:
                await sendMessage(message.channel.id, msg)

    if message.content.upper().startswith('WARSTATUS'):
        await message.channel.send(file=discord.File('screen.png'))

    if message.content.upper().startswith('RECONNECT'):
        canUse = False
        for role in message.author.roles:
            if role.name == 'AdminRoger':
                canUse = True
        if canUse:
            if not disconnected:
                text = "What are you doing, I'm not disconnected :face_with_raised_eyebrow:"
                await message.channel.send(text)
            else:
                pyautogui.click(x=660, y=620)
                disconnected = False
                text = "I'm reconnecting, please wait a few seconds :clock1:"
                await message.channel.send(text)
        else:
            text = "Help, "
            text += message.author.mention
            text += " wants to touch me :sob:"
            await message.channel.send(text)


def getEmoji(emojiName):
    return str(discord.utils.get(client.emojis, name=emojiName))


def sendMessage(channelParamID, messageParam):
    return client.get_channel(int(channelParamID)).send(messageParam)


async def my_background_task():
    global buildingList
    global buildingPos
    global firstTest
    global disconnected

    await client.wait_until_ready()

    # 0 : grey (nobody)
    # 1 : blue (us)
    # 2 : red (them)
    newBuildingList = [0, 0, 0, 0, 0, 0]

    while not client.is_closed():

        print("============================= New iteration")

        # take and save screenshot
        im = pyautogui.screenshot(region=(108, 32, 1109, 693))
        im.save(r"./screen.png")

        # locate the reconnect button if any
        reconnectButton = pyautogui.locateOnScreen('reconnect.png')
        print(reconnectButton)
        if reconnectButton and not disconnected:
            disconnected = True

            # get AdminRoger role for ping
            roles = list(client.guilds)[0].roles
            for role in roles:
                if role.name == 'AdminRoger':
                    adminRoger = role
            message = adminRoger.mention
            message += " Disconnection detected, waiting for command"
            await sendMessage(channelId_ACckChat, message)

        # check each buildings for pixel RGB color
        if not disconnected:
            for i in range(0, 6):
                pos1 = buildingPos[i][0]  # building i position x
                pos2 = buildingPos[i][1]  # building i position y
                # get pixel at coords pos1, pos2. return (R, G, B)
                pixel = im.getpixel((pos1, pos2))
                # blue
                if pixel == (144, 179, 235):
                    newBuildingList[i] = 1

                # red
                if pixel == (255, 101, 100):
                    newBuildingList[i] = 2

                # grey
                if pixel == (94, 106, 131):
                    newBuildingList[i] = 0

            # display old status and new status, for debug
            print(buildingList)
            print(newBuildingList)

            somethingMoved = False
            # only if not first iteration of the background task
            if not firstTest:

                message = ""

                # for each building
                for i in range(0, 6):

                    # if status has changed
                    if buildingList[i] != newBuildingList[i]:
                        somethingMoved = True

                        # if nobody has the building
                        if newBuildingList[i] == 0:
                            if buildingList[i] == 1:  # 1 : was ours
                                message += "We lost building " + str(i+1) + " :weary:\n"
                            else:  # 2 : was theirs
                                message += "They lost building " + str(i+1) + ", focus P bots :grimacing:\n"

                        # if we have the building
                        if newBuildingList[i] == 1:
                            message += "We took "
                            if buildingList[i] == 0:  # 0 : was empty
                                message += "empty building " + str(i+1) + " :grin:\n"
                            else:  # 2 : was theirs
                                message += "their building " + str(i+1) + " " + getEmoji("pika") + "\n"

                        # if they have the building
                        if newBuildingList[i] == 2:
                            message += "They took "
                            if buildingList[i] == 0:  # 0 : was empty
                                message += "empty building " + str(i+1) + " :angry:\n"
                            else:  # 1 : was ours
                                message += "our building " + str(i+1) + " :rage:\n"

                # only if the status of one of the buildings has changed
                if somethingMoved:

                    # get senior role for ping
                    roles = list(client.guilds)[0].roles
                    for role in roles:
                        if role.name == 'Senior':
                            senior = role
                    message = senior.mention + " " + message

                    # send message + screenshot
                    await sendMessage(channelId_ACckChat, message)
                    await client.get_channel(int(channelId_ACckChat)).send(file=discord.File('screen.png'))

        # first iteration done, not firstTest anymore
        firstTest = False

        # update building status
        buildingList = newBuildingList[:]

        # task runs every n seconds
        n = 15
        await asyncio.sleep(n)


client.loop.create_task(my_background_task())
client.run(token)
