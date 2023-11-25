import subprocess

import uuid
from flask import jsonify, request, Blueprint

from app import s3

router = Blueprint('video', __name__, url_prefix='/video')


@router.route('/webm', methods=['POST'])
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
