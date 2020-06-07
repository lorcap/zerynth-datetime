datetime for Zerynth
====================

This module supplies classes for manipulating dates, times, and deltas.
It represents a minimalistic implementation of Python module
[datetime](https://docs.python.org/3/library/datetime.html) for
[Zerynth](https://www.zerynth.com/) platform.

This module relays on the availability of `divmod()` and `round()` as
Zerynth's builtins. Currently, there are two pull requests for them:

* [core-zerynth-stdlib#3](https://github.com/zerynth/core-zerynth-stdlib/pull/3)
* [core-zerynth-stdlib#4](https://github.com/zerynth/core-zerynth-stdlib/pull/4)
