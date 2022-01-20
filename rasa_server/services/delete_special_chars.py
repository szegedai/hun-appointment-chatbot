from rasa.nlu.components import Component
from typing import Any, Optional, Text, Dict


class DeleteSpecialChars(Component):
    name = "DeleteSpecialChars"
    provides = ["text"]
    defaults = {}
    language_list = None

    def __init__(self, component_config=None):
        super(DeleteSpecialChars, self).__init__(component_config)

    def process(self, message, **kwargs):
        mt = message.get('text', '')
        to_replace = "[$&+,:;=?@#_|<>.^*()%!-]"
        message.set('text', mt.translate(str.maketrans(to_replace, " " * len(to_replace))))

    def persist(self, file_name: Text, model_dir: Text) -> Optional[Dict[Text, Any]]:
        pass

    @classmethod
    def load(
            cls,
            meta: Dict[Text, Any],
            model_dir: Optional[Text] = None,
            model_metadata: Optional["Metadata"] = None,
            cached_component: Optional["Component"] = None,
            **kwargs: Any
    ) -> "Component":
        """Load this component from file."""

        if cached_component:
            return cached_component
        else:
            return cls(meta)
