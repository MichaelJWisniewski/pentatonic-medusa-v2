import omni.ext
from .ui.window import GenAIWindow

class Extension(omni.ext.IExt):
    def on_startup(self, ext_id: str):
        self._window = GenAIWindow("Pentatonic Medusa", width=500, height=600)

    def on_shutdown(self):
        self._window.destroy()
        self._window = None
