import argparse
import random
import numpy as np
import simpleaudio as sa
import csv
import matplotlib.pyplot as plt
import time
import os
import uuid
import pandas as pd

MAX_FREQUENCY=15000
MIN_FREQUENCY=50

def sine_tone(frequency, duration, volume=0.2, sample_rate=44100):
    data = (32767*volume*np.sin(2*np.pi*np.linspace(0, np.round(duration*frequency), sample_rate*duration))).astype(np.int16)
    return sa.play_buffer(data, 1, 2, sample_rate)

def random_frequency():
    return np.exp(random.uniform(np.log(MIN_FREQUENCY), np.log(MAX_FREQUENCY)))

def test(savefile):
    loop = True
    testid = uuid.uuid4()
    if savefile and not os.path.isfile(savefile):
        with open(savefile, 'w') as sf:
            writer = csv.writer(sf)
            writer.writerow(["time", "frequency", "estimate", "testid"])
    while loop:
        f = random_frequency()
        s = sine_tone(f, 1)
        print("Estimated frequency:", end=' ')
        i = input()
        try:
            ans = float(i)
            if savefile:
                try:
                    with open(savefile, 'a') as sf:
                        writer = csv.writer(sf)
                        writer.writerow([int(time.time()), f, ans, str(testid)])
                except:
                    print(f"Failed to save result to save file {savefile}")
        except ValueError:
            print("Not a valid number")
        print(f"Frequency was {f}")
        print("Continue? (Y/n)", end=' ')
        if input().lower() in ['n', 'no']:
            loop = False
        s.wait_done()

def learn():
    loop = True
    while loop:
        f = random_frequency()
        print(f"Playing frequency {f}")
        sine_tone(f, 1).wait_done()
        print("Continue? (Y/n)", end=' ')
        if input().lower() in ['n', 'no']:
            loop = False

def plot(savefile):
    if savefile:
        try:
            with open(savefile, 'r') as f:
                r = csv.reader(f)
                head = next(r)
                if head != ['time', 'frequency', 'estimate', 'testid']:
                    print("Invalid save file format")
                else:
                    times = []
                    freqs = []
                    ests = []
                    testids = []
                    for row in r:
                        times.append(int(row[0]))
                        freqs.append(float(row[1]))
                        ests.append(float(row[2]))
                        testids.append(row[3])
                    freqs = np.array(freqs)
                    ests = np.array(ests)
                    errs = np.abs(np.divide(freqs-ests, freqs))
                    moving_av_errs = np.exp(pd.Series(np.log(errs)).rolling(10).mean())
                    print(moving_av_errs)
                    ax = plt.subplot(121)
                    ax.scatter(range(1,len(errs)+1), 100*errs, c=np.log(freqs))
                    ax.plot(range(1,len(errs)+1), 100*moving_av_errs, c='0.50', zorder=-1)
                    ax.set_xlabel("Attempt")
                    ax.set_ylabel("Percentage error")
                    ax = plt.subplot(122)
                    ax.set_xscale("log")
                    ax.set_yscale("log")
                    ax.plot([MIN_FREQUENCY, MAX_FREQUENCY], [MIN_FREQUENCY, MAX_FREQUENCY], ls='--', c='0.50', zorder=-1)
                    ax.scatter(freqs, ests, c=range(len(freqs)))
                    ax.set_xlabel("Frequency")
                    ax.set_ylabel("Estimate")
                    plt.show()
        except FileNotFoundError:
            print(f"Save file {savefile} not found")
        except ValueError:
            print(f"Error parsing save file {savefile}")
    else:
        print("Please specify a save file with `--save`")

def main():
    parser = argparse.ArgumentParser(description='Learn to hear in frequencies.',
                                     formatter_class=argparse.RawDescriptionHelpFormatter,
#                                     usage='''hertz [-h] [-s <savefile>] <command>
#
#optional arguments:
#  -h, --help     show this help message and exit
#  -s <savefile>, --save <savefile>
#                 file to store test results
                                     epilog='''commands:
  learn                 play sounds and display the frequency
  test                  test your accuracy
  graph                 plot your progress''')
    parser.add_argument('-s', '--save', dest='savefile', help='file to store test results')
    parser.add_argument('command', help='Subcommand to run')

    args = parser.parse_args()
    if args.command == "learn":
        learn()
    elif args.command == "test":
        test(args.savefile)
    elif args.command == "graph":
        plot(args.savefile)
    else:
        parser.print_help()
