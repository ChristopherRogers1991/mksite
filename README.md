# mksite

Parse Yaml files and generate HTML.

I do not have social media, so sharing vacation photos with
my family resulted in rolling my own website. I created this
parser to make it a little easier. I probably could have used
something off-the-shelf (jinja, Wordpress, etc), but this was
more fun/educational. I have little expectation this will be
useful for anyone else, but there's no reason to keep it to
myself.

# Install

Clone the repo, and from the top level directory, run `pip install .`

# Usage

As noted above, I don't expect anyone else to find this particularly
useful, so I haven't bothered to document it, but here's a screenshot
showing the basic YAML syntax and resulting webpage:

![image](https://user-images.githubusercontent.com/8608191/203390384-117fa8d3-5334-4772-8682-c059b6e23e74.png)

Once the YAML has been created, and the source files (images) are in
place, the following can be used to generate the HTML.
```
python -m mksite.generator /path/to/input /path/to/output
```

The output path must not exist. This will recursively copy everything
from input to output, and then convert any files ending in `.yml` to
HTML files.

Here's a gif showing a sample website:

![example gif](https://user-images.githubusercontent.com/8608191/206720769-17ef0979-fd33-4161-b722-2002e4d39bf4.gif)
