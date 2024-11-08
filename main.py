import os
import aiohttp
import asyncio
import ssl
import certifi

class PixabayDownloaderAsync:
    """
    Clase para descargar imágenes de Pixabay usando la API de manera asincrónica con asyncio y aiohttp.

    Atributos:
    ----------
    api_key : str
        Clave de API de Pixabay para autenticar solicitudes.
    directorio_imagenes : str
        Directorio donde se guardarán las imágenes descargadas.

    Métodos:
    --------
    __init__(api_key, directorio_imagenes="imagenes_descargadas")
        Inicializa la clase con la clave de API y el directorio de descarga.
    obtener_urls_imagenes(consulta, cantidad=5)
        Realiza una consulta a la API de Pixabay y devuelve una lista de URLs de imágenes.
    descargar_imagen(session, url, nombre_archivo)
        Descarga una imagen de manera asincrónica desde una URL específica.
    descargar_imagenes_concurrentes(consulta, cantidad=5)
        Realiza la descarga asincrónica de imágenes basadas en la consulta dada.
    """

    def __init__(self, api_key, directorio_imagenes="imagenes_descargadas"):
        """
        Inicializa la clase con la clave de API y el directorio de descarga.

        Parámetros:
        -----------
        api_key : str
            Clave de API de Pixabay para autenticar las solicitudes.
        directorio_imagenes : str, opcional
            Nombre del directorio donde se guardarán las imágenes descargadas. (por defecto "imagenes_descargadas")
        """
        self.api_key = api_key
        self.directorio_imagenes = directorio_imagenes
        os.makedirs(directorio_imagenes, exist_ok=True)

    async def obtener_urls_imagenes(self, consulta, cantidad=5): # 5 es el valor por defecto, si no se especifica en la llamada al constructor
        """
        Realiza una consulta a la API de Pixabay y devuelve una lista de URLs de imágenes.

        Parámetros:
        -----------
        consulta : str
            Palabra clave para buscar imágenes en Pixabay.
        cantidad : int, opcional
            Número de imágenes a obtener. (por defecto 5)

        Retorna:
        --------
        list
            Una lista de URLs de imágenes obtenidas de Pixabay.
        """
        URL_BASE = "https://pixabay.com/api/"
        parametros = {
            'key': self.api_key,
            'q': consulta,
            'image_type': 'photo',
            'per_page': cantidad
        }

        # Crear un contexto SSL personalizado utilizando el archivo de certificados de certifi
        ssl_context = ssl.create_default_context(cafile=certifi.where())
        
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=ssl_context)) as session:
            async with session.get(URL_BASE, params=parametros) as respuesta:
                if respuesta.status == 200:
                    datos = await respuesta.json()
                    urls = [imagen['largeImageURL'] for imagen in datos['hits']]
                    return urls
                else:
                    print(f"Error en la solicitud a la API: {respuesta.status}")
                    return []

    async def descargar_imagen(self, session, url, nombre_archivo):
        """
        Descarga una imagen de manera asincrónica desde una URL específica.

        Parámetros:
        -----------
        session : aiohttp.ClientSession
            Sesión de aiohttp para hacer solicitudes HTTP.
        url : str
            URL de la imagen a descargar.
        nombre_archivo : str
            Nombre del archivo donde se guardará la imagen.
        """
        async with session.get(url) as respuesta:
            if respuesta.status == 200:
                contenido = await respuesta.read()
                ruta = os.path.join(self.directorio_imagenes, nombre_archivo)
                with open(ruta, 'wb') as archivo:
                    archivo.write(contenido)
                print(f"Descarga completada: {nombre_archivo}")
            else:
                print(f"Error descargando {nombre_archivo}: {respuesta.status}")

    async def descargar_imagenes_concurrentes(self, consulta, cantidad=5):
        """
        Realiza la descarga asincrónica de imágenes basadas en la consulta dada.

        Parámetros:
        -----------
        consulta : str
            Palabra clave para buscar imágenes en Pixabay.
        cantidad : int, opcional
            Número de imágenes a descargar. (por defecto 5)
        """
        urls = await self.obtener_urls_imagenes(consulta, cantidad)
        
        if not urls:
            print("No se encontraron imágenes para descargar.")
            return

        # Utilizar el mismo contexto SSL personalizado en las descargas
        ssl_context = ssl.create_default_context(cafile=certifi.where())
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=ssl_context)) as session:
            tareas = [self.descargar_imagen(session, url, f"imagen_{i+1}.jpg") for i, url in enumerate(urls)]
            await asyncio.gather(*tareas)  # Ejecuta todas las tareas de descarga en paralelo

        print("Todas las imágenes han sido descargadas.")

# Ejemplo de uso asincrónico
async def main():
    # Reemplaza 'TU_API_KEY' con tu clave de API de Pixabay
    descargador = PixabayDownloaderAsync(api_key="PON_AQUÍ_TU_API_KEY")
    await descargador.descargar_imagenes_concurrentes(consulta="gatos", cantidad=50)

# Ejecutar el bucle de eventos
asyncio.run(main())
