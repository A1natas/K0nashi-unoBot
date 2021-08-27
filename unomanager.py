from asyncio.events import Handle
import random

from pydantic.parse import load_str_bytes

class Uno_Manager:
    cards=["红1","红2","红3","红4","红5","红6","红7","红8","红9","红0",
        "红1","红2","红3","红4","红5","红6","红7","红8","红9",
        "蓝1","蓝2","蓝3","蓝4","蓝5","蓝6","蓝7","蓝8","蓝9","蓝0",
        "蓝1","蓝2","蓝3","蓝4","蓝5","蓝6","蓝7","蓝8","蓝9",
        "黄1","黄2","黄3","黄4","黄5","黄6","黄7","黄8","黄9","黄0",
        "黄1","黄2","黄3","黄4","黄5","黄6","黄7","黄8","黄9",
        "绿1","绿2","绿3","绿4","绿5","绿6","绿7","绿8","绿9","绿0",
        "绿1","绿2","绿3","绿4","绿5","绿6","绿7","绿8","绿9",
        "红禁","红禁","绿禁","绿禁","黄禁","黄禁","蓝禁","蓝禁",
        "红转","红转","绿转","绿转","黄转","黄转","蓝转","蓝转",
        "红+2","红+2","绿+2","绿+2","黄+2","黄+2","蓝+2","蓝+2",
        "变色","变色","变色","变色",
        "+4","+4","+4","+4",
    ]
    cardOrder = [
    "红0","红1","红2","红3","红4","红5","红6","红7","红8","红9","红禁","红转","红+2",
    "黄0","黄1","黄2","黄3","黄4","黄5","黄6","黄7","黄8","黄9","黄禁","黄转","黄+2",
    "蓝0","蓝1","蓝2","蓝3","蓝4","蓝5","蓝6","蓝7","蓝8","蓝9","蓝禁","蓝转","蓝+2",
    "绿0","绿1","绿2","绿3","绿4","绿5","绿6","绿7","绿8","绿9","绿禁","绿转","绿+2",
    "变色","+4",
    ]
    def __init__(self,gamers):
        self.gamers = gamers
    
    def draw(self,num):
        if num <= len(self.gaming_cards):
            pass
        else:
            new_cards = Uno_Manager.cards
            random.shuffle(new_cards)
            self.gaming_cards.extend(new_cards)
        draw_card = self.gaming_cards[:num]
        self.gaming_cards = self.gaming_cards[num:]

        return draw_card
        # return ["红禁"] + ["红+2"] + ["红禁"] + ["红+2"]

    def gamerDraw(self,gamerId,num):
        self.hand_cards[gamerId].extend(self.draw(num))

    def startUno(self):
        self.gaming_cards = Uno_Manager.cards
        random.shuffle(self.gaming_cards)
        self.hand_cards = []
        for i in range(self.gamers):
            self.hand_cards.append(self.draw(5))
        self.lastCard = ""
        self.plusNum = 0
        self.lastPlus = 0
        self.turnId = 0
        self.turnForward = 1
        self.banFlag = 0
        self.banDict = {}
        self.checkAfterTouchFlag = False
        self.unoFlag = {}
        self.lastOneCheckFlag = -1
        self.swapCard = 0b00
        self.waitSwap = 0

    def getHandCards(self):
        return self.hand_cards

    def getCardOrder(self):
        return self.cardOrder

    def legalCheck(self,lastCard,cardname):
        if self.lastPlus != 0 and not '+' in cardname:
            return False
        if self.lastPlus == 4 and "+2" in cardname:
            return False
        if "禁" in lastCard and not "禁" in cardname and self.banFlag != 0:
            return False
        if cardname == "+4":
            return True
        if cardname == "变色":
            return True
        if lastCard != "":
            if lastCard[0] != cardname[0] and lastCard[1] != cardname[1]:
                return False
        return True

    def changelastCard(self,cardname,color=None):
        if color != None:
            self.lastCard = color + "$"
        else:
            self.lastCard = cardname
        if "+" in cardname:
            if cardname == "+4":
                self.lastPlus = 4
                self.plusNum +=4
            else:
                self.lastPlus = 2
                self.plusNum +=2

    def getPlusNum(self):
        return self.plusNum

    def resetPlusNum(self):
        self.plusNum = 0

    def getLastCard(self):
        if "$" in self.lastCard:
            if self.lastPlus == 0:
                cardname = "变色 " + self.lastCard[0]
            else:
                cardname = "+4 " + self.lastCard[0]
        else:
            cardname = self.lastCard
        return cardname

    def outCard(self,gamerId,cardname,color=None):
        if self.lastCard == "":
            pass
        else:
            if not self.legalCheck(self.lastCard,cardname):
                return False
            else: 
                pass
        self.hand_cards[gamerId].remove(cardname)
        self.changelastCard(cardname,color)
        if "转" in cardname:
            self.turnForward *= -1
        if "禁" in cardname:
            self.banFlag += 1
        if "0" or "7" in cardname:
            if "0" in cardname:
                self.swapCard |= 0b01
            if "7" in cardname:
                self.swapCard |= 0b10
        return True
    
    def winCheck(self):
        for i in range(len(self.hand_cards)):
            if len(self.hand_cards[i]) == 0:
                return i
        return -1

    def isTurn(self,gamerId,outCard = "$$"):
        if gamerId == self.turnId:
            return True
        elif outCard == self.lastCard:
            self.turnId = gamerId
            return True
        return False

    def turnNext(self):
        self.turnId = (self.turnId + self.turnForward + len(self.hand_cards)) % len(self.hand_cards)
    

    def getTurn(self):
        return self.turnId

    def touch(self,gamerId):
        if self.plusNum != 0:
            num = self.plusNum
            self.plusNum = 0
            self.lastPlus = 0
        else:
            num = 1
        self.hand_cards[gamerId].extend(self.draw(num)) 
        return num

    def getBanFlag(self):
        return self.banFlag

    def banCheck(self,gamerId):
        return gamerId in self.banDict.keys()

    def banAdd(self,gameId):
        self.banDict[gameId] += self.banFlag
        self.banFlag = 0     

    def getBanDict(self,gamerId):
        if gamerId in self.banDict.keys():
            return  self.banDict[gamerId]
        else:
            return 0

    def banCount(self):
        if self.banFlag > 0:
            if self.getTurn() in self.banDict.keys():
                self.banDict[self.getTurn()] += self.banFlag
            else:
                self.banDict[self.getTurn()] = self.banFlag
            self.banFlag = 0
        self.banDict[self.getTurn()] -= 1
        if self.banDict[self.getTurn()] == 0:
            del self.banDict[self.getTurn()]
    
    def couldSkip(self):
        skipFlag = 0b00
        if self.banCheck(self.getTurn()):
            skipFlag |= 0b01
        if self.banFlag != 0:
            skipFlag |= 0b10
        return skipFlag
        
    def checkAfterTouch(self,touchNum):
        if touchNum > 1:
            return False
        if self.legalCheck(self.lastCard,self.hand_cards[self.getTurn()][-1]):
            self.checkAfterTouchFlag = True
            return True
        return False

    def getCheckAfterTouchFlag(self):
        return self.checkAfterTouchFlag
        
    def resetCheckAfterTouchFlag(self):
        self.checkAfterTouchFlag = False

    def lastOneCheck(self):
        if len(self.hand_cards[self.getTurn()]) == 1:
            self.lastOneCheckFlag = self.getTurn()
        else:
            self.lastOneCheckFlag = -1
    def resetLastOneCheckFlag(self):
        self.lastOneCheckFlag = -1
    
    def getLastOneCheckFlag(self):
        return self.lastOneCheckFlag
    
    def getSwapCard(self):
        return self.swapCard
    
    def zeroSwap(self):
        print(self.hand_cards)
        newHandCards = []
        if self.turnForward == 1:
            newHandCards.append(self.hand_cards[-1])
            for i in range(len(self.hand_cards) - 1):
                newHandCards.append(self.hand_cards[i])
        else:
            for i in range(1,len(self.hand_cards)):
                newHandCards.append(self.hand_cards[i])
            newHandCards.append(self.hand_cards[0])    
        self.hand_cards = newHandCards
        self.waitSwap = 0
        self.swapCard = 0
        print(self.hand_cards)


    def sevenSwap(self,gamerIda,gamerIdb):
        print(self.hand_cards)
        print(gamerIda,gamerIdb)
        self.hand_cards[gamerIda],self.hand_cards[gamerIdb] = self.hand_cards[gamerIdb],self.hand_cards[gamerIda]
        self.waitSwap = 0
        self.swapCard = 0
        print(self.hand_cards)

    def waitingSwap(self):
        self.waitSwap = 1
    
    def getWaitSwap(self):
        return self.waitSwap