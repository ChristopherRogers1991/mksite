# mksite

Parse Yaml files and generate HTML.

# Usage

```
python -m mksite.generator /path/to/input /path/to/output
```

The output path must not exist. This will recursively copy everything
from input to output, and then convert any files ending in `.yml` to
HTML files.

![image](https://user-images.githubusercontent.com/8608191/203390384-117fa8d3-5334-4772-8682-c059b6e23e74.png)
