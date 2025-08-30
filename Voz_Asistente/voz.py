import pyttsx3
import vosk
import sounddevice as sd
import json
import time
import os
import sys

# 📁 Cargar modelo Vosk
modelo_path = os.path.join(os.path.dirname(__file__), "modelo", "vosk-model-es-0.42")
modelo = vosk.Model(modelo_path)

# 🔊 Inicializar motor de voz
voz = pyttsx3.init()

def hablar(texto, pausa=1.2):
    print(f"🗣️ Asistente dice: {texto}")
    voz.say(texto)
    voz.runAndWait()
    time.sleep(pausa)

def escuchar():
    hablar("Te escucho...")
    try:
        with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype='int16', channels=1) as stream:
            rec = vosk.KaldiRecognizer(modelo, 16000)
            while True:
                data = bytes(stream.read(4000)[0])
                if rec.AcceptWaveform(data):
                    resultado = json.loads(rec.Result())
                    texto = resultado.get("text", "")
                    if texto:
                        print(f"🎧 Texto reconocido: {texto}")
                        hablar(f"Dijiste: {texto}")
                        return texto
    except Exception as e:
        print("❌ Error al escuchar:", e)
        hablar("Hubo un error al escuchar.")
        return ""

def procesar_entrada(texto):
    texto = texto.lower()
    if "hora" in texto:
        return time.strftime("Son las %H:%M")
    elif "salir" in texto or "terminar" in texto:
        hablar("Hasta pronto.")
        sys.exit()
    elif "nombre" in texto:
        return "Me llamo Copilot, tu asistente conversacional."
    else:
        return f"No entendí bien: {texto}"

def ciclo_conversacional():
    hablar("Hola, estoy listo para conversar.")
    while True:
        entrada = escuchar()
        if entrada:
            respuesta = procesar_entrada(entrada)
            hablar(respuesta)

if __name__ == "__main__":
    ciclo_conversacional()
