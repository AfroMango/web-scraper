import requests


def bot_send_text(bot_message):
    
    bot_token = '7104228395:AAFq0xFHycNPOsC2OygmBpkFtWgjnRs47cs'
    bot_chatID = '899389704'
    send_text = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + bot_chatID + '&parse_mode=Markdown&text=' + bot_message

    response = requests.get(send_text)

    return response
bot_send_text('Mensaje de prueba')