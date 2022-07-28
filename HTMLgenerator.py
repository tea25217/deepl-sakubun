from Common import LANGUAGES


class HTMLgenerator:
    def generateLanguageSelector():
        def makeRow(param):
            code, name = param[0], param[1]
            default = ' selected="selected"' if code == "EN-GB" else ''
            return f'<option value="{code}"{default}>{name}</option>'

        return ''.join(list(map(makeRow, LANGUAGES)))
