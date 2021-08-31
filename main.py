#!python3
from http.client import METHOD_NOT_ALLOWED
import json
from operator import eq
from random import randint
from dateutil import rrule
from urllib.request import urlretrieve
from PIL import ImageFont,ImageDraw
from graia.application import Group,Friend
from graia.application.event.messages import GroupMessage,FriendMessage
from graia.application.group import Member, MemberInfo
from graia.application.message.elements import Element
from graia.application.message.elements.internal import App, At, Image, Plain, Source
from graia.broadcast import Broadcast
from graia.application import GraiaMiraiApplication, Session
from graia.application.message.chain import MessageChain
import asyncio
import requests
from pathlib import Path
import os
from PIL import Image as Im
import sys
import time
from datetime import date,timedelta
import datetime
import math
import re,itertools
from unomanager import Uno_Manager

loop = asyncio.get_event_loop()

bcc = Broadcast(loop=loop)
app = GraiaMiraiApplication(
    broadcast=bcc,
    connect_info=Session(
        host="http://127.0.0.1:11451", # 填入 httpapi 服务运行的地址
        authKey="k0nashi114514", # 填入 authKey
        account=1227057446, # 你的机器人的 qq 号
        websocket=True # Graia 已经可以根据所配置的消息接收的方式来保证消息接收部分的正常运作.
    )
)    
testing = 1

created = 0
gamers = []
homeowner = 0
findingGamers= 0
started = 0
hand_cards = []
manager = None
homegroup = 0
gamerIdList = []

def init():
    global created,gamers,homeowner,findingGamers,started,hand_cards,manager,homegroup,gamerIdList
    created = 0
    gamers = []
    homeowner = 0
    homegroup = 0
    findingGamers= 0
    started = 0
    manager = None
    gamerIdList = []

@bcc.receiver("GroupMessage")
async def group_message_handler(app: GraiaMiraiApplication, message: MessageChain, group: Group, member: Member):
    global created,testing,gamers,homeowner,findingGamers,started,hand_cards,manager,homegroup,gamerIdList
    if message.asDisplay() == "uno help":
        outmsg = """指令列表
uno create:创建一场游戏，使用该指令者会被作为房主，管理本场游戏的开始结束。
我来:当有人使用uno create后，其他人用于加入游戏
我爬:在还未start的时候，使用“我爬”,可以退出房间 
uno start:房主等想来玩的人齐了以后使用该指令开始游戏
uno over:在create之后如果不玩了记得使用这个指令释放，否则别人也玩不了
看牌:使用后bot会私聊你的手牌是什么
游戏命令:
普通牌/功能牌出牌（例：红9/蓝禁）:如果手中有这张牌，轮到你的时候就可以将这张牌打出
万能牌出牌（例：变色 黄）:万能牌出牌时需要指定之后的颜色，所以需要在牌的名称后加上颜色的名字
摸:当你没有东西能出的时候（非禁），可以摸牌
过:当你上家出了“禁”，而你没有禁可以出的时候，或者你被禁还未解禁的时候使用，用于跳过本回合
出/不出:在摸之后（+2/+4后除外），如果摸到的牌可以出，则可以选择是否打出这张牌
uno:当某个人出完牌后如果只剩下一张牌，则需要说uno，否则如果在下一个玩家出牌之前被人出警，则会被罚摸两张牌
没说uno:可以出警别人有没有忘说uno,仅在下一个人出牌前有效
游戏规则：你不会百度吗？"""
        await app.sendGroupMessage(group,MessageChain.create([Plain(outmsg)]))
    if message.asDisplay() == "uno create":
        if created:
            outmsg = "有人在玩了，您等等吧"
            await app.sendGroupMessage(group,MessageChain.create([Plain(outmsg)]))
        else:
            created = 1
            findingGamers = 1
            gamers.append(member)
            homeowner = member.id
            homegroup = group.id
            outmsg = '正在等待其他成员加入。想要一起玩的说一句“我来”就能一起玩哦'
            await app.sendGroupMessage(group,MessageChain.create([Plain(outmsg)]))
            outmsg = '人组齐了房主说一声“uno start”即可开始游戏'
            await app.sendGroupMessage(group,MessageChain.create([Plain(outmsg)]))
            outmsg = '如果没人或者不玩了，一定要记得“uno over”结束游戏'
            await app.sendGroupMessage(group,MessageChain.create([Plain(outmsg)]))
    if message.asDisplay() == "我来" and findingGamers and group.id == homegroup: 
        if not member in gamers:
            gamers.append(member)
            outmsg = "加入成功！"
            await app.sendGroupMessage(group,MessageChain.create([Plain(outmsg)]))
        else:
            outmsg = "你在队里了"
            await app.sendGroupMessage(group,MessageChain.create([Plain(outmsg)]))
    if message.asDisplay() == "我爬" and not started and member in gamers and member.id != homeowner:
        gamers.remove(member)
        outmsg = member.name + "灰溜溜的爬了"
        await app.sendGroupMessage(group,MessageChain.create([Plain(outmsg)]))

    if message.asDisplay() == "uno start" and member.id == homeowner:
        if len(gamers) < 3 and not testing:
            outmsg = "人不够，您再等等"
            await app.sendGroupMessage(group,MessageChain.create([Plain(outmsg)]))
        else:
            outmsg = "游戏开始！"
            await app.sendGroupMessage(group,MessageChain.create([Plain(outmsg)]))
            for i in range(1,len(gamers)+1):
                gamerIdList.append(str(i))
            findingGamers = 0
            started = 1
            manager = Uno_Manager(len(gamers))
            outmsg = "正在发牌……"
            await app.sendGroupMessage(group,MessageChain.create([Plain(outmsg)]))
            manager.startUno()
            outmsg = "发牌完成，发送“看牌”，机器人就会偷偷告诉你你的牌是什么噢！"
            await app.sendGroupMessage(group,MessageChain.create([Plain(outmsg)]))  
            for eachmambers in gamers:
                cards = sorted(manager.getHandCards()[gamers.index(eachmambers)],key = lambda x:manager.cardOrder.index(x))
                outmsg = "你的手牌是：" + "、".join(cards)
                await app.sendTempMessage(group,eachmambers,MessageChain.create([Plain(outmsg)]))
    if message.asDisplay() == "看牌" and started and member in gamers and started:   
        cards = sorted(manager.getHandCards()[gamers.index(member)],key = lambda x:manager.cardOrder.index(x))
        outmsg = "你的手牌是：" + "、".join(cards)
        await app.sendTempMessage(group,member,MessageChain.create([Plain(outmsg)]))
    if message.asDisplay() == "uno over" and (member.id == homeowner or member.id == 562723584) and created:
        outmsg = "游戏结束！"
        await app.sendGroupMessage(group,MessageChain.create([Plain(outmsg)]))
        init()
    #?出牌
    if (message.asDisplay() in Uno_Manager.cards or message.asDisplay()[:2] == "+4" or message.asDisplay()[:2] == "变色")and member in gamers and started:
        if manager.banCheck(gamers.index(member)):
            outmsg="你被禁了，现在不能出牌"
            await app.sendGroupMessage(group,MessageChain.create([Plain(outmsg)]))
            return
        if not manager.isTurn(gamers.index(member),message.asDisplay()):
            outmsg="现在不是你的回合"
            await app.sendGroupMessage(group,MessageChain.create([Plain(outmsg)]))
            return
        if manager.getCheckAfterTouchFlag():
            outmsg="你只能选择“出”/“不出”"
            await app.sendGroupMessage(group,MessageChain.create([Plain(outmsg)]))
            return
        if message.asDisplay() in manager.getHandCards()[gamers.index(member)] or message.asDisplay()[:2] in manager.getHandCards()[gamers.index(member)]:
            cardname = "$$"
            if message.asDisplay()[:2] =="+4" or message.asDisplay()[:2] == "变色":
                msg = message.asDisplay().replace(" ","")
                if len(msg) == 3:
                    if msg[2] in "红黄蓝绿":
                        cardname = msg[:2]
                        color = msg[2]
                else:
                    outmsg="功能牌请输入要转换的颜色，例如“变色 黄”"
                    await app.sendGroupMessage(group,MessageChain.create([Plain(outmsg)]))
                    return
            else:
                cardname = message.asDisplay()
                color = None
            if manager.outCard(gamers.index(member),cardname,color):
                outmsg = member.name + " 出了一张：" + manager.getLastCard()
                await app.sendGroupMessage(group,MessageChain.create([Plain(outmsg)]))
                winnerId = manager.winCheck()
                if winnerId != -1:
                    outmsg = "游戏结束，获胜者：" + member.name
                    await app.sendGroupMessage(group,MessageChain.create([Plain(outmsg)]))
                    init()
                    return
                manager.lastOneCheck()
                swaped = 0
                if (swapcard := manager.getSwapCard()):
                    if swapcard & 0b01:
                        manager.zeroSwap()
                        outmsg = "所有人手牌递交给下家！"
                        await app.sendGroupMessage(group,MessageChain.create([Plain(outmsg)]))
                        manager.lastOneCheck()
                        for eachmambers in gamers:
                            cards = sorted(manager.getHandCards()[gamers.index(eachmambers)],key = lambda x:manager.cardOrder.index(x))
                            outmsg = "你的手牌是：" + "、".join(cards)
                            await app.sendTempMessage(group,eachmambers,MessageChain.create([Plain(outmsg)]))
                        swaped = 1
                    elif swapcard & 0b10:
                        outmsg = "请选择你要交换的玩家编号：（例如：1）\n"
                        gamerid = 1
                        for i in gamers:
                            outmsg += str(gamerid) + "." + i.name + "还剩" + str(len(manager.getHandCards()[gamerid-1])) + "张牌" +"\n"
                            gamerid += 1
                        await app.sendGroupMessage(group,MessageChain.create([Plain(outmsg)]))
                        manager.waitingSwap()
                        return
                manager.turnNext()
                manager.resetUnoed()
                outmsg = "现在轮到：" + gamers[manager.getTurn()].name + "出牌了，Ta还剩" + str(len(manager.getHandCards()[manager.getTurn()])) + "张牌"
                if manager.getLastCard() != "":
                    outmsg += ",上一张牌是：" + manager.getLastCard()
                await app.sendGroupMessage(group,MessageChain.create([Plain(outmsg)]))
                if manager.banCheck(manager.getTurn()):
                    outmsg = gamers[manager.getTurn()].name + "还有" + str(manager.getBanDict(manager.getTurn())) + "回合解禁，请选择“过”"
                    await app.sendGroupMessage(group,MessageChain.create([Plain(outmsg)]))
                if not swaped:
                    cards = sorted(manager.getHandCards()[gamers.index(member)],key = lambda x:manager.cardOrder.index(x))
                    outmsg = "你的手牌是：" + "、".join(cards)
                    await app.sendTempMessage(group,member,MessageChain.create([Plain(outmsg)]))
                    nextmember = gamers[manager.getTurn()]
                    cards = sorted(manager.getHandCards()[gamers.index(nextmember)],key = lambda x:manager.cardOrder.index(x))
                    outmsg = "你的手牌是：" + "、".join(cards)
                    await app.sendTempMessage(group,nextmember,MessageChain.create([Plain(outmsg)]))
            else:
                outmsg = "你不能出这个哦，上一张牌是：" + manager.getLastCard()
                await app.sendGroupMessage(group,MessageChain.create([Plain(outmsg)]))
        else:
            outmsg = "你出的什么jb？"
            await app.sendGroupMessage(group,MessageChain.create([Plain(outmsg)]))
    
    if message.asDisplay() == "摸" and member in gamers and started:
        if not manager.isTurn(gamers.index(member)):
            outmsg="现在不是你的回合"
            await app.sendGroupMessage(group,MessageChain.create([Plain(outmsg)]))
            return
        if manager.getBanFlag() > 0:
            outmsg="现在不能摸，你只能出“禁”或者“过”"
            await app.sendGroupMessage(group,MessageChain.create([Plain(outmsg)]))
            return
        if manager.getCheckAfterTouchFlag():
            outmsg="你只能选择“出”/“不出”"
            await app.sendGroupMessage(group,MessageChain.create([Plain(outmsg)]))
            return
        touchNum = manager.touch(gamers.index(member))
        outmsg = member.name + "摸了" + str(touchNum) + "张牌"
        await app.sendGroupMessage(group,MessageChain.create([Plain(outmsg)]))
        if manager.checkAfterTouch(touchNum):
            card = manager.getHandCards()[gamers.index(member)][-1]
            outmsg = "你抽到了一张：" + card + "，请在群里选择“出”/“不出”"
            await app.sendTempMessage(group,member,MessageChain.create([Plain(outmsg)]))
            outmsg = "请选择“出”/“不出”"
            await app.sendGroupMessage(group,MessageChain.create([Plain(outmsg)]))
            return
        manager.turnNext()
        manager.resetUnoed()
        outmsg = "现在轮到：" + gamers[manager.getTurn()].name + "出牌了，Ta还剩" + str(len(manager.getHandCards()[manager.getTurn()])) + "张牌"
        if manager.getLastCard() != "":
            outmsg += ",上一张牌是：" + manager.getLastCard()
        await app.sendGroupMessage(group,MessageChain.create([Plain(outmsg)]))
        if manager.banCheck(manager.getTurn()):
            outmsg = gamers[manager.getTurn()].name + "还有" + str(manager.getBanDict(manager.getTurn())) + "回合解禁，请选择“过”"
            await app.sendGroupMessage(group,MessageChain.create([Plain(outmsg)]))
        cards = sorted(manager.getHandCards()[gamers.index(member)],key = lambda x:manager.cardOrder.index(x))
        outmsg = "你的手牌是：" + "、".join(cards)
        await app.sendTempMessage(group,member,MessageChain.create([Plain(outmsg)]))
        nextmember = gamers[manager.getTurn()]
        cards = sorted(manager.getHandCards()[gamers.index(nextmember)],key = lambda x:manager.cardOrder.index(x))
        outmsg = "你的手牌是：" + "、".join(cards)
        await app.sendTempMessage(group,nextmember,MessageChain.create([Plain(outmsg)]))

    if message.asDisplay() == "过" and member in gamers and started:
        if not manager.isTurn(gamers.index(member)):
            outmsg="现在不是你的回合"
            await app.sendGroupMessage(group,MessageChain.create([Plain(outmsg)]))
            return
        skipFlag = manager.couldSkip()
        if skipFlag != 0:
            if (skipFlag & 0b10) != 0:
                outmsg= member.name + "选择了跳过，被禁了" + str(manager.getBanFlag()) + "回合"
                await app.sendGroupMessage(group,MessageChain.create([Plain(outmsg)]))
            manager.banCount()

            if (skipFlag & 0b01) != 0:
                bandict = manager.getBanDict(manager.getTurn())
                if bandict > 0:
                    outmsg= member.name + "还要被禁" + str(bandict) + "回合"
                else:
                    outmsg= member.name + "解禁"
                if plusNum := manager.getPlusNum():
                    outmsg += ",并摸了" + str(plusNum) + "张牌"
                manager.gamerDraw(gamers.index(member),plusNum)
                manager.resetPlusNum()
                await app.sendGroupMessage(group,MessageChain.create([Plain(outmsg)]))
            manager.turnNext()
            manager.resetUnoed()
            outmsg = "现在轮到：" + gamers[manager.getTurn()].name + "出牌了，Ta还剩" + str(len(manager.getHandCards()[manager.getTurn()])) + "张牌"
            if manager.getLastCard() != "":
                outmsg += ",上一张牌是：" + manager.getLastCard()
            await app.sendGroupMessage(group,MessageChain.create([Plain(outmsg)]))
            if manager.banCheck(manager.getTurn()):
                outmsg = gamers[manager.getTurn()].name + "还有" + str(manager.getBanDict(manager.getTurn())) + "回合解禁，请选择“过”"
                await app.sendGroupMessage(group,MessageChain.create([Plain(outmsg)]))
            cards = sorted(manager.getHandCards()[gamers.index(member)],key = lambda x:manager.cardOrder.index(x))
            outmsg = "你的手牌是：" + "、".join(cards)
            await app.sendTempMessage(group,member,MessageChain.create([Plain(outmsg)]))
            nextmember = gamers[manager.getTurn()]
            cards = sorted(manager.getHandCards()[gamers.index(nextmember)],key = lambda x:manager.cardOrder.index(x))
            outmsg = "你的手牌是：" + "、".join(cards)
            await app.sendTempMessage(group,nextmember,MessageChain.create([Plain(outmsg)]))
            return
        else:
            outmsg= "你只有在“禁”之后，才能选择跳过"
            await app.sendGroupMessage(group,MessageChain.create([Plain(outmsg)]))

    if message.asDisplay() == "出" or message.asDisplay() == "不出" or (message.asDisplay()[:2] == "出 " and message.asDisplay()[2] in "红黄蓝绿" and len(message.asDisplay()) == 3) and manager.getCheckAfterTouchFlag() and started and member in gamers:
        if not manager.isTurn(gamers.index(member)):
            outmsg="现在不是你的回合"
            await app.sendGroupMessage(group,MessageChain.create([Plain(outmsg)]))
            return
        if not manager.getCheckAfterTouchFlag():
            outmsg="你出nm呢？"
            await app.sendGroupMessage(group,MessageChain.create([Plain(outmsg)]))
            return
        msg = manager.getHandCards()[gamers.index(member)][-1]
        if len(message.asDisplay()) == 3:
            msg += " " + message.asDisplay()[2]
        print(msg)
        if message.asDisplay()[0] == "出" and member == gamers[manager.getTurn()]:
            if msg[:2] =="+4" or msg[:2] == "变色":
                msg = msg.replace(" ","")
                if len(msg) == 3:
                    if msg[2] in "红黄蓝绿":
                        cardname = msg[:2]
                        color = msg[2]
                else:
                    outmsg="功能牌请输入要转换的颜色，例如“出 黄”"
                    await app.sendGroupMessage(group,MessageChain.create([Plain(outmsg)]))
                    return
            else:
                cardname = msg
                color = None
            if manager.outCard(gamers.index(member),cardname,color):
                manager.lastOneCheck()
                outmsg = member.name + " 出了一张：" + manager.getLastCard()
                await app.sendGroupMessage(group,MessageChain.create([Plain(outmsg)]))
        if message.asDisplay() == "不出" and member == gamers[manager.getTurn()]:
            pass
        manager.resetCheckAfterTouchFlag()
        swaped = 0
        if (swapcard := manager.getSwapCard()):
            if swapcard & 0b01:
                manager.zeroSwap()
                outmsg = "所有人手牌递交给下家！"
                await app.sendGroupMessage(group,MessageChain.create([Plain(outmsg)]))
                manager.lastOneCheck()
                for eachmambers in gamers:
                    cards = sorted(manager.getHandCards()[gamers.index(eachmambers)],key = lambda x:manager.cardOrder.index(x))
                    outmsg = "你的手牌是：" + "、".join(cards)
                    await app.sendTempMessage(group,eachmambers,MessageChain.create([Plain(outmsg)]))
                swaped = 1
            elif swapcard & 0b10:
                outmsg = "请选择你要交换的玩家编号：（例如：1）\n"
                gamerid = 1
                for i in gamers:
                    outmsg += str(gamerid) + "." + i.name + "还剩" + str(len(manager.getHandCards()[gamerid-1])) + "张牌" +"\n"
                    gamerid += 1
                await app.sendGroupMessage(group,MessageChain.create([Plain(outmsg)]))
                manager.waitingSwap()
                return
        manager.turnNext()
        manager.resetUnoed()
        outmsg = "现在轮到：" + gamers[manager.getTurn()].name + "出牌了，Ta还剩" + str(len(manager.getHandCards()[manager.getTurn()])) + "张牌"
        if manager.getLastCard() != "":
            outmsg += ",上一张牌是：" + manager.getLastCard()
        await app.sendGroupMessage(group,MessageChain.create([Plain(outmsg)]))
        if manager.banCheck(manager.getTurn()):
            outmsg = gamers[manager.getTurn()].name + "还有" + str(manager.getBanDict(manager.getTurn())) + "回合解禁，请选择“过”"
            await app.sendGroupMessage(group,MessageChain.create([Plain(outmsg)]))
        cards = sorted(manager.getHandCards()[gamers.index(member)],key = lambda x:manager.cardOrder.index(x))
        outmsg = "你的手牌是：" + "、".join(cards)
        await app.sendTempMessage(group,member,MessageChain.create([Plain(outmsg)]))
        nextmember = gamers[manager.getTurn()]
        cards = sorted(manager.getHandCards()[gamers.index(nextmember)],key = lambda x:manager.cardOrder.index(x))
        outmsg = "你的手牌是：" + "、".join(cards)
        await app.sendTempMessage(group,nextmember,MessageChain.create([Plain(outmsg)]))
        return
    if message.asDisplay() == "uno":
        if not created:
            outmsg = "想来把uno吗？“uno create”即可开启一场游戏哦！想了解游戏规则可以使用“uno help”"
            await app.sendGroupMessage(group,MessageChain.create([Plain(outmsg)]))
        else:
            if not member in gamers:
                return
            unoFlag = manager.getLastOneCheckFlag()
            if (unoFlag == -1 and member != gamers[manager.getTurn()] and (member == gamers[manager.getTurn()] and len(manager.getHandCards[manager.getTurn()]) != 2)):
                outmsg = "你uno nm呢？"
                await app.sendGroupMessage(group,MessageChain.create([Plain(outmsg)])) 
                return
            if gamers.index(member) == unoFlag:
                manager.resetLastOneCheckFlag()
                return
            manager.setUnoed()
            
    if message.asDisplay() == "没说uno" and started and member in gamers:
        lastOneCheckFlag = manager.getLastOneCheckFlag()
        if lastOneCheckFlag != -1:
            manager.gamerDraw(lastOneCheckFlag,2)
            outmsg = gamers[lastOneCheckFlag].name + "忘喊uno，被罚两张"
            manager.resetLastOneCheckFlag()
            await app.sendGroupMessage(group,MessageChain.create([Plain(outmsg)]))
            cards = sorted(manager.getHandCards()[lastOneCheckFlag],key = lambda x:manager.cardOrder.index(x))
            outmsg = "你的手牌是：" + "、".join(cards)
            await app.sendTempMessage(group,gamers[lastOneCheckFlag],MessageChain.create([Plain(outmsg)]))
        else:
            print(gamers.index(member))
            # manager.gamerDraw(gamers.index(member),1)
            # outmsg = "乱出警是吧，赏你一张"
            outmsg = "乱出警是吧，爬"
            await app.sendGroupMessage(group,MessageChain.create([Plain(outmsg)]))
            cards = sorted(manager.getHandCards()[gamers.index(member)],key = lambda x:manager.cardOrder.index(x))
            outmsg = "你的手牌是：" + "、".join(cards)
            await app.sendTempMessage(group,member,MessageChain.create([Plain(outmsg)]))
    if message.asDisplay() in gamerIdList and started and member in gamers and manager.getWaitSwap():
        if not manager.isTurn(gamers.index(member)):
            outmsg="现在不是你的回合"
            await app.sendGroupMessage(group,MessageChain.create([Plain(outmsg)]))
            return
        if gamers.index(member) == int(message.asDisplay())-1:
            outmsg="不能跟自己换牌"
            await app.sendGroupMessage(group,MessageChain.create([Plain(outmsg)]))
            return
        manager.sevenSwap(gamers.index(member),int(message.asDisplay())-1)
        outmsg = "交换了 " + member.name +" 和" + gamers[int(message.asDisplay())-1].name +"的手牌"
        await app.sendGroupMessage(group,MessageChain.create([Plain(outmsg)]))
        cards = sorted(manager.getHandCards()[gamers.index(member)],key = lambda x:manager.cardOrder.index(x))
        outmsg = "你的手牌是：" + "、".join(cards)
        await app.sendTempMessage(group,member,MessageChain.create([Plain(outmsg)]))
        cards = sorted(manager.getHandCards()[int(message.asDisplay())-1],key = lambda x:manager.cardOrder.index(x))
        outmsg = "你的手牌是：" + "、".join(cards)
        await app.sendTempMessage(group,gamers[int(message.asDisplay())-1],MessageChain.create([Plain(outmsg)]))
        manager.lastOneCheck()
        manager.turnNext()
        manager.resetUnoed()
        outmsg = "现在轮到：" + gamers[manager.getTurn()].name + "出牌了，Ta还剩" + str(len(manager.getHandCards()[manager.getTurn()])) + "张牌"
        if manager.getLastCard() != "":
            outmsg += ",上一张牌是：" + manager.getLastCard()
        await app.sendGroupMessage(group,MessageChain.create([Plain(outmsg)]))
        if manager.banCheck(manager.getTurn()):
            outmsg = gamers[manager.getTurn()].name + "还有" + str(manager.getBanDict(manager.getTurn())) + "回合解禁，请选择“过”"
            await app.sendGroupMessage(group,MessageChain.create([Plain(outmsg)]))
        nextmember = gamers[manager.getTurn()]
        cards = sorted(manager.getHandCards()[gamers.index(nextmember)],key = lambda x:manager.cardOrder.index(x))
        outmsg = "你的手牌是：" + "、".join(cards)
        await app.sendTempMessage(group,nextmember,MessageChain.create([Plain(outmsg)]))

    if message.asDisplay() == "玩家列表" and started == 1 and member in gamers:
        for i in gamers:
            outmsg += str(gamerid) + "." + i.name + "还剩" + str(len(manager.getHandCards()[gamerid-1])) + "张牌" +"\n"
            gamerid += 1
        await app.sendGroupMessage(group,MessageChain.create([Plain(outmsg)]))



app.launch_blocking()

try:
    loop.run_forever()
except KeyboardInterrupt:
    exit()