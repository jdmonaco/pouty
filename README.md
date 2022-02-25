> **Note: `roto` has not yet been refactored as an independent package. You should have no expectation that it will run or import correctly in its current state.**
>
> **I hope to ameliorate this as soon as I have time; of course, PRs welcome.**

<p>&nbsp;</p>

# roto

The `roto` package is a collection of tools for supporting a wide range of scientific computing approaches. Its functions are organized loosely into topic/domain-based modules that should be largely self-evident from how they are named. This package represents the cumulative state of the tools that I have found necessary (or convenient) to build myself over many years. It may or may not be useful to anyone else, but it does serve as a dependency for several of my other packages including [`spikemaps`](https://github.com/jdmonaco/spikemaps) and [`skaggs`](https://github.com/jdmonaco/skaggs).

## Dependencies

*Note: This section will be updated as the packaging and dependencies are fixed.*

The `roto` package requires a typical scientific python computing environment, which can be set up using Anaconda or similar distributions (see the `requirements.txt`). 

## Todo

- [ ] Fix dependencies for other packages of mine (e.g., remove or add as submodules)
- [ ] Update the `setup.py` to ensure correct installation, etc.
- [ ] Improve function and class APIs to enhance usabililty and convenience
- [ ] Code style and formatting consistency (e.g., `flake8` validation)
