__author__ = 'kkennedy'

import sys

def main(args=None):

    if args is None:
        args = sys.argv[1:]

    try:
        # from application.a_Main import a_Main
        # main_gui = a_Main()
        # main_gui.mainloop()

        import wx

        import controllers.lab
        controller = controllers.lab.LabManagerController()

        import views.wx_main
        view = views.wx_main.MainView(controller)
        view.run()

    except Exception as e:
        raise EnvironmentError("Unable to load labtronyx-gui")