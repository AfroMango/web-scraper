import io
import sys
from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd
import time
import requests
import schedule


import io
import sys

def funcion_con_print():
    print("Hola buenas tardes")

# Crear un objeto StringIO para capturar la salida
captura = io.StringIO()

# Redirigir stdout a nuestro objeto StringIO
sys.stdout = captura

# Llamar a la función que contiene el print
funcion_con_print()

# Restaurar stdout a su valor original
sys.stdout = sys.__stdout__

# Obtener el contenido del StringIO
contenido_del_print = captura.getvalue()

# Ahora la variable contenido_del_print contiene el texto impreso
print(f"El contenido capturado es: {contenido_del_print}")


def bot_send_text(bot_message):
    
    bot_token = '7104228395:AAFq0xFHycNPOsC2OygmBpkFtWgjnRs47cs'
    bot_chatID = '899389704'
    send_text = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + bot_chatID + '&parse_mode=Markdown&text=' + bot_message

    response = requests.get(send_text)

    return response
bot_send_text(contenido_del_print)