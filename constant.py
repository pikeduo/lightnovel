'''
定义一些常量
'''
import sys


class const:
    class ConstError(TypeError):
        pass

    class ConstCaseError(ConstError):
        pass

    def __setattr__(self, name, value):
        if name in self.__dict__:
            raise self.ConstError("Can't change const.{}".format(name))
        if not name.isupper():
            raise self.ConstCaseError("const name {} is not all uppercase".format(name))
        self.__dict__[name] = value


sys.modules[__name__] = const()

const.TEXT = '<item href="Text/{text}" id="{text}" media-type="application/xhtml+xml"/>'
const.IMAGE = '<item href="Images/{image}" id="{image}" media-type="image/jpeg"/>'
const.FONT = '<item href="Fonts/{font}" id="{font}" media-type="font/woff2"/>'
const.NCX = '<itemref idref="{href}" properties="duokan-page-fitwindow"/>'
const.GUIDE = '<reference href="Text/{href}" title="{title}" type="text"/>'
const.NAVPOINT = '''<navPoint id="navPoint-{i}" playOrder="{i}">
            <navLabel>
                <text>{title}</text>
            </navLabel>
            <content src="Text/{href}"/>
        </navPoint>'''