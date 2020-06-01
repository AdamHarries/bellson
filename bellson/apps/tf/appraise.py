#!/usr/bin/env python3
import argparse
import logging
import gc
import objgraph
import math

from os import path
import sys

import tensorflow as tf
from tensorflow import Graph
from tensorflow import keras
from tensorflow.python.lib.io import file_io
from tensorflow.python.client import device_lib

import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

from ...libbellson.ellington_library import EllingtonLibrary, Track
from ...libbellson.library_iterator import LibraryIterator, TrackIterator
from ...libbellson.model import load_model
from ...libbellson import config

import re
import operator


def evaluate_model(library, modelfile, sample_count, resultd):
    # Get a shorthand name for the model
    model_name = path.basename(modelfile)

    # Create a CSV file based on that name for writing data:
    result_filename = resultd + "/" + model_name + "-appraisal.csv"
    with open(result_filename, "w") as resultf:
        resultf.write(
            "model|expected_bpm|predicted_bpm\n")

        graph1 = tf.Graph()
        with graph1.as_default():
            logging.info(f"Loading model {modelfile}")

            model = load_model(modelfile)

            logging.info("Loaded model")

            for track in library.tracks:
                # Get the known data about the track.
                expected_bpm = track.bpm

                # create a track from the audio_file file path, and load spectrogram data
                track_iterator = TrackIterator.from_track(track)
                logging.info(f"Loaded track {track.trackname}")

                logging.info("Reading samples from track")
                samples = track_iterator.get_uniform_batch(
                    sample_c=sample_count)

                logging.info("Predicting batch")
                results = model.predict_on_batch(samples)

                # Do some checks to support different python/tensorflow version
                if isinstance(results, tf.python.framework.ops.EagerTensor):
                    results = results.numpy().flatten().tolist()
                else:
                    results = results.flatten().tolist()

                for datapoint in results:
                    if datapoint < 1:
                        datapoint = datapoint * 400
                    # Output a CSV line of form model, track, expected_bpm, predicted_bpm
                    resultf.write(
                        f"{model_name}|{expected_bpm}|{datapoint}\n")
                resultf.flush()


def main(cache_dir, ellington_lib, sample_count, resultd, models):
    config.cache_directory = cache_dir

    # check whether or not the models exist before we start testing them
    for modelfile in models:
        logging.info(f"Checking model file {modelfile}")
        if not path.exists(modelfile):
            logging.error(f"Model file {modelfile} does not exist!")
            sys.exit(-1)

    # Load the library
    library = EllingtonLibrary.from_file(ellington_lib)

    for modelfile in models:
        evaluate_model(library, modelfile, sample_count, resultd)


if __name__ == '__main__':
    logging.basicConfig(
        format='%(asctime)s %(levelname)s %(module)s %(lineno)d : %(message)s', level=logging.INFO)

    parser = argparse.ArgumentParser()
    parser.add_argument("--cache-dir", required=True,
                        help='Path to cache directory, for pre-compiled histograms')
    parser.add_argument('--ellington-lib', required=True,
                        help='The ellington library from which to read track names and BPMs')
    parser.add_argument('--sample-count', required=False,
                        help='The number of samples to query for each track', type=int, default=int(100))
    parser.add_argument('--resultd', required=False,
                        help='The directory in which to write CSV files of results', default="data")
    # parser.add_argument('--resultfile', required=False,
    # help='Which file to write the results to', default='results.csv')
    parser.add_argument("--models", required=True, nargs='+',
                        help='Bellson models to evaluate')
    args = parser.parse_args()
    arguments = args.__dict__
    main(**arguments)
