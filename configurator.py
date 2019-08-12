class Template(object):
    """Configuration template.

    You can instanciate this with any field you wish. Templates have the ability
    to merge data from  another template.
    """

    def __init__(self: "Template", **kwargs) -> None:
        self.fields = list(kwargs.keys())
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    def __eq__(self: "Template", other: object) -> bool:
        if self.fields != getattr(other, "fields", []):
            return False
        for field in self.fields:
            if getattr(self, field) != getattr(other, field):
                return False
        return True

    def merge_from(self: "Template", other: "Template") -> None:
        for field in other.fields:
            field_value = getattr(other, field)
            if field not in self.fields:
                self.fields.append(field)
                setattr(self, field, field_value)
            if callable(field_value):
                setattr(self, field, field_value(getattr(self, field)))
            elif isinstance(field_value, Template) and isinstance(
                getattr(self, field), Template
            ):
                getattr(self, field).merge_from(field_value)
            else:
                setattr(self, field, field_value)


if __name__ == "__main__":
    raise Exception("Configurator is not meant to be run directly.")