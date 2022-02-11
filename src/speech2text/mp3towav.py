from pydub import AudioSegment
import getopt, sys, os
from tqdm import tqdm

def to_wav(file_path, output_dir):
    if os.path.exists(output_dir) is False:
        os.mkdir(output_dir)
    fn = file_path.split("\\")[-1][:-4]
    sound = AudioSegment.from_mp3(file_path)
    output = f"{output_dir}\\{fn}.wav" if output_dir else f"{fn}.wav"
    sound.export(output, format="wav")

def main():
    input_dir = None
    output_dir = None
    try:
        opts, args = getopt.getopt(sys.argv[1:], "i:o:")
        for opt, arg in opts:
            if opt == '-i':
                input_dir = arg
            elif opt == '-o':
                output_dir = arg
    except getopt.GetoptError as err:
        print(err)
        quit()

    assert input_dir != None, "-i is required!"
    assert output_dir != None, "-o is required!"

    mp3s = [fp for fp in os.listdir(input_dir) if fp.endswith(".mp3")]
    with tqdm(total=len(mp3s)) as pbar:
        for mp3 in mp3s:
            to_wav(f"{input_dir}\\{mp3}", output_dir)
            pbar.update(1)

if __name__ == "__main__":
    main()