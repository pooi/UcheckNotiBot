#-*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import os
import time
import datetime
import MySQLdb

from MyScheduler import * # import Scheduler
from SupportMysql import * # import SQL support class
from AdditionFunc import * # import addition function class

import threading

# Telegram interface
import telebot
from telebot import types, apihelper

API_TOKEN = '<INPUT_YOUR_API_KEY>'
bot = telebot.TeleBot(API_TOKEN)

administratorChatID = '<INPUT_YOUR_TELEGRAM_CHAT_ID>'

# Connect database
host = '<INPUT_YOUR_DATABASE_SERVER_HOST>'
db_id = '<INPUT_YOUR_DATABASE_ID>'
db_pw = '<INPUT_YOUR_DATABASE_PASSWORD>'
db_name = '<INPUT_YOUR_DATABASE_NAME>'
db = MySQLdb.connect( host, db_id, db_pw, db_name, charset='utf8') # Encoding utf-8

# Generate class method
mydb = SupportMysql(db) # DB controller
scheduler = Scheduler(bot)
addF = AdditionFunc()

addSubTemp = {} # Used in the process of adding the class(user subject)
deleteSubTemp = {} # Used in the process of removing the class(user subject)

# If you want to send help message to user, please input your message.
help_message =(
    "유체크 알림 봇은 사용자에게 출석 체크 확인 메시지를 보내줍니다. "
    "메시지를 받고 싶은 수업을 /add 명령어를 통해 서버에 저장하면 "
    "저장된 수업 시간에서 최대 10분 전에 출석 체크 확인 메시지를 전송합니다.\n\n"

    "이 봇의 고유 주소는 telegram.me/UcheckNotiBot 입니다. "
    "유체크 알림 봇은 오픈소스로 프로젝트입니다. "
    "소스 코드는 깃허브(github.com/pooi/UcheckNotiBot)에서 확인할 수 있습니다."
    "기타 문의 사항은 ldayou@me.com으로 문의 바랍니다. "
    "이메일로 문의할 경우에는 ChatID를 함께 전송해주세요. "
    "(ChatID는 /info 명령어를 통해 확인할 수 있습니다.)\n"
    "** 유체크 알림 봇은 사용자가 입력한 정보, ChatID, 활성화한 날짜 이외의 정보(이름 등)를"
    " 수집하지 않습니다.\n\n"

    "유체크 알림 봇에서 사용할 수 있는 명령어는 총 5개로 각각의 명령어에 대한 설명은 아래와 같습니다.\n\n"
    "/help - 도움말을 확일할 수 있습니다.\n"
    "/info - 사용자의 고유 정보를 확인할 수 있습니다.\n"
    "/add - 수업을 새롭게 추가할 수 있습니다.\n"
    "/delete - 등록된 수업을 삭제할 수 있습니다.\n"
    "/show - 현재 등록된 모든 수업을 확인할 수 있습니다."
)

# When successfully saved in the database
start_message_True=(
    '{}님의 정보가 성공적으로 서버에 등록되었습니다. '
    '{}님의 Chat ID는 {}이며 추후에 Chat ID를 다시 확인하고 싶다면'
    ' /info 명령어를 통해 확인할 수 있습니다.\n'
    '이 봇에 대한 도움말은 /help 명령어를 통해 확인할 수 있습니다.'
)
# When already saved in the database
start_message_False=(
    '{}님의 정보가 이미 서버에 등록되어있습니다. '
    '수업 추가는 /add 명령어를 통해 가능하며 '
    '삭제 및 전체 조회는 /delete 및 /show 명령어로 '
    '안내받을 수 있습니다.\n'
    '이 봇에 대한 도움말은 /help 명령어를 통해 확인할 수 있습니다. '
    '기타 문의 사항은 ldayou@me.com으로 문의 바랍니다.'
)

# When start add user class
addSubject_message=(
    "총 3번의 단계를 거처 출석 체크 알림을 등록할 수 있습니다. "
    "각 단계별로 안내에 따라 반드시 제시한 형식에 맞춰서 문구를 입력해주시기 바랍니다. "
    "도중에 수업을 추가하는 것을 멈추고 싶다면 /cancel 명령어를 통해 "
    "진행을 멈출 수 있습니다. 도중에 진행을 멈출 시 지금까지 입력된 "
    "정보는 저장되지 않습니다.\n\n"
    "불행히도 정보를 잘못 입력했을 경우 수정하는 기능을 제공하지 않습니다. "
    "수정을 원하는 과목은 /delete 명령어로 삭제 후 다시 등록해주시기 바랍니다.\n\n"
    "출석 확인 메시지는 등록된 시간에서 최대 10분 전에 전송됩니다. "
    "(ex. 14시 00분 수업일 경우 13시 50분에 메시지 전송, "
    "09시 53분 수업일 경우 09시 50분에 메시지 전송)\n\n"
    "** 수업 등록은 08:00 ~ 18:50까지의 수업만 등록이 가능합니다.\n"
    "** 같은 수업이지만 요일별로 수업시간이 다를 경우 요일별로 나워서 등록해야 합니다."
)

# 특정 시간 간격으로 스케줄러로부터 호출되는 함수
# Function that is called at a specific time interval from the scheduler.
def sendNotification(bot, mydb):
    '''
    출석체크 확인 메시지를 여기서 보냄
    Sending a confirmation message to user
    :param bot: bot controller
    :param mydb: database controller
    '''

    # Bring current week, hour, minute
    todayWeek = datetime.datetime.today().weekday()
    todayWeek = addF.returnWeekday(todayWeek) # Convert number to String(like 월)
    currentHour = int(datetime.datetime.today().hour)
    currentMin = int(datetime.datetime.today().minute)

    # Create a character in a specific format such as "1500".
    if currentHour < 10:
        currentHour = '0' + str(currentHour)
    else:
        currentHour = str(currentHour)
    if currentMin < 10:
        currentMin = '0' + str(currentMin)
    else:
        currentMin = str(currentMin)
    time = currentHour + currentMin
    time = addF.changeTime(time, 10)

    # Bring the data that 'ChatID' and class name from database.
    # 특정 요일 및 시간에 수업을 등록한 사람들의 명단과 수업명을 데이터베이스로 부터 가져옴
    dbMsg = mydb.selectMsg(todayWeek, time)
    data = mydb.returnCommand(dbMsg)

    if data == 'error':
        bot.send_message(administratorChatID, '전송에러 확인 요망')
    else:
        for d in data:
            cid = d[0] # ChatID
            subject = d[1] # Class Name
            msg = "{} 수업 출석체크하셨나요?".format(subject)
            t = threading.Thread(target=sendMessageProc, args=(bot, mydb, cid, msg))
            t.start()
            #bot.send_message(cid, msg) # Send message to user.

def sendMessageProc(bot, mydb, cid, msg):
    try:
        bot.send_message(cid, msg)
    except telebot.apihelper.ApiException as e:
        error_code = str(e.result)
        if error_code.find("403") != -1: # When user delete and stop bot
            # Delete user from the database
            msg1 = mydb.deleteMsg('memberTbl', "chatID = '{}'".format(cid))
            check = mydb.setCommand(msg1)
            if check == False:
                bot.send_message(administratorChatID, "DB 멤버({}) 삭제 에러".format(cid))
            else:
                msg2 = mydb.deleteMsg('memSubTbl', "chatID = '{}'".format(cid))
                check = mydb.setCommand(msg2)
                if check == False:
                    bot.send_message(administratorChatID, "DB 멤버({}) 수업 삭제 에러".format(cid))





if __name__ == '__main__':
    # Add scheduler into another processor
    scheduler.scheduler('cron', "1", sendNotification, bot, mydb)
    bot.send_message(administratorChatID, '동작중')

# When receive '/start' command
@bot.message_handler(commands=['start'])
def send_start(m):
    ''' Register user chatID in a database  '''
    cid = m.chat.id # Get chat ID
    check = mydb.initMember(cid) # Verify that the user has already been registered and register user chatId in a database.
    name = m.chat.last_name + m.chat.first_name # Get user name
    markup = types.ReplyKeyboardHide() # Keyboard markup

    if check: # Send success message
        msg = start_message_True.format(name, name, cid) + '\n' + help_message
        try:
            bot.send_message(cid, msg, reply_markup=markup)
        except telebot.apihelper.ApiException as e:
            pass
    else: # Send fail message
        msg = start_message_False.format(name)
        try:
            bot.send_message(cid, msg, reply_markup=markup)
        except telebot.apihelper.ApiException as e:
            pass

# When receive '/help' command
@bot.message_handler(commands=['help'])
def send_help(m):
    ''' Send help message '''
    cid = m.chat.id
    markup = types.ReplyKeyboardHide()
    try:
        bot.send_message(cid, help_message, reply_markup=markup)
    except telebot.apihelper.ApiException as e:
        pass

# When receive '/info' command
@bot.message_handler(commands=['info'])
def send_info(m):
    ''' Send user information(name, chatID) '''
    cid = m.chat.id
    name = m.chat.last_name + m.chat.first_name
    markup = types.ReplyKeyboardHide()
    msg = '이름 : {}\nChat ID : {}'.format(name, cid)
    try:
        bot.send_message(cid, msg, reply_markup=markup)
    except telebot.apihelper.ApiException as e:
        pass

# When receive '/add' command
@bot.message_handler(commands=['add'])
def add_class(m):
    ''' Register class in a database '''
    cid = m.chat.id

    # 등록하고자하는 사용자의 chatID로 구성된 KEY가 있는지 확인
    # Verify that the key already exists
    if cid in addSubTemp:
        del addSubTemp[cid]

    # Made empty list
    addSubTemp[cid] = []
    bot.send_message(cid, addSubject_message) # Send information message
    text = (
        '등록하고자 하는 수업의 요일을 입력해주세요.\n'
        'ex. 월화수 or 월 화 수 or 월,화,수 or 월'
    )
    try:
        msg = bot.send_message(cid, text)
        bot.register_next_step_handler(msg, sb1)
    except telebot.apihelper.ApiException as e:
        return

def sb1(m):
    ''' Receive weekday '''
    cid = m.chat.id
    if m.text == '/cancel': # When receive '/cancel' command
        try:
            bot.send_message(cid, '수업 시간 추가를 취소합니다.')
            del addSubTemp[cid]
        except telebot.apihelper.ApiException as e:
            return
    elif (cid in addSubTemp) == False: # If the key does not exist
        try:
            bot.send_message(cid, '에러... 다시 시도해주세요.')
        except telebot.apihelper.ApiException as e:
            pass
    else:
        weekTemp = addSubTemp[cid]
        weekdayList = addF.returnWeek(m.text) # Get weekdays same as "월화수"

        if len(weekdayList) == 0: # Receive the wrong input
            try:
                msg = bot.send_message(cid, '요일을 다시 입력해주세요.\nex. 월화수 or 월 화 수 or 월,화,수 or 월')
                bot.register_next_step_handler(msg, sb1) # Return to the previous step
            except telebot.apihelper.ApiException as e:
                pass
        else:
            weekTemp.append(weekdayList) # Add weekday in the dictionary

            weekday = ", ".join(weekdayList)

            text = (
                "[{}] 무슨 수업인가요?\n"
                "* 최대 10글자까지만 지원"
            ).format(weekday)
            try:
                msg = bot.send_message(m.chat.id, text)
                bot.register_next_step_handler(msg, sb2)
            except telebot.apihelper.ApiException as e:
                pass

def sb2(m):
    ''' Receive class name '''
    cid = m.chat.id

    if m.text == '/cancel':
        try:
            bot.send_message(cid, '수업 시간 추가를 취소합니다.')
            del addSubTemp[cid]
        except telebot.apihelper.ApiException as e:
            return
    elif (cid in addSubTemp) == False:
        try:
            bot.send_message(cid, '에러... 다시 시도해주세요.')
        except telebot.apihelper.ApiException as e:
            return
    else:
        subTemp = addSubTemp[cid]

        if len(m.text) == 0: # When receive empty message
            try:
                msg = bot.send_message(m.chat.id, '과목명이 너무 짧습니다.\n과목명을 다시 입력해주세요.')
                bot.register_next_step_handler(msg, sb2) # Return to the previous step
            except telebot.apihelper.ApiException as e:
                return
        else:
            # Add class name in the dictionary
            subTemp.append(m.text[:10]) # 10글자 제한으로 저장 (Save as 10 character limit)

            subject = addSubTemp[cid][1] # Get class name from dictionary
            text = (
                "{} 과목의 수업 시간을 입력해주세요.(반드시 숫자 4개)\n"
                "ex. 9시 수업일 경우 - 09:00 or 0900 or 09시 00분, "
                "오후 3시 수업일 경우 - 15:00 or 1500 or 15시 00분\n"
                "잘못된 예 - 9, 9:00, 9시, 오후 03시 30분\n"
                "* 08:00 ~ 18:50까지의 수업만 등록이 가능합니다."
            ).format(subject)
            try:
                msg = bot.send_message(m.chat.id, text)
                bot.register_next_step_handler(msg, sb3)
            except telebot.apihelper.ApiException as e:
                pass

def sb3(m):
    ''' Receive class time '''
    cid = m.chat.id

    if m.text == '/cancel':
        try:
            bot.send_message(cid, '수업 시간 추가를 취소합니다.')
            del addSubTemp[cid]
        except telebot.apihelper.ApiException as e:
            return
    elif (cid in addSubTemp) == False:
        try:
            bot.send_message(cid, '에러... 다시 시도해주세요.')
        except telebot.apihelper.ApiException as e:
            return
    else:
        timeTemp = addSubTemp[cid]
        timeName = addF.returnTime(m.text) # Get column name such as "1500" using time

        if timeName == 'error': # Receive wrong input type
            text = (
                "시간을 다시 입력해주세요. (반드시 숫자 4개)\n"
                "ex. 9시 수업일 경우 - 09:00 or 0900 or 09시 00분, "
                "오후 3시 수업일 경우 - 15:00 or 1500 or 15시 00분\n"
                "잘못된 예 - 9, 9:00, 9시, 오후 03시 30분\n"
                "* 08:00 ~ 18:50까지의 수업만 등록이 가능합니다."
            )
            try:
                msg = bot.send_message(m.chat.id, text)
                bot.register_next_step_handler(msg, sb3)
            except telebot.apihelper.ApiException as e:
                pass
        else:
            timeTemp.append(timeName) # Add column name(time) in the dictionary

            try:
                msg = addSubjectToTable(cid) # Register weekday, class name and time in the database
                bot.send_message(m.chat.id, msg)
                del addSubTemp[cid]
            except telebot.apihelper.ApiException as e:
                pass

def addSubjectToTable(cid):
    ''' Register weekday, class name and time in the database '''
    inform = addSubTemp[cid]
    weekday = inform[0]
    subject = inform[1] # Class name
    time = inform[2] # Time form : "1500"

    weekdays = "".join(weekday)

    msg = mydb.updateMemTableMsg('memSubTbl', cid, weekdays, subject, time) # Get INSERT sql command
    check = mydb.setCommand(msg) # Register chatID, weekday, class name and time in the database

    if check: # Do not receive error when using database.
        # Make weekday text such as "월, 수, 금"
        weekdays = ", ".join(weekday)

        returnMsg = ( # Confirm message
            '성공적으로 서버에 저장하였습니다.\n'
            '수업일 : {}\n'
            '수업시간 : {}\n'
            '수업명 : {}\n'
            '알림 예정 시간 : {}\n\n'
            '등록된 수업 확인 /show\n수업 추가 /add, 수업 삭제 /delete'
        ).format(weekdays, addF.setTimeMsg(time), subject, addF.setTimeMsg(addF.changeTime(time, -10)))
        return returnMsg
    else: # Receive error when using database
        returnMsg = (
            '오류로 인하여 '
            '서버에 저장하는데 실패하였습니다. '
            '관리자(ldayou@me.com)에게 문의바랍니다.'
        )
        return returnMsg

# When receive '/show' command
@bot.message_handler(commands=['show'])
def show_class(m):
    ''' Send all class information '''
    cid = m.chat.id
    name = m.chat.last_name + m.chat.first_name

    msg = mydb.selectAllMsg('memSubTbl', cid) # Get SELECT sql command
    data = mydb.returnCommand(msg) # Get all the data for the user

    if data == 'error': # Receive error when using database
        text = (
            '오류로 인하여 수업 조회에 실패하였습니다. '
            '관리자(ldayou@me.com)에게 문의바랍니다.'
        )
        try:
            bot.send_message(cid, text)
        except telebot.apihelper.ApiException as e:
            return
    elif len(data) == 0: # No data
        text = (
            '{name}님의 저장된 수업 정보가 없습니다.'
        )
        try:
            bot.send_message(cid, text.format(name=name))
        except telebot.apihelper.ApiException as e:
            return
    else:
        try:
            msg = addF.returnClassMsg(data)
            msg = "현재 {}님이 등록한 수업입니다.\n\n".format(name) + msg + "\n수업 추가 /add\n수업 삭제 /delete"
            bot.send_message(cid, msg)
        except telebot.apihelper.ApiException as e:
            return

# When receive '/delete' command
@bot.message_handler(commands=['delete'])
def delete_subject(m):
    ''' Delete class '''
    cid = m.chat.id
    name = m.chat.last_name + m.chat.first_name

    msg = mydb.selectAllMsg('memSubTbl', cid)
    data = mydb.returnCommand(msg)

    if data == 'error':
        try:
            text = (
                '오류로 인하여 수업 조회에 실패하였습니다. '
                '관리자(ldayou@me.com)에게 문의바랍니다.'
            )
            bot.send_message(cid, text)
        except telebot.apihelper.ApiException as e:
            return
    elif len(data) == 0:
        try:
            text = (
                '{name}님의 저장된 수업 정보가 없습니다.'
            )
            bot.send_message(cid, text.format(name=name))
        except telebot.apihelper.ApiException as e:
            return
    else:
        subjectList = addF.returnClassMsg(data) # Get button title using receiving data
        subjectList = subjectList.split('\n') # Text split

        if cid in deleteSubTemp:
            del deleteSubTemp[cid]

        deleteSubTemp[cid] = data

        # Made custom keyboard
        markup = types.ReplyKeyboardMarkup(resize_keyboard = True, one_time_keyboard=True, row_width=1)

        for s in subjectList: # Add keyboard buttons
            itembtn = types.KeyboardButton(s)
            markup.row(itembtn)

        # Add 'Delete All' and 'Cancel' button
        itembtnAll = types.KeyboardButton('전체 삭제')
        itembtnCancel = types.KeyboardButton('취소')
        markup.row(itembtnAll)
        markup.row(itembtnCancel)

        try:
            msg = bot.send_message(cid, '삭제할 수업을 선택해주세요.', reply_markup=markup)
            bot.register_next_step_handler(msg, dsb1)
        except telebot.apihelper.ApiException as e:
            return

def dsb1(m):
    cid = m.chat.id
    markup = types.ReplyKeyboardHide()

    if (cid in deleteSubTemp) == False:
        try:
            bot.send_message(cid, '에러... 다시 시도해주세요.', reply_markup=markup)
        except telebot.apihelper.ApiException as e:
            return
    elif m.text == '취소':
        try:
            bot.send_message(cid, '수업 삭제를 취소합니다.', reply_markup=markup)
            del deleteSubTemp[cid]
        except telebot.apihelper.ApiException as e:
            return
    elif m.text == '전체 삭제':
        try:
            dataList = deleteSubTemp[cid]
            for data in dataList:
                deleteSubjectToTable(cid, data) # Remove all the data from the database
            bot.send_message(cid, '성공적으로 삭제하였습니다.\n\n새로운 수업 등록 /add', reply_markup=markup)
            del deleteSubTemp[cid]
        except telebot.apihelper.ApiException as e:
            pass
    elif m.text in addF.returnClassMsg(deleteSubTemp[cid]):
        try:
            index = int(m.text[0])-1
            data = deleteSubTemp[cid][index]
            deleteSubjectToTable(cid, data) # Remove one data from the database
            bot.send_message(cid, '성공적으로 삭제하였습니다.\n\n다른 수업 삭제 /delete\n새로운 수업 등록 /add', reply_markup=markup)
            del deleteSubTemp[cid]
        except telebot.apihelper.ApiException as e:
            pass
    else: # Occur unexpect error
        try:
            bot.send_message(cid, '에러... 다시 시도해주세요.', reply_markup=markup)
            del deleteSubTemp[cid]
        except telebot.apihelper.ApiException as e:
            pass

def deleteSubjectToTable(cid, data):
    ''' Remove data from the database '''
    # Do not use '0' index because '0' index is chatID
    weekday = data[1]
    subject = data[2]
    time = data[3]

    # Remove memSubTbl table
    msg = mydb.deleteMsg('memSubTbl',\
            "chatID = '{}' and weekdays = '{}' and subject = '{}' and time = '{}'".format(cid, weekday, subject, time))
    mydb.setCommand(msg)
    pass

# Receive all message
@bot.message_handler(func=lambda message : True)
def echo_all(m):
    if m.text == '/cancel':
        pass
    elif m.text[0] == '/':
        try:
            bot.send_message(m.chat.id, '{} 명령어가 존재하지 않습니다.\n이 봇의 명령어는 /help 명령어를 통해 확인할 수 있습니다.'.format(m.text))
        except telebot.apihelper.ApiException as e:
            return
    else:
        pass

bot.polling(none_stop=True)


