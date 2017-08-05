![](https://cdn.rawgit.com/rr-/bubblesub/master/docs/logo.svg)

Simple extensible ASS subtitle editor for Linux

## Features

- Python - extend it however you want with ease
- Video preview
- Audio preview (spectrogram)
- Audio and video are synced at all times
- Spectrogram range selection for eases timing
- Spectrogram shows where subs start and end
- Slow playback support
- I can sub an entire episode without ever having to touch the mouse
- Mouse users are not excluded and can click their way to all the commands
- Robust plugin API (everything GUI is capable of can be done through the API)
- Simple architecture (Commands ↔ API ↔ GUI)
- Separate control for persistent inline comments (useful for translating)
- Newlines support in the editor
- Seeking is aligned to video frames
- No bloat

**Planned features**

- Documentation
    - Hotkeys
    - Built-in commands
    - Configuration files
    - The API
- Spell checker
- Style editor
- Meta data editor

Screenshot:

![](docs/screen.png)

## Installation

- Install system dependencies
    - [`libmpv`](https://github.com/mpv-player/mpv.git)
    - [`ffms`](https://github.com/FFMS/ffms2)
    - [`fftw`](https://github.com/FFTW/fftw3)
    - `QT5` and `PyQT5` bindings
- Clone the repository: `git clone https://github.com/rr-/bubblesub`
- Enter its directory: `cd bubblesub`
- Install `bubblesub`: `pip install --user .`

## Configuration and plugins

- `~/.config/bubblesub/scripts`: contains user plugins
- `~/.config/bubblesub/`: contains user configuration in JSON (subject to change, **please back it up between upgrades**)
- `~/.cache/bubblesub/`: used to cache time codes and such

#### Example plugin: speech recognition of selected lines

```python
import io
import speech_recognition as sr
from bubblesub.api.cmd import PluginCommand


LANGUAGE = 'ja'


def _work(api, logger, line):
    logger.info('line #{} - analyzing'.format(line.number))
    recognizer = sr.Recognizer()
    try:
        with io.BytesIO() as handle:
            api.audio.save_wav(handle, line.start, line.end)
            handle.seek(0, io.SEEK_SET)
            with sr.AudioFile(handle) as source:
                audio = recognizer.record(source)
        note = recognizer.recognize_google(audio, language=LANGUAGE)
    except sr.UnknownValueError:
        logger.warn('line #{}: not recognized'.format(line.number))
    except sr.RequestError as ex:
        logger.error('line #{}: error ({})'.format(line.number, ex))
    else:
        logger.info('line #{}: OK'.format(line.number))
        if line.note:
            line.note = line.note + r'\N' + note
        else:
            line.note = note


class SpeechRecognitionCommand(PluginCommand):
    name = 'grid/speech-recognition'

    def enabled(self):
        return self.api.subs.has_selection and self.api.audio.has_audio_source

    def run(self):
        for line in self.api.subs.selected_lines:
            _work(self.api, self, line)
```

## Questions

1. Why not aegisub?

    As of August 2017:

    - It's dead
        - Forum is down for two months
        - Bug tracker is down for much longer
        - Pull requests are ignored
    - It has numerous unfixed bugs
        - It often crashes
        - Recent menu wasn't working for at least 2 years
        - Karaoke joining never worked to begin with
    - Its API is very limited and I can't write the plugins I need
    - Its code is complicated making it hard to add features to

2. Windows builds?

    This is a hobby project and wrestling with Windows to have it compile a
    single C dependency library isn't my idea of a well-spent afternoon. It
    should be possible with MSYS2.

## Contributing

1. I want to report a bug.

    Please use GitHub issues.

2. I want a feature.

    Chances are I'm too busy to work on features I don't personally need, so
    pull requests are strongly encouraged.