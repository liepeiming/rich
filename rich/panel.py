from typing import Optional, Tuple, Union

from . import box
from .console import (
    Console,
    ConsoleOptions,
    ConsoleRenderable,
    RenderableType,
    RenderResult,
    Measurement,
)
from .style import Style
from .text import Text
from .segment import Segment


class Panel:
    """A console renderable that draws a border around its contents.
    
    Example::
        >>> console.print(Panel("Hello, World!"))

    Args:
        renderable (RenderableType): A console renderable object.
        box (Box, optional): A Box instance that defines the look of the border.
            Defaults to box.SQUARE.
        expand (bool, optional): If True the panel will stretch to fill the console 
            width, otherwise it will be sized to fit the contents. Defaults to False.
        style (str, optional): The style of the border. Defaults to "none".
        width (Optional[int], optional): Optional width of panel. Defaults to None to auto-detect.
    """

    def __init__(
        self,
        renderable: RenderableType,
        box: box.Box = box.ROUNDED,
        expand: bool = True,
        style: Union[str, Style] = "none",
        width: Optional[int] = None,
    ) -> None:
        self.renderable = renderable
        self.box = box
        self.expand = expand
        self.style = style
        self.width = width

    def __console__(self, console: Console, options: ConsoleOptions) -> RenderResult:
        style = console.get_style(self.style)
        width = (
            options.max_width
            if self.width is None
            else min(self.width, options.max_width)
        )
        child_width = (
            width - 2
            if self.expand
            else Measurement.get(console, self.renderable, width - 2).maximum
        )
        width = child_width + 2
        child_options = options.update(width=child_width)
        lines = console.render_lines(self.renderable, child_options)

        box = self.box
        line_start = Segment(box.mid_left, style)
        line_end = Segment(f"{box.mid_right}\n", style)
        yield Segment(box.get_top([width - 2]), style)
        yield Segment.line()
        for line in lines:
            yield line_start
            yield from line
            yield line_end
        yield Segment(box.get_bottom([width - 2]), style)
        yield Segment.line()

    def __measure__(self, console: "Console", max_width: int) -> Measurement:
        if self.expand:
            return Measurement(max_width, max_width)
        width = Measurement.get(console, self.renderable, max_width - 2).maximum + 2
        return Measurement(width, width)


if __name__ == "__main__":  # pragma: no cover
    from .console import Console

    c = Console()

    from .padding import Padding
    from .box import ROUNDED

    p = Panel(
        Panel(
            Padding(Text.from_markup("[bold magenta]Hello World!"), (1, 8)),
            box=ROUNDED,
            expand=False,
        )
    )

    print(p)
    c.print(p)
