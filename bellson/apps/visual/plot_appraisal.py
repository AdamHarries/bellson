#!/usr/bin/env python3
import argparse
import logging
import gc
import objgraph
import math

import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

import re
import operator


def replace(s):
    m = re.search("model-epoch-(\d+)-.*", s)
    epoch = int(m.group(1))
    return epoch


def main(name, plotd, data_files):
    sns.set(color_codes=True)
    sns.set_style(style='white')
    sns.set_palette("deep")

    fig, ax = plt.subplots(figsize=(20, 20))

    frames = []

    for file in data_files:
        logging.info(f"Loading data from file: {file}")
        data = pd.read_csv(file, delimiter="|", header=0)
        data["model"] = data["model"].apply(replace)
        if data["model"][0] <= 100:
            frames.append(data)

    logging.info(f"Concatenating data frames")
    data = pd.concat(frames)

    logging.info(f"Building facet grid")
    g = sns.FacetGrid(data, col="model", hue="library", col_wrap=5)

    logging.info(f"Mapping lineplot")
    g.map(sns.lineplot, "expected_bpm", "predicted_bpm")

    logging.info(f"Plotting expected line")
    for ax in g.axes.flat:
        ax.set_frame_on(False)
        ax.plot((100, 300), (100, 300), c=".2", ls="--")

    plt.savefig(f"{plotd}/{name}")


if __name__ == '__main__':
    logging.basicConfig(
        format='%(asctime)s %(levelname)s %(module)s %(lineno)d : %(message)s', level=logging.INFO)

    parser = argparse.ArgumentParser()
    parser.add_argument("--name", required=False, default="model_fits.png",
                        help="Name of the file to plot to. Stored in plotd.")

    parser.add_argument('--plotd', required=False, default="plots",
                        help='A directory in which to store generated plots.')

    parser.add_argument("--data-files", required=True, nargs='+',
                        help='Files of data to plot of the form "model|expected|predicted"')
    args = parser.parse_args()
    arguments = args.__dict__
    main(**arguments)
