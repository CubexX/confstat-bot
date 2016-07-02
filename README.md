Confstat bot
====
This [bot](http://telegram.me/confstatbot) collects statistics from your chat.

Installation
-------
**Python >=3.5 required!**
```bash
pip3 install -r requirements.txt
```
Usage
-------
Edit config.py:
```python
TOKEN = "your_token"
DATABASE = 'mysql://user:password@localhost/database?charset=utf8mb4'
SITE_URL = 'http://your.site.name'
```
And start bot:
```bash
python main.py
```
License
-------
[MIT License](http://www.opensource.org/licenses/MIT)
