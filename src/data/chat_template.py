import os

class TemplateSingleEmbed:
    def __init__(self) -> None:
        self.fullpath = None
        self.name = None
        self.type = "unknown"
        self.content = None

    def load_text_file(self, name, filepath):
        """load text content file
        
        NOTE
        ----
        MUST be UTF-8
        """
        self.fullpath = os.path.abspath(filepath)
        self.name = name
        self.type = "text"
        with open(self.fullpath, "rt", encoding="utf-8") as f:
            self.content = f.read()

    def set_text_input(self, name, text):
        self.fullpath = None
        self.name = name
        self.type = "input_text"
        self.content = text

    def gether_info(self):
        return {
            "type" : self.type,
            "name" : self.name,
            "fullpath" : self.fullpath,
            "content" : self.content
        }

    def expand_info(self, info_dict):
        self.type = info_dict["type"]
        self.name = info_dict["name"]
        self.fullpath = info_dict["fullpath"]
        self.content = info_dict["content"]

class TemplateOnly:
    def __init__(self) -> None:
        self.fullpath = None
        self.content = ""

    @property
    def filename(self):
        if self.fullpath is None:
            return None
        return os.path.basename(self.fullpath)

    def load(self, filepath):
        self.fullpath = os.path.abspath(filepath)
        with open(self.fullpath, "rt", encoding="utf-8") as f:
            self.content = f.read()

    def gether_info(self):
        return {
            "filename" : self.filename,
            "fullpath" : self.fullpath,
            "content" : self.content
        }

    def expand_info(self, info_dict):
        self.fullpath = info_dict["fullpath"]
        self.content = info_dict["content"]

class InitialValue:
    def __init__(self) -> None:
        self.template = None
        self.embedded = {}

    def set_template(self, filepath):
        self.template = TemplateOnly()
        self.template.load(filepath)

    def set_template_by_text(self, text):
        self.template = TemplateOnly()
        self.template.fullpath = None
        self.template.content = text

    def add_file_embedded(self, name, filepath):
        embed = TemplateSingleEmbed()
        embed.load_text_file(name, filepath)
        self.embedded.append(embed)

    def add_input_text_embedded(self, name, text):
        embed = TemplateSingleEmbed()
        embed.set_text_input(name, text)
        self.embedded[name] = embed

    def gether_info(self):
        whole_embed = {}
        for k, e in self.embedded.items():
            whole_embed[k] = e.gether_info()

        # build data
        return {
            "template" : self.template.gether_info(),
            "embedded" : whole_embed,
            "version" : "chat-data-v0.0.1",
            "system" : "template-v0.0.1",
        }
    
    def expand_info(self, initial_values):
        # TODO : version adaptation in future

        self.template = TemplateOnly()
        self.template.expand_info(initial_values["template"])

        self.embedded = {}
        for k, e in initial_values["embedded"].items():
            embed = TemplateSingleEmbed()
            embed.expand_info(e)
            self.embedded[k] = e
