### `autoesv`

Moves `.pk6` and `.pk7` files to subdirectories based on their ESV. It's meant to be used for organizing eggs for [shiny hatching](https://www.reddit.com/r/SVExchange/).

This is a very basic script that *only* copies files around for convenience in e.g. egg giveaways.

Run `./autoesv.py --help` for usage information. This script has no third party dependencies.

#### Example

My recommendation is that you make a directory called 'in' and put all your `.pk6` and `.pk7` files in there. Then make an empty directory called 'out'. This way you can just run `./autoesv.py ./in ./out --pk-dir` and it will organize all your egg files into the 'out' directory.

Here's an example of how that would work:

<img src="https://raw.githubusercontent.com/msikma/autoesv/master/resources/example_1.png">

The image above shows a terminal running the program. It displays some basic information about the files it processes, and after it's done they are copied into the 'out' directory, organized in subdirectories. The subdirectory name is the ESV that will hatch the egg as a shiny.

<img src="https://raw.githubusercontent.com/msikma/autoesv/master/resources/example_2.png">

As you can see, the eggs have been copied to subdirectories by ESV, and sorted by generation.

#### PK6/PK7 directory

If you supply the `--pk-dir` flag when running the script, two directories `PK6` and `PK7` will sit at the top of the hierarchy (inside the 'out' directory), in case you prefer them separate. This is recommended. If you don't pass this flag, generation 6 and 7 eggs will be placed together in the same ESV subdirectory.

### Links

* [/r/svexchange](https://www.reddit.com/r/SVExchange/) - the best resource for hatching shiny Pokémon using the ESV method

### License

MIT licensed.
