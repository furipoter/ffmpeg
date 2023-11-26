import subprocess

import uuid
from flask import jsonify, request, Blueprint

from app import s3

router = Blueprint('video', __name__, url_prefix='/video')


@router.route('mp4/<file_name>', methods=['GET'])
def video_mp4(file_name):
    convert_url = f'tmp/{file_name}'
    s3.download_file(
        Bucket='furiosa-video',
        Key=f'ffmpeg/{file_name}',
        Filename=convert_url,
    )
    ffmpeg_local = f'tmp/{uuid.uuid4()}.mp4'
    ffmpeg_url = "https://furiosa-video.s3.ap-northeast-2.amazonaws.com/ffmpeg/" + file_name

    command=f'ffmpeg -i {convert_url} -vcodec libx264 {ffmpeg_local}'
    # subprocess를 사용하여 명령 실행
    subprocess.run(command, shell=True)
    # s3에 업로드
    s3.upload_file(
        Bucket='furiosa-video',
        Filename=ffmpeg_local,
        Key=f'ffmpeg/{file_name}',
    )
    return jsonify({
        'message': 'success',
        'ffmpeg_url': ffmpeg_url
    }), 200


@router.route('webm', methods=['POST'])
def video_webm():
    video = request.files['video']
    file_name = request.form['file_name']
    webm_url = f"tmp/{file_name}"
    video.save(webm_url)

    tmp_url = f"tmp/{uuid.uuid4()}.mp4"
    subprocess.call(
        [
            'ffmpeg',
            '-i', webm_url,
            '-vf', 'pad=ceil(iw/2)*2:ceil(ih/2)*2',
            '-c:v', 'libx264',
            '-crf', '30',
            '-b:v', '0',
            '-c:a', 'aac',
            '-b:a', '128k',
            tmp_url
        ])

    mp4_path = f"{'.'.join(file_name.split('.')[:-1])}.mp4"
    mp4_url = "https://furiosa-video.s3.ap-northeast-2.amazonaws.com/mp4/" + mp4_path
    s3.upload_file(
        Bucket='furiosa-video',
        Filename=tmp_url,
        Key=f'mp4/{file_name}.mp4',
    )

    return jsonify({
        'message': 'Video converted successfully',
        'mp4_url': mp4_url,
    })
