#-*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import os

class AdditionFunc:

    WEEKDAY = ['월', '화', '수', '목', '금', '토', '일']

    def __init__(self):
        pass

    def checkWeek(self, t):
        for w in self.WEEKDAY:
            if w == t:
                return True
        return False

    def returnWeek(self, text):
        returnValue = []
        for t in text:
            if self.checkWeek(t):
                returnValue.append(t)
        return returnValue

    def returnWeekday(self, text):
        return {
            '0' : '월',
            0 : '월',
            '1' : '화',
            1 : '화',
            '2' : '수',
            2 : '수',
            '3' : '목',
            3 : '목',
            '4' : '금',
            4 : '금',
            '5' : '토',
            5 : '토',
            '6' : '일',
            6 : '일'
        }[text]

    def isNumber(self, s):
        try:
            float(s)
            return True
        except ValueError:
            return False

    def returnTime(self, text):
        text = text.replace(' ', '')
        text = text.replace(':', '')
        # 숫자가 아닌 문자가 있는지 확인
        text2 = text
        text = ''
        for t in text2:
            if self.isNumber(t):
                text = text + t
        # 정상적으로 시간을 입력받았는지 확인
        if len(text) == 4:
            hour = int(text[:2])
            if 7 < hour < 19:
                min = int(text[2:])
                if min%10 != 0:
                    min = min + (10 - min%10)

                if min<10:
                    min = '0' + str(min)
                else:
                    min = str(min)

                time = text[:2] + min

                return time
            else: # 시간 범위 체크
                return 'error'
        else: # 길이 체크
            return 'error'

    def returnClassMsg(self, data):
        returnMsg = ''
        count = 1
        for d in data:
            weekday = d[1]
            subject = d[2]
            time = d[3]

            weekdays = ", ".join(weekday)

            time = self.setTimeMsg(time)

            msg = '{}. {}({} {})\n'\
                .format(count, subject, weekdays, time)
            returnMsg += msg
            count += 1
        return returnMsg

    def changeTime(self, time, value):
        '''
        increase or decrease time
        :param time: form => '1300'
        :param value: + or - integer value
        :return: return time. from is same as input type
        '''
        tMin = 60 + 60*int(abs(value)/60)
        tHour = int(tMin/60)

        hour = int(time[:2])
        min = int(time[2:])

        min = min + value + tMin
        hour = hour - tHour + int(min/60)
        min = min%60

        if hour < 10:
            hour = '0' + str(hour)
        else:
            hour = str(hour)

        if min < 10:
            min = '0' + str(min)
        else:
            min = str(min)

        time = hour + min

        return time

    def setTimeMsg(self, time):

        hour = int(time[:2])
        min = int(time[2:])

        msg = "{}시 {}분".format(hour, min)
        return msg





