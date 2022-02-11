from pydub import AudioSegment
import getopt, sys, os, math
from tqdm import tqdm

def single_split(audio, from_min, to_min, split_filename, output_dir):
    if os.path.exists(output_dir) is False:
        os.mkdir(output_dir)
    t1 = from_min * 60 * 1000
    t2 = to_min * 60 * 1000
    split_audio = audio[t1:t2]
    split_audio.export(f'{output_dir}\\{split_filename}', format="wav")

def multiple_split(audio, min_per_split, filename, output_dir):
    total_mins = math.ceil(audio.duration_seconds / 60)
    for i in tqdm(range(0, total_mins, min_per_split)):
        split_fn = str(i) + '_' + filename
        single_split(audio, i, i+min_per_split, split_fn, output_dir)

def main():
    fp = None
    output_dir = None
    duration = 1
    try:
        opts, args = getopt.getopt(sys.argv[1:], "f:o:d:")
        for opt, arg in opts:
            if opt == '-f':
                fp = arg
            elif opt == '-o':
                output_dir = arg
            elif opt == '-d':
                duration = int(arg)
    except getopt.GetoptError as err:
        print(err)
        quit()

    assert fp != None, "-f is required!"
    assert output_dir != None, "-o is required!"

    fn = fp.split("\\")[-1][:-4]
    audio = AudioSegment.from_wav(fp)
    multiple_split(audio, duration, f"{fn}.wav", output_dir)

if __name__ == "__main__":
    main()