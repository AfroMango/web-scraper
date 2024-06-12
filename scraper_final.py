from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd
import time

def scrape_page(driver, data): # Crea una función que será la encargada de extraer los datos.
    prev_height = driver.execute_script("return document.body.scrollHeight;") # Almacena el valor del largo de la página al inicio.

    while True:
    # Bucle hasta que el valor del largo de la página no se modifique.
        # Hace scroll hasta el final de la página.
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)  # Espera un segundo antes de seguir bajando.

        # Captura el largo actual de la página.
        curr_height = driver.execute_script("return document.body.scrollHeight;")

        # Compara el largo actual con el largo previo. Si ambos valores son iguales, sale del bucle y pasa al siguiente paso. Si no, continúa bajando.
        if curr_height == prev_height:
            break
    
        # Actualiza el valor del largo de la página.
        prev_height = curr_height
    soup = BeautifulSoup(driver.page_source, 'html.parser') # Crea un objeto de BeautifulSoup de la página especificada.
    matches = soup.find_all('a') # Indico a beautifulsoup las etiquetas que quiero que indexe.
    
    for match in matches:
        # Puesto que puede haber muchas etiquetas 'a' en la web, indico que solo quiero que encuentre aquellas cuya clase sea un nombre en específico. Para ello, analizo la estructura del html. (Ver el documento adjunto donde explico el funcionamiento del programa).
        partidoA = match.find('div', class_="team-name ta-r team_left") or match.find('div', class_="team-name ta-r team_left winner")
        equipoA = partidoA.text.strip() if partidoA else "N/A" # Obtengo el texto que hay dentro de esta etiqueta de tipo 'a'.

        # Repito el proceso para todos los tipos de etiquetas que desee. En mi caso: Equipo local, equipo visitante, resultado u hora en caso de que el partido no haya sido disputado aún, jornada, donde verlo y estado del partido (comenzado, finalizado, aplazado, etc.))
        partidoB = match.find('div', class_="team-name ta-l team_right") or match.find('div', class_="team-name ta-l team_right winner")
        equipoB = partidoB.text.strip() if partidoB else "N/A"

        resultado = match.find('div', class_="marker")
        resultados = resultado.text.strip() if resultado else "N/A"
        if resultado == "N/A": # Creao un bucle 'if' para obtener la hora en caso de que el partido no haya comenzado aún.
            resultado = match.find('p', class_="match_hour time")
            resultados = resultado.text.strip() if resultado else "N/A"

        jornada = match.find('div', class_="middle-info ta-c")
        jornadas = jornada.text.strip() if jornada else "N/A"

        dondeVer = match.find('div', class_="right-info ta-r")
        dondeVerTodos = dondeVer.text.strip() if dondeVer else "N/A"

        estado = match.find('div', class_="match-status-label")
        estados = estado.text.strip() if estado else "N/A"

        # Este bucle no es necesario pero aclara las abreviaciones propuestas por la página web y añade claridad al documento excel que genera.
        if equipoA != "N/A" and equipoB != "N/A" and resultados != "N/A" and jornadas != "N/A" and dondeVerTodos != "N/A":
            if dondeVerTodos == "":
                dondeVerTodos = "No hay canal disponible"
            if estados == "":
                estados = "No comenzado"
            elif estados=="Fin":
                estados = "Finalizado"
            elif estados=="Apl":
                estados = "Aplazado"
            else:
                estados = "En transcurso"
            
            # Añado todos los datos a una lista de datos creada anteriormente que, hasta ahora, estaba vacía.
            data.append({
                "Estado ": estados,
                "Equipo A ": equipoA,
                "Resultado/Hora ": resultados,
                "Equipo B ": equipoB,
                "Jornada ": jornadas,
                "Dónde ver ": dondeVerTodos
            })
        
        if equipoA != "N/A" and equipoB != "N/A" and resultados != "N/A" and jornadas != "N/A" and dondeVerTodos != "N/A":
            print(f"Estado del partido: {estados} \r\n Equipos enfrentados: {equipoA} vs. {equipoB} \r\n Resultado (Local-Visitante)/ Hora: {resultados} \r\n Jornada: {jornadas} \r\n Dónde ver: {dondeVerTodos}")
            print("------------------------")

# Defino la URL de donde mi programa extraerá los datos.
url = "https://es.besoccer.com/"

# Esta función imprime los datos en la consola de python. Además, es la que contiene la lista que el programa anterior introduce en el archivo excel.

def scrape_matches(url):
    driver = webdriver.Chrome()
    data = []
    try:
        driver.get(url)
        scrape_page(driver, data)
    finally:
        driver.quit()

    # Gracias a la librería panda, podemos crear una tabla desde la que será mucho mas fácil visualizar los datos en el excel.
    df = pd.DataFrame(data)
    temp_html_file = "temp_besoccer_todos_los_partidos_de_hoy.html"
    final_html_file = "besoccer_todos_los_partidos_de_hoy.html"

    # Genero el archivo HTML sin formato
    df.to_html(temp_html_file, index=False)
    # Genero el archivo excel que el usuario podrá descargar más adelante.
    excel_file = "besoccer_todos_los_partidos_de_hoy.xlsx"
    df.to_excel(excel_file, index=False)

    # Lee el contenido HTML generado
    with open(temp_html_file, "r", encoding="utf-8") as file:
        html_content = file.read()

    # Añado contenido personalizado al HTML que se ha generado de manera automática sin formato

    # Aquí, creo el botón que me servirá para descargar la tabla generada en excel.
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
    # Ahora añado un poco de CSS para hacer que mi página sea más atractiva visualmente.
    custom_html = """
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f0f0f0;
            display: block;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 100px;
            overflow: auto;
        }
        .container {
            background-color: #fff;
            border-radius: 10px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            padding: 40px;
            max-height: 90vh;
            overflow: auto;
        }
        h1 {
            color: #333;
            text-align: center;
            margin-bottom: 20px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }
        table th, table td {
            border: 1px solid #ddd;
            padding: 12px;
            text-align: center;
        }
        table th {
            background-color: #007BFF;
            color: #fff;
        }
        table tr:nth-child(even) {
            background-color: #f2f2f2;
        }
        table tr:hover {
            background-color: #ddd;
        }
        button {
            background-color: #007BFF;
            color: white;
            padding: 10px 20px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            text-align: center;
            text-decoration: none;
            display: inline-block;  
            justify-content: center;
            align-items: center;
            font-size: 16px;
            margin-top: 20px;
            transition-duration: 0.4s;
        }
        button:hover {
            background-color: #0056b3;
            color: white;
        }
    </style>
    <div class="container">
        <h1>Reporte de Partidos</h1>
    """
    
    # Modifico el contenido HTML para incluir el contenido personalizado
    html_content = f"<!DOCTYPE html>\n<html lang='es'>\n<head>\n<meta charset='UTF-8'>\n<meta name='viewport' content='width=device-width, initial-scale=1.0'>\n<title>Reporte de Partidos</title>\n{custom_html}\n</head>\n<body>\n{html_content}\n</div>\n</body>\n</html>"
    html_content = html_content + custom_div_html

    # Guardar el contenido HTML modificado
    with open(final_html_file, "w", encoding="utf-8") as file:
        file.write(html_content)
    print(f"Documentos generados correctamente.")


# Llamo a la función estableciendo como parámetro la URL antes definida.
scrape_matches(url)