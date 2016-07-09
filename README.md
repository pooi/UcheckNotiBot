<h1 align=center>UcheckNotiBot</h1>
<p align=center>유체크 알림 봇은 텔레그램 api 및 파이썬을 사용하여<br>출석 체크 확인 메시지를 전송해주는 봇입니다.</p>
<br>

>유체크 알림 봇은 출석 체크 확인 메시지만 전송할 뿐 출석체크를 하는 기능은 없습니다.<br>

유체크 알림 봇 활성화 <a href="https://telegram.me/UcheckNotiBot">telegram.me/UcheckNotiBot</a><br>
Bot available at <a href="https://telegram.me/UcheckNotiBot">telegram.me/UcheckNotiBot</a>

License : MIT License<br>
Contact & Help : ldayou@me.com

## 개발에 참고한 문서
><a href="https://github.com/eternnoir/pyTelegramBotAPI">https://github.com/eternnoir/pyTelegramBotAPI</a><br>
><a href="http://www.hardcopyworld.com/gnuboard5/bbs/board.php?bo_table=lecture_rpi&wr_id=38">http://www.hardcopyworld.com/gnuboard5/bbs/board.php?bo_table=lecture_rpi&wr_id=38</a><br>
><a href="http://www.clien.net/cs2/bbs/board.php?bo_table=lecture&wr_id=324116&page=2">http://www.clien.net/cs2/bbs/board.php?bo_table=lecture&wr_id=324116&page=2</a>

<br>

## Notice
>유체크 알림 봇은 <a href="https://core.telegram.org/bots/api">Telegram cli</a>, <a href="https://github.com/eternnoir/pyTelegramBotAPI">pyTelegramBotAPI</a>, MySQL, apscheduler, 파이썬 2.7을 사용합니다.<br>

* pyTelegramBotAPI<br>
<a href="http://www.hardcopyworld.com/gnuboard5/bbs/board.php?bo_table=lecture_rpi&wr_id=8&page=1">http://www.hardcopyworld.com/gnuboard5/bbs/board.php?bo_table=lecture_rpi&wr_id=8&page=1</a>
```python
import telebot
from telebot import types
```

* MySQLdb<br>
<a href="http://www.hardcopyworld.com/gnuboard5/bbs/board.php?bo_table=lecture_rpi&wr_id=37">http://www.hardcopyworld.com/gnuboard5/bbs/board.php?bo_table=lecture_rpi&wr_id=37</a>
```python
import MySQLdb
```

* apscheduler<br>
<a href="http://www.clien.net/cs2/bbs/board.php?bo_table=lecture&wr_id=324116&page=2">http://www.clien.net/cs2/bbs/board.php?bo_table=lecture&wr_id=324116&page=2</a>
```
$ sudo pip install apscheduler
```
```python
from apscheduler.jobstores.base import JobLookupError
from apscheduler.schedulers.background import BackgroundScheduler
```


<br>
## Usage
>기본적인 설정은 위의 링크대로 진행해주세요.<br>

이 프로젝트를 사용하기 위해서는 <a href="https://telegram.me/botfather">@BotFather</a>(<a href="https://core.telegram.org/bots#3-how-do-i-create-a-bot">안내</a>)를 통해 api key를 획득한 후 사용해주세요.

획득한 api key를 <a href="https://github.com/pooi/UcheckNotiBot/blob/master/ucheckNoti_Bot.py">`ucheckNoti_Bot.py`</a>에 입력해주세요.
```python
API_TOKEN = '<INPUT_YOUR_API_KEY>'
bot = telebot.TeleBot(API_TOKEN)
```

MySQL과 연동을 위해 <a href="github.com/pooi/UcheckNotiBot/blob/master/ucheckNoti_Bot.py">`ucheckNoti_Bot.py`</a>에 Host, ID, Password, DB Name을 입력해주세요.
```python
# Connect database
host = '<INPUT_YOUR_DATABASE_SERVER_HOST>'
db_id = '<INPUT_YOUR_DATABASE_ID>'
db_pw = '<INPUT_YOUR_DATABASE_PASSWORD>'
db_name = '<INPUT_YOUR_DATABASE_NAME>'
db = MySQLdb.connect( host, db_id, db_pw, db_name, charset='utf8') # Encoding utf-8
```

혹시 자신에게 메시지를 전송하고 싶다면 편의를 위해 자신의 Chat ID를 기록해두세요.
```python
administratorChatID = '<INPUT_YOUT_TELEGRAM_CHAT_ID>'
```


<br>
## Bot Commands
유체크 알림 봇은 총 7개의 명령어를 사용합니다.
```
/start    최초 시작시 사용되는 명령어입니다.
/help     도움말을 보여줍니다.
/add      수업을 새롭게 추가할 수 있습니다.
/delete   등록된 수업을 삭제할 수 있습니다.
/show     현재 등록된 모든 수업을 확인할 수 있습니다.
/info     사용자의 고유 정보를 확인할 수 있습니다. (현재는 Chat ID만)
/cancel   특정 작업을 취소합니다.
```



<br>
## How it works
유체크 알림 봇은 사용자가 /add 명령어를 통해 봇과의 대화 형식으로 수업을 추가하면 cron 형식의 스케줄러가 월요일부터 토요일까지 8시 ~ 19시 사이에 10분 간격으로 해당 시간에 수업이 등록된 사용자가 있는지 확인 후 등록된 수업이 있으면 해당 사용자에게 메시지를 전송합니다. 메시지 전송은 수업시간 최대 10분 전에 이루어집니다.<br>


<br>
## Database Modeling
<img src="https://github.com/pooi/UcheckNotiBot/blob/master/screenshot/DBmodeling.jpg" width=60%>

<br>
## Screenshot
### /start<br>
<img src="https://github.com/pooi/UcheckNotiBot/blob/master/screenshot/IMG_1400.PNG" width=45%>
<img src="https://github.com/pooi/UcheckNotiBot/blob/master/screenshot/IMG_1401.PNG" width=45%><br>
<br>
### command<br>
<img src="https://github.com/pooi/UcheckNotiBot/blob/master/screenshot/IMG_1402.PNG" width=45%><br>
<br>
### /add<br>
<img src="https://github.com/pooi/UcheckNotiBot/blob/master/screenshot/IMG_1403.PNG" width=45%>
<img src="https://github.com/pooi/UcheckNotiBot/blob/master/screenshot/IMG_1404.PNG" width=45%><br>
<br>
### /show<br>
<img src="https://github.com/pooi/UcheckNotiBot/blob/master/screenshot/IMG_1405.PNG" width=45%><br>
<br>
### /delete<br>
<img src="https://github.com/pooi/UcheckNotiBot/blob/master/screenshot/IMG_1406.PNG" width=45%>
<img src="https://github.com/pooi/UcheckNotiBot/blob/master/screenshot/IMG_1407.PNG" width=45%><br>
