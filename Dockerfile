FROM tensorflow/tensorflow:latest-gpu-py3
run apt-get update 
run apt-get -y install libsndfile1 ffmpeg

run pip3 install \ 
    objgraph \
    librosa \
    matplotlib

workdir bellson 

add do_training.sh do_training.sh

ENTRYPOINT ./do_training.sh