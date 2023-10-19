import os
from flask import Flask, render_template, request, redirect, url_for, send_file
from pytube import YouTube
from moviepy.editor import VideoFileClip
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    url = request.form['url']
    format = request.form['format']
    print(f"Format selected: {format}")

    try:
        yt = YouTube(url)
    except Exception as e:
        print(f"Error al procesar la URL: {e}")
        return "Error al procesar la URL. Asegúrate de que la URL sea válida."
    video_stream = yt.streams.get_highest_resolution()
    video_stream.download(output_path="downloads")
    filename = video_stream.default_filename

    # Renombrar el archivo descargado para evitar sobrescribir
    base_filename, file_extension = os.path.splitext(filename)
    new_filename = filename
    counter = 1

    while os.path.exists(os.path.join("downloads", new_filename)):
        new_filename = f"{base_filename} ({counter}){file_extension}"
        counter += 1

    os.rename(os.path.join("downloads", filename), os.path.join("downloads", new_filename))

    if format == 'mp3':
        # Convierte el archivo a MP3 utilizando moviepy
        video_clip = VideoFileClip(os.path.join("downloads", new_filename))
        audio_clip = video_clip.audio
        audio_filename = new_filename.replace(file_extension, '.mp3')
        audio_clip.write_audiofile(os.path.join("downloads", audio_filename))
        audio_clip.close()
        video_clip.close()

        # Elimina el archivo de video original
        os.remove(os.path.join("downloads", new_filename))

        # Descargar el archivo de audio al usuario
        return send_file(f"downloads/{audio_filename}", as_attachment=True)
    else:
        return send_file(f"downloads/{new_filename}", as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)