__author__ = 'chassotce'
__author__ = 'chassotce'
from flask import Flask
import os

app = Flask(__name__)
app.config.from_object('config')




import route
