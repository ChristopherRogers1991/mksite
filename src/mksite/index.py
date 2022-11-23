from textwrap import dedent
from os.path import join

class Index():
    def __init__(self, prelude, table_of_contents):
        self.prelude = prelude
        self.table_of_contents = table_of_contents

    @classmethod
    def from_file(cls, path):
        from oyaml import load, Loader
        with open(path) as yaml_file:
            data = load(yaml_file.read(), Loader=Loader)
            return cls(**data)

    def generate_html(self, output_dir: str):
        content = dedent(f"""
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <link rel="stylesheet" href="styles.css">
                <script src="scripts.js"></script>
            </head>
            <body>
                <p>
                    {self.prelude}
                </p>
                {self._toc_list()}
            </body>
        """)

        with open(join(output_dir, "index.html"), 'w') as output_file:
            output_file.write(content)

    def _toc_list(self):
        items = "\n    ".join(
            [f"<li><a href={page + '.html'}>{page.replace('_', ' ').title()}</a></li>" for page in self.table_of_contents]
        )
        return f"<ul>\n{items}\n</ul>"
