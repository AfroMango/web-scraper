from telethon import TelegramClient, events
from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd
import time

# Replace these with appropriate values
api_id = '21424972'
api_hash = '719028c1e15ccad801e5f400ae556e08'
bot_token = '7104228395:AAFq0xFHycNPOsC2OygmBpkFtWgjnRs47cs'
chat_id = '899389704'

client = TelegramClient('bot', api_id, api_hash).start(bot_token=bot_token)

def scrape_page(driver, data):
    print("Scraping started...")
    prev_height = driver.execute_script("return document.body.scrollHeight;")

    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)
        curr_height = driver.execute_script("return document.body.scrollHeight;")
        if curr_height == prev_height:
            break
        prev_height = curr_height

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    matches = soup.find_all('a')

    match_messages = []
    for match in matches:
        partidoA = match.find('div', class_="team-name ta-r team_left") or match.find('div', class_="team-name ta-r team_left winner")
        equipoA = partidoA.text.strip() if partidoA else "N/A"
        partidoB = match.find('div', class_="team-name ta-l team_right") or match.find('div', class_="team-name ta-l team_right winner")
        equipoB = partidoB.text.strip() if partidoB else "N/A"
        resultado = match.find('div', class_="marker")
        resultados = resultado.text.strip() if resultado else "N/A"
        if resultado == "N/A":
            resultado = match.find('p', class_="match_hour time")
            resultados = resultado.text.strip() if resultado else "N/A"
        jornada = match.find('div', class_="middle-info ta-c")
        jornadas = jornada.text.strip() if jornada else "N/A"
        dondeVer = match.find('div', class_="right-info ta-r")
        dondeVerTodos = dondeVer.text.strip() if dondeVer else "N/A"
        estado = match.find('div', class_="match-status-label")
        estados = estado.text.strip() if estado else "N/A"

        if equipoA != "N/A" and equipoB != "N/A" and resultados != "N/A" and jornadas != "N/A" and dondeVerTodos != "N/A":
            if dondeVerTodos == "":
                dondeVerTodos = "No hay canal disponible"
            if estados == "":
                estados = "No comenzado"
            elif estados == "Fin":
                estados = "Finalizado"
            elif estados == "Apl":
                estados = "Aplazado"
            else:
                estados = "En transcurso"

            data.append({
                "Estado ": estados,
                "Equipo A ": equipoA,
                "Resultado/Hora ": resultados,
                "Equipo B ": equipoB,
                "Jornada ": jornadas,
                "Dónde ver ": dondeVerTodos
            })

            match_message = (f"Estado del partido: {estados} \n"
                             f"Equipos enfrentados: {equipoA} vs. {equipoB} \n"
                             f"Resultado (Local-Visitante)/ Hora: {resultados} \n"
                             f"Jornada: {jornadas} \n"
                             f"Dónde ver: {dondeVerTodos}\n")
            match_messages.append(match_message)
    
    # Combine all match messages into a single message
    all_matches_message = "\n------------------------\n".join(match_messages)
    return all_matches_message

def scrape_matches(url):
    driver = webdriver.Chrome()
    data = []
    try:
        driver.get(url)
        message = scrape_page(driver, data)
    finally:
        driver.quit()

    df = pd.DataFrame(data)
    temp_html_file = "temp_besoccer_todos_los_partidos_de_hoy.html"
    final_html_file = "besoccer_todos_los_partidos_de_hoy.html"
    df.to_html(temp_html_file, index=False)
    excel_file = "besoccer_todos_los_partidos_de_hoy.xlsx"
    df.to_excel(excel_file, index=False)

    with open(temp_html_file, "r", encoding="utf-8") as file:
        html_content = file.read()

    custom_div_html = """
        <div class="otro-div">
            <button id="downloadButton">Descargar tabla en Excel</button>
            <script>
                document.getElementById('downloadButton').addEventListener('click', function() {
                    window.location.href = 'besoccer_todos_los_partidos_de_hoy.xlsx';
                });
            </script>
        </div>
    """
    custom_html = """
    <style>
        body { font-family: Arial, sans-serif; background-color: #f0f0f0; display: block; justify-content: center; align-items: center; height: 100vh; margin: 100px; overflow: auto; }
        .container { background-color: #fff; border-radius: 10px; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1); padding: 40px; max-height: 90vh; overflow: auto; }
        h1 { color: #333; text-align: center; margin-bottom: 20px; }
        table { width: 100%; border-collapse: collapse; margin: 20px 0; }
        table th, table td { border: 1px solid #ddd; padding: 12px; text-align: center; }
        table th { background-color: #007BFF; color: #fff; }
        table tr:nth-child(even) { background-color: #f2f2f2; }
        table tr:hover { background-color: #ddd; }
        button { background-color: #007BFF; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; text-align: center; text-decoration: none; display: inline-block; justify-content: center; align-items: center; font-size: 16px; margin-top: 20px; transition-duration: 0.4s; }
        button:hover { background-color: #0056b3; color: white; }
    </style>
    <div class="container">
        <h1>Reporte de Partidos</h1>
    """

    html_content = f"<!DOCTYPE html>\n<html lang='es'>\n<head>\n<meta charset='UTF-8'>\n<meta name='viewport' content='width=device-width, initial-scale=1.0'>\n<title>Reporte de Partidos</title>\n{custom_html}\n</head>\n<body>\n{html_content}\n</div>\n</body>\n</html>"
    html_content = html_content + custom_div_html

    with open(final_html_file, "w", encoding="utf-8") as file:
        file.write(html_content)
    print("Documents generated correctly.")
    return message

async def main():
    url = "https://es.besoccer.com/"
    message = scrape_matches(url)
    try:
        # Split the message if it exceeds 4096 characters
        max_message_length = 4096
        message_parts = [message[i:i + max_message_length] for i in range(0, len(message), max_message_length)]
        for part in message_parts:
            await client.send_message(chat_id, part)
            time.sleep(1)  # Add a delay to avoid hitting rate limits
        print("Messages sent to Telegram.")
    except Exception as e:
        print(f"An error occurred: {e}")

print("Bot is running...")
with client:
    client.loop.run_until_complete(main())
client.run_until_disconnected()
