import os


class AppIndexer:

    @staticmethod
    def build_index():

        app_index = {}

        start_menu_paths = [
            os.path.expandvars(r"%APPDATA%\Microsoft\Windows\Start Menu\Programs"),
            r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs"
        ]

        for base in start_menu_paths:

            if not os.path.exists(base):
                continue

            for root, dirs, files in os.walk(base):

                for file in files:

                    if file.endswith(".lnk"):

                        name = file.replace(".lnk", "").lower()
                        path = os.path.join(root, file)

                        app_index[name] = path

        return app_index