import argparse
import random
import numpy as np
import simpleaudio as sa
import csv
import matplotlib.pyplot as plt
import time
import os

MAX_FREQUENCY=15000
MIN_FREQUENCY=50

def sine_tone(frequency, duration, volume=0.2, sample_rate=44100):
    data = (32767*volume*np.sin(2*np.pi*np.linspace(0, np.round(duration*frequency), sample_rate*duration))).astype(np.int16)
    return sa.play_buffer(data, 1, 2, sample_rate)

def random_frequency():
    return np.exp(random.uniform(np.log(MIN_FREQUENCY), np.log(MAX_FREQUENCY)))

def test(savefile):
    loop = True
    if savefile and not os.path.isfile(savefile):
        with open(savefile, 'w') as sf:
            writer = csv.writer(sf)
            writer.writerow(["time", "frequency", "estimate"])
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
                        writer.writerow([int(time.time()), f, ans])
                except:
                    print(f"Failed to save result to save file {savefile}")
        except ValueError:
            print("Not a valid number")
        print(f"Frequency was {f}")
        print("Continue? (Y/n)", end=' ')
        if input().lower() in ['n', 'no']:
            loop = False
        s.wait_done()

def learn(savefile):
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
                if head != ['time', 'frequency', 'estimate']:
                    print("Invalid save file format")
                else:
                    try:
                        times = []
                        freqs = []
                        ests = []
                        for row in r:
                            times.append(float(row[0]))
                            freqs.append(float(row[1]))
                            ests.append(float(row[2]))
                        freqs = np.array(freqs)
                        ests = np.array(ests)
                        errors = np.abs(np.divide(freqs-ests, freqs))
                        plt.scatter(range(1,len(errors)+1), 100*errors)
                        plt.xlabel("Attempt")
                        plt.ylabel("Percentage error")
                        plt.show()
                    except:
                        print("Error reading save file")
        except FileNotFoundError:
            print(f"Save file {savefile} not found")
    else:
        print("Please specify a save file with `--save`")

def main():
    parser = argparse.ArgumentParser(description='Learn to hear in frequencies.')
    parser.add_argument('-s', '--save', dest='savefile', help='file to store test results')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-l', '--learn', dest='mode', action='store_const',
                        const=learn,
                        help='play sounds and display the frequency')
    group.add_argument('-t', '--test', dest='mode', action='store_const',
                        const=test,
                        help='test your accuracy')
    group.add_argument('-g', '--graph', dest='mode', action='store_const',
                        const=plot,
                        help='plot your progress')

    args = parser.parse_args()
    if args.mode:
        args.mode(args.savefile)
    else:
        parser.print_usage()
