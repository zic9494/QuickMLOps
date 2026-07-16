from jinja2 import Environment, FileSystemLoader, select_autoescape
from typing import Annotated
from pathlib import Path
from annotated_doc import Doc

DEFAULT_TEMPLATE_DIR = ( Path(__file__).parent / "templates" / "home.html" )

class HomePage:

    def __init__(
        self,
        *, 
        template_path: Annotated[str | Path | None, Doc("")] = None,
        title : Annotated[str, Doc("")] = "QuickMLOps"
    ) -> None:
        
        path = Path(template_path or DEFAULT_TEMPLATE_DIR).resolve()
        enviroment = Environment(
            loader = FileSystemLoader(path.parent),
            autoescape = select_autoescape(["html", "xml"])
        )

        self.template = enviroment.get_template(path.name)
        self.title = title

    def get_page(self) -> str:
        context = {
            "title" : self.title
        }
        
        return self.template.render(context)

