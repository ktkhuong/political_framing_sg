# Speech to Text

## State-of-the-Art Techniques
### Spectrum
The Spectrum is the set of frequencies that are combined together to produce a signal. eg. the picture shows the spectrum of a piece of music.

The Spectrum plots all of the frequencies that are present in the signal along with the strength or amplitude of each frequency.

<figure>
    <img src="https://miro.medium.com/max/1040/1*yfJw9Jgf5c-bUQi9vWxaCQ.jpeg" alt="Spectrum showing the frequencies that make up a sound signal" style="width:100%">
    <figcaption align="center">Spectrum showing the frequencies that make up a sound signal (<a href="https://towardsdatascience.com/audio-deep-learning-made-simple-part-1-state-of-the-art-techniques-da1d3dff2504">Source</a>)</figcaption>
</figure>

**Fundamental frequency**: the lowest frequency in a signal

**Harmonic frequency**: a whole number multiple of the fundamental frequency

**Time Domain**: shows Amplitude (y) against Time (x)

**Frequency Domain**: shows Amplitude (y) against Frequency (x) *at a moment in time*

### Spectrogram
A Spectrogram of a signal plots its Spectrum over time and is like a ‘photograph’ of the signal. It plots Time on the x-axis and Frequency on the y-axis.

It uses different colors to indicate the Amplitude or strength of each frequency. The brighter the color the higher the energy of the signal. Each vertical ‘slice’ of the Spectrogram is essentially the Spectrum of the signal at that instant in time and shows how the signal strength is distributed in every frequency found in the signal at that instant.

In the example below, the first picture displays the signal in the Time domain ie. Amplitude vs Time. It gives us a sense of how loud or quiet a clip is at any point in time, but it gives us very little information about which frequencies are present.

### Audio Deep Learning Models

<figure>
    <img src="https://miro.medium.com/max/1400/1*rBUXN2u1Yh-9pxKzUGjmMg.png" alt="Typical pipeline used by audio deep learning models" style="width:100%">
    <figcaption align="center">Typical pipeline used by audio deep learning models (<a href="https://towardsdatascience.com/audio-deep-learning-made-simple-part-1-state-of-the-art-techniques-da1d3dff2504">Source</a>)</figcaption>
</figure>

Most deep learning audio applications use Spectrograms to represent audio:
* Start with raw audio data in the form of a wave file.
* Convert the audio data into its corresponding spectrogram.
* Optionally, use simple audio processing techniques to augment the spectrogram data. (Some augmentation or cleaning can also be done on the raw audio data before the spectrogram conversion)
* Now that we have image data, we can use standard CNN architectures to process them and extract feature maps that are an encoded representation of the spectrogram image.

## Mel Spectrograms
### How do humans hear frequencies?
The way we hear frequencies in sound is known as ‘pitch’. It is a subjective impression of the frequency. So a high-pitched sound has a higher frequency than a low-pitched sound.

Humans do not perceive frequencies linearly. We are more sensitive to differences between lower frequencies than higher frequencies.

### Mel Scale
It is a scale of pitches, such that each unit is judged by listeners to be equal in pitch distance from the next.

<figure>
    <img src="https://miro.medium.com/max/712/1*erUKb2-Z-Wi_u8JWel6cDQ.png" alt="Mel Scale measures human perception of pitch" style="width:100%">
    <figcaption align="center">Mel Scale measures human perception of pitch (<a href="https://towardsdatascience.com/audio-deep-learning-made-simple-part-2-why-mel-spectrograms-perform-better-aad889a93505">Source</a>)</figcaption>
</figure>

### How do humans hear amplitudes?
The human perception of the amplitude of a sound is its loudness. And similar to frequency, we hear loudness logarithmically rather than linearly. We account for this using the Decibel scale.

### Decibel Scale
On this scale, 0 dB is total silence. From there, measurement units increase exponentially. 10 dB is 10 times louder than 0 dB, 20 dB is 100 times louder and 30 dB is 1000 times louder.

### Mel Spectrograms
A Mel Spectrogram makes two important changes relative to a regular Spectrogram that plots Frequency vs Time.
* It uses the Mel Scale instead of Frequency on the y-axis.
* It uses the Decibel Scale instead of Amplitude to indicate colors.

**For deep learning models, we usually use this rather than a simple Spectrogram.**

## Data Preparation and Augmentation
There are a number of hyper-parameters that we can use to tune how the Spectrogram is generated. For that, we need to understand a few concepts about how Spectrograms are constructed.

### Fast Fourier Transform (FFT) 
One way to compute Fourier Transforms is by using a technique called DFT (Discrete Fourier Transform). The DFT is very expensive to compute, so in practice, the FFT (Fast Fourier Transform) algorithm is used, which is an efficient way to implement the DFT.

However, the FFT will give you the overall frequency components for the entire time series of the audio signal as a whole. It won’t tell you how those frequency components change over time within the audio signal. You will not be able to see, for example, that the first part of the audio had high frequencies while the second part had low frequencies, and so on.

### Short-time Fourier Transform (STFT)
To get that more granular view and see the frequency variations over time, we use the STFT algorithm (Short-Time Fourier Transform). The STFT is another variant of the Fourier Transform that breaks up the audio signal into smaller sections by using a sliding time window. It takes the FFT on each section and then combines them. It is thus able to capture the variations of the frequency with time.

<figure>
    <img src="https://miro.medium.com/max/1080/1*KoXWCAyudh0AIe0HlLeeNw.png" alt="Mel Scale measures human perception of pitch" style="width:100%">
    <figcaption align="center">STFT slides an overlapping window along the signal and does a Fourier Transform on each segment (<a href="https://miro.medium.com/max/1080/1*KoXWCAyudh0AIe0HlLeeNw.png">Source</a>)</figcaption>
</figure>

### Mel Spectrogram Hyperparameters
#### Frequency Bands
* fmin — minimum frequency
* fmax — maximum frequency to display
* n_mels — number of frequency bands (ie. Mel bins). This is the height of the Spectrogram
#### Time Sections
* n_fft — window length for each time section
* hop_length — number of samples by which to slide the window at each step. Hence, the width of the Spectrogram is = Total number of samples / hop_length

### MFCC (for Human Speech)
For problems dealing with human speech, like Automatic Speech Recognition,  MFCC (Mel Frequency Cepstral Coefficients) sometimes works better.

The MFCC extracts a much smaller set of features from the audio that are the most relevant in capturing the essential quality of the sound.

### Data Augmentation
#### Spectrogram Augmentation
A method known as `SpecAugment` where we block out sections of the spectrogram. There are two flavors:
* Frequency mask — randomly mask out a range of consecutive frequencies by adding horizontal bars on the spectrogram.
* Time mask — similar to frequency masks, except that we randomly block out ranges of time from the spectrogram by using vertical bars.

#### Raw Audio Augmentation
**Time Shift** — shift audio to the left or the right by a random amount.

**Pitch Shift** — randomly modify the frequency of parts of the sound.

**Time Stretch** — randomly slow down or speed up the sound.

**Add Noise** — add some random values to the sound.

