__author__ = 'kkennedy'

import sys

def main(*args):

    if len(args) == 0:
        args = sys.argv[1:]

    try:
        import controllers.main
        controller = controllers.main.MainApplicationController()

        if args[0] == 'wx':
            import wx
            from wx_views import wx_main

            wx_main.main(controller)

        else:
            from application.a_Main import a_Main
            main_gui = a_Main()
            main_gui.mainloop()

        controller._stop()

    except Exception as e:
        raise
        raise EnvironmentError("Unable to load labtronyx-gui")

if __name__ == '__main__':
    main('wx')